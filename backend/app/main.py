import asyncio, logging
import os
import secrets

from fastapi import FastAPI, UploadFile, File, HTTPException, Response, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from werkzeug.utils import secure_filename
from starlette.responses import JSONResponse

from .config import settings
from .logging import configure_logging
from .metrics import metrics
from .models import UploadResponse, FileListResponse, FileMeta
from .storage import make_store, IFileStore
from .middlewares import RequestContextMiddleware
from .exceptions import json_exception_handler

configure_logging()
logger = logging.getLogger("app")
dedupe_lock = asyncio.Lock()
app = FastAPI(title="File Upload API", version=settings.API_VERSION)
store: IFileStore = make_store(settings.FILE_BACKEND)
api_router = APIRouter(prefix=settings.API_PREFIX)
upload_semaphore = asyncio.Semaphore(settings.CONCURRENT_UPLOAD_LIMIT)

app.add_exception_handler(Exception, json_exception_handler)
app.add_middleware(RequestContextMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def in_flight_mw(request: Request, call_next):
    """Track requests_in_progress metric."""
    await metrics.inc_in_progress()
    try:
        return await call_next(request)
    finally:
        await metrics.dec_in_progress()
@app.get("/")
async def root():
    """Root liveness endpoint."""
    return {"ok": True, "message": "File Upload API", "version": settings.API_VERSION}

@api_router.get("/health")
async def health():
    """Health and uptime check."""
    return {"status": "ok", "uptime_s": metrics.uptime_s()}

async def _read_stream_with_timeout(up: UploadFile, max_bytes: int, timeout: int) -> bytes:
    """
    Read an uploaded file asynchronously with timeout and maximum size limit.
    :param up: UploadFile stream from FastAPI.
    :param max_bytes: Maximum allowed file size in bytes.
    :param timeout: Maximum read duration in seconds.
    :return: File content as bytes.
    :raises HTTPException: 413 if too large, 408 if timed out.
    """
    buf = bytearray()
    async def _read_all():
        chunk = await up.read(64 * 1024)
        while chunk:
            buf.extend(chunk)
            if len(buf) > max_bytes:
                raise HTTPException(status_code=413, detail="file too large")
            chunk = await up.read(64 * 1024)
    try:
        await asyncio.wait_for(_read_all(), timeout=timeout)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="upload timeout")
    return bytes(buf)

def api_version_header(resp: Response):
    """
    Inject X-API-Version header into a FastAPI response.
    :param resp: Response object to modify.
    """
    resp.headers["x-api-version"] = settings.API_VERSION

@api_router.get("/metrics")
async def get_metrics():
    """Expose runtime metrics."""
    if not settings.ENABLE_METRICS:
        return JSONResponse({"ok": False, "error": "metrics_disabled"}, status_code=404)
    return {
        "ok": True,
        "uploads_total": metrics.counters.uploads_total,
        "upload_bytes_sum": metrics.counters.upload_bytes_sum,
        "requests_in_progress": metrics.gauges.requests_in_progress,
        "queue_len": metrics.gauges.queue_len,
        "uptime_s": metrics.uptime_s(),
    }

@api_router.get("/files", response_model=FileListResponse)
async def list_files(response: Response):
    """
    List all uploaded files in memory.
    :param response: FastAPI response for adding headers.
    :return: FileListResponse model with metadata for all files.
    """
    api_version_header(response)
    files = await store.list()
    return FileListResponse(files=[
        FileMeta(name=f.name, size=f.size, content_type=f.content_type, uploaded_at=f.uploaded_at)
        for f in files
    ])

@api_router.post("/upload", response_model=UploadResponse)
async def upload_file(
    response: Response,
    request: Request,
    file: UploadFile = File(...),
):
    """Upload file with concurrency limits, metrics, safety checks, and deduping."""
    api_version_header(response)

    if settings.FEATURE_REQUIRE_CSRF_HEADER:
        if request.headers.get("x-csrf-token") is None:
            raise HTTPException(status_code=400, detail="missing csrf header")

    # backpressure
    if upload_semaphore.locked() and upload_semaphore._value <= 0:
        await metrics.set_queue_len(settings.CONCURRENT_UPLOAD_LIMIT)
        return JSONResponse(
            status_code=503,
            content={"ok": False, "error": "backpressure"},
            headers={"Retry-After": "1"},
        )

    # sanitize & validate
    raw_name = file.filename or ""
    safe_name = secure_filename(raw_name)
    if not safe_name:
        raise HTTPException(status_code=400, detail="invalid filename")

    name_root, name_ext = os.path.splitext(safe_name)

    async with upload_semaphore:
        # reflect queued capacity
        await metrics.set_queue_len(settings.CONCURRENT_UPLOAD_LIMIT - upload_semaphore._value)

        # read stream with size/time bounds before we grab the short critical section
        data = await _read_stream_with_timeout(
            file, settings.MAX_UPLOAD_SIZE_BYTES, settings.REQUEST_TIMEOUT_SEC
        )
        content_type = file.content_type or "application/octet-stream"

        # short critical section: allocate a unique name then save
        async with dedupe_lock:
            candidate = safe_name
            # probe store for collision; append short random suffix until unique
            while (await store.get(candidate)) is not None:
                suffix = secrets.token_hex(3)  # 6 hex chars
                candidate = f"{name_root}_{suffix}{name_ext}"

            saved = await store.save(candidate, content_type, data)

        await metrics.inc_uploads(len(data))
        meta = FileMeta(
            name=saved.name,
            size=saved.size,
            content_type=saved.content_type,
            uploaded_at=saved.uploaded_at,
        )
        return UploadResponse(file=meta)

@api_router.get("/files/{name}")
async def download_file(name: str):
    """
    Download a previously uploaded file by name.
    - Name is sanitized to match how we saved it.
    - Returns Content-Disposition: attachment.
    """
    safe_name = secure_filename(name)
    f = await store.get(safe_name)
    if f is None:
        raise HTTPException(status_code=404, detail="file not found")
    headers = {
        "Content-Disposition": f'attachment; filename="{safe_name}"'
    }
    return Response(content=f.data, media_type=f.content_type, headers=headers)
app.include_router(api_router)
