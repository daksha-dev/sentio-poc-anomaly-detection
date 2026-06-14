import json
import logging
import sys
import uuid
from typing import Optional


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S.%fZ"),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        for attr in ("request_id", "endpoint", "latency_ms", "events_processed",
                     "alerts_generated", "error"):
            val = getattr(record, attr, None)
            if val is not None:
                log_entry[attr] = val
        return json.dumps(log_entry)


def setup_logging():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_request(logger: logging.Logger, endpoint: str, latency_ms: float,
                events_processed: Optional[int] = None,
                alerts_generated: Optional[int] = None,
                error: Optional[str] = None):
    extra_attrs = {
        "request_id": str(uuid.uuid4())[:8],
        "endpoint": endpoint,
        "latency_ms": round(latency_ms, 2),
    }
    if events_processed is not None:
        extra_attrs["events_processed"] = events_processed
    if alerts_generated is not None:
        extra_attrs["alerts_generated"] = alerts_generated
    if error is not None:
        extra_attrs["error"] = error

    if error:
        logger.warning("Request completed with error", extra=extra_attrs)
    else:
        logger.info("Request completed", extra=extra_attrs)
