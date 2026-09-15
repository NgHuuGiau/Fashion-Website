"""Logging utilities for HUUGIAU Fashion Website."""

import logging
import uuid
from threading import local

# Thread-local storage for correlation/request IDs
_thread_local = local()


def get_correlation_id() -> str:
    """Get or generate correlation ID for current request."""
    if not hasattr(_thread_local, "correlation_id"):
        _thread_local.correlation_id = str(uuid.uuid4())
    return _thread_local.correlation_id


def set_correlation_id(correlation_id: str | None = None) -> str:
    """Set correlation ID for current request."""
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())
    _thread_local.correlation_id = correlation_id
    return correlation_id


def get_request_id() -> str:
    """Get or generate request ID for current request."""
    if not hasattr(_thread_local, "request_id"):
        _thread_local.request_id = str(uuid.uuid4())[:8]
    return _thread_local.request_id


def set_request_id(request_id: str | None = None) -> str:
    """Set request ID for current request."""
    if request_id is None:
        request_id = str(uuid.uuid4())[:8]
    _thread_local.request_id = request_id
    return request_id


def clear_context():
    """Clear correlation and request IDs."""
    if hasattr(_thread_local, "correlation_id"):
        del _thread_local.correlation_id
    if hasattr(_thread_local, "request_id"):
        del _thread_local.request_id


class CorrelationIdFilter(logging.Filter):
    """Add correlation_id to log records."""

    def filter(self, record):
        record.correlation_id = get_correlation_id()
        return True


class RequestIdFilter(logging.Filter):
    """Add request_id to log records."""

    def filter(self, record):
        record.request_id = get_request_id()
        return True


class CorrelationIdMiddleware:
    """Middleware to set correlation ID and request ID for each request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Generate or extract correlation ID
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())[:8]

        set_correlation_id(correlation_id)
        set_request_id(request_id)

        # Add to request for downstream use
        request.correlation_id = correlation_id
        request.request_id = request_id

        response = self.get_response(request)

        # Add headers to response
        response["X-Correlation-ID"] = correlation_id
        response["X-Request-ID"] = request_id

        clear_context()
        return response
