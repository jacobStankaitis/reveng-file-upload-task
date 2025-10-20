import json
import logging
import sys
import time
import uuid
from typing import Any, Dict


class JsonFormatter(logging.Formatter):
    """
    Custom JSON log formatter that outputs structured logs with timestamp, level, and message.
    """
    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)

def configure_logging() -> None:
    """
    Configure root logger to use JSON formatting and suppress noisy dependencies.
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers = [handler]
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

def new_id() -> str:
    """
    Generate a random UUID hex string.
    :return: 32-character hexadecimal unique identifier.
    """
    return uuid.uuid4().hex
