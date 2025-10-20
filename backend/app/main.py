import asyncio

from fastapi import FastAPI, UploadFile, File, HTTPException, Response, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from werkzeug.utils import secure_filename

from .config import settings
from .logging import configure_logging
from .models import FileListResponse, FileMeta, UploadResponse
from .storage import IFileStore, make_store

configure_logging()

app = FastAPI(title="File Upload API", version=settings.API_VERSION)
store: IFileStore = make_store(settings.FILE_BACKEND)
api_router = APIRouter(prefix=settings.API_PREFIX)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@api_router.get("/health")
async def health():
    """
    Health check endpoint.
    :return: JSON object with {"status": "ok"}.
    """
    return {"status": "ok"}

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
async def upload_file(response: Response, file: UploadFile = File(...)):
    """
    Handle file upload and save it into the in-memory store.
    :param response: Response object for version header injection.
    :param file: Incoming file from multipart form.
    :return: UploadResponse containing saved file metadata.
    """
    api_version_header(response)
    safe_name = secure_filename(file.filename or "unnamed")
    data = await _read_stream_with_timeout(file, settings.MAX_UPLOAD_SIZE_BYTES, settings.REQUEST_TIMEOUT_SEC)
    saved = await store.save(safe_name, file.content_type or "application/octet-stream", data)
    meta = FileMeta(name=saved.name, size=saved.size, content_type=saved.content_type, uploaded_at=saved.uploaded_at)
    return UploadResponse(file=meta)
app.include_router(api_router)
