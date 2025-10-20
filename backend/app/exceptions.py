import logging

from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("app.errors")

async def json_exception_handler(request: Request, exc: Exception)-> JSONResponse:
    """
    Handle unhandled exceptions in FastAPI and return a structured JSON error response.
    :param request: Incoming HTTP request that triggered the exception.
    :param exc: The unhandled exception instance.
    :return: JSONResponse with {"ok": False, "error": "internal_error"} and 500 status.
    """
    logger.error("unhandled", exc_info=exc, extra={"path": request.url.path})
    return JSONResponse(status_code=500, content={"ok": False, "error": "internal_error"})
