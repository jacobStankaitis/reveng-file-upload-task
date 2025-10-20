import logging
import time
from contextvars import ContextVar
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from .logging import new_id

request_id_var: ContextVar[str] = ContextVar("request_id", default="")
trace_id_var: ContextVar[str] = ContextVar("trace_id", default="")

class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware that injects request_id and trace_id into contextvars,
    logs request completion, and attaches tracing headers.
    """
    async def dispatch(self, request: Request, call_next: Callable):
        rid = request.headers.get("x-request-id") or new_id()
        request_id_var.set(rid)

        traceparent = request.headers.get("traceparent")
        trace_id = traceparent.split("-")[1] if traceparent else new_id()
        trace_id_var.set(trace_id)

        started = time.perf_counter()
        logger = logging.getLogger("app.request")

        try:
            response: Response = await call_next(request)
        except Exception:
            logger.exception(
                "request failed",
                extra={"request_id": rid, "trace_id": trace_id, "path": request.url.path}
            )
            raise
        finally:
            duration_ms = int((time.perf_counter() - started) * 1000)
            extra = {
                "request_id": rid, "trace_id": trace_id,
                "path": request.url.path, "status_code": getattr(response, "status_code", 500),
                "duration_ms": duration_ms
            }
            logger.info("request done", extra=extra)

        response.headers["x-request-id"] = rid
        response.headers["traceparent"] = f"00-{trace_id}-0000000000000000-01"
        return response
