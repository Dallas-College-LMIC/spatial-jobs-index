"""Structured logging configuration for the application."""

import logging
import json
import traceback
import uuid
from datetime import datetime, timezone
from contextvars import ContextVar
from typing import Optional, Dict, Any


# Context variable for correlation IDs
correlation_id_var: ContextVar[Optional[str]] = ContextVar(
    "correlation_id", default=None
)


def setup_logging(log_level: str) -> None:
    """Configure structured logging for the application."""
    level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


class StructuredLogger:
    """Logger that outputs structured JSON logs."""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)

    def info(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        log_data = {
            "message": message,
            "service": self.service_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if extra:
            log_data.update(extra)

        # Add correlation ID if available
        correlation_id = correlation_id_var.get()
        if correlation_id:
            log_data["correlation_id"] = correlation_id

        self.logger.info(json.dumps(log_data))

    def error(
        self,
        message: str,
        exc_info: bool = False,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        log_data = {
            "message": message,
            "service": self.service_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if extra:
            log_data.update(extra)

        if exc_info:
            log_data["exception"] = traceback.format_exc()

        self.logger.error(json.dumps(log_data))


class CorrelationIdFilter:
    """Filter to add correlation IDs to log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        correlation_id = correlation_id_var.get() if correlation_id_var else None
        if correlation_id:
            record.correlation_id = correlation_id
        return True


class CorrelationIdMiddleware:
    """Middleware to generate correlation IDs for requests."""

    def __init__(self) -> None:
        pass

    async def dispatch(self, request: Any, call_next: Any) -> Any:
        """Generate and set correlation IDs for requests."""
        # Generate a new correlation ID if not present in headers
        correlation_id = request.headers.get("X-Correlation-ID")
        if not correlation_id:
            correlation_id = uuid.uuid4().hex

        # Set the correlation ID in the context variable
        correlation_id_var.set(correlation_id)

        try:
            # Process the request
            response = await call_next(request)

            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id

            return response
        finally:
            # Clear the context variable after the request
            correlation_id_var.set(None)
