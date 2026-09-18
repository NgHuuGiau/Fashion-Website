from functools import wraps
from ipaddress import ip_address
from time import time
import logging

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse

logger = logging.getLogger(__name__)


def get_client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff and getattr(settings, "TRUSTED_PROXY", False):
        candidate = xff.split(",", 1)[0].strip()
        try:
            return str(ip_address(candidate))
        except ValueError:
            pass
    remote_addr = request.META.get("REMOTE_ADDR", "")
    try:
        return str(ip_address(remote_addr))
    except ValueError:
        return "unknown"


class RateLimiter:
    def __init__(
        self,
        key_prefix,
        max_requests=10,
        window=60,
        error_msg="Quá nhiều yêu cầu. Vui lòng thử lại sau.",
        methods=("POST", "PUT", "PATCH", "DELETE"),
    ):
        self.key_prefix = key_prefix
        self.max_requests = max_requests
        self.window = window
        self.error_msg = error_msg
        self.methods = frozenset(methods)

    def _get_cache_key(self, request):
        ip = get_client_ip(request)
        return f"rl:{self.key_prefix}:{ip}"

    def _get_hits(self, cache_key):
        return int(cache.get(cache_key, 0) or 0), time()

    def is_allowed(self, request):
        cache_key = self._get_cache_key(request)
        hits, _ = self._get_hits(cache_key)
        return hits < self.max_requests

    def get_remaining(self, request):
        cache_key = self._get_cache_key(request)
        hits, _ = self._get_hits(cache_key)
        return max(0, self.max_requests - hits)

    def _record_hit(self, request):
        cache_key = self._get_cache_key(request)
        if not cache.add(cache_key, 1, timeout=self.window):
            try:
                cache.incr(cache_key)
            except ValueError:
                cache.add(cache_key, 1, timeout=self.window)

    def consume(self, request):
        """Atomically count the request; Redis/cache backend owns the counter."""
        cache_key = self._get_cache_key(request)
        if cache.add(cache_key, 1, timeout=self.window):
            return True
        try:
            return cache.incr(cache_key) <= self.max_requests
        except ValueError:
            return cache.add(cache_key, 1, timeout=self.window)

    def get_retry_after(self, request):
        return self.window

    def get_response(self, request):
        retry_after = self.get_retry_after(request)
        if request.headers.get("Accept", "").startswith("application/json"):
            resp: HttpResponse = JsonResponse(
                {"error": self.error_msg, "retry_after": retry_after}, status=429
            )
        else:
            resp = HttpResponse(self.error_msg, status=429)
        resp["Retry-After"] = str(retry_after)
        return resp

    def __call__(self, view):
        @wraps(view)
        def _wrapped(request, *args, **kwargs):
            if request.method not in self.methods:
                return view(request, *args, **kwargs)
            try:
                allowed = self.consume(request)
            except Exception:
                logger.exception("Rate-limit cache unavailable for %s", self.key_prefix)
                if getattr(settings, "DEBUG", False):
                    return view(request, *args, **kwargs)
                return JsonResponse(
                    {"error": "Dịch vụ tạm thời không khả dụng."}, status=503
                )
            if not allowed:
                return self.get_response(request)
            return view(request, *args, **kwargs)

        return _wrapped


def rate_limit(
    key_prefix,
    max_requests=10,
    window=60,
    error_msg="Quá nhiều yêu cầu. Vui lòng thử lại sau.",
    methods=("POST", "PUT", "PATCH", "DELETE"),
):
    limiter = RateLimiter(key_prefix, max_requests, window, error_msg, methods)
    return limiter.__call__
