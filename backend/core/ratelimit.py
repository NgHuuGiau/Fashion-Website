from functools import wraps
from time import time

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden


def get_client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff and getattr(settings, "TRUSTED_PROXY", False):
        ip = xff.split(",")[0].strip()
        if ip:
            return ip
    return request.META.get("REMOTE_ADDR") or "unknown"


class RateLimiter:
    def __init__(self, key_prefix, max_requests=10, window=60, error_msg="Quá nhiều yêu cầu. Vui lòng thử lại sau."):
        self.key_prefix = key_prefix
        self.max_requests = max_requests
        self.window = window
        self.error_msg = error_msg

    def _get_cache_key(self, request):
        ip = get_client_ip(request)
        return f"rl:{self.key_prefix}:{ip}"

    def _get_hits(self, cache_key):
        now = time()
        hits = cache.get(cache_key, [])
        hits = [t for t in hits if t > now - self.window]
        return hits, now

    def is_allowed(self, request):
        cache_key = self._get_cache_key(request)
        hits, _ = self._get_hits(cache_key)
        return len(hits) < self.max_requests

    def get_remaining(self, request):
        cache_key = self._get_cache_key(request)
        hits, _ = self._get_hits(cache_key)
        return max(0, self.max_requests - len(hits))

    def _record_hit(self, request):
        cache_key = self._get_cache_key(request)
        hits, now = self._get_hits(cache_key)
        hits.append(now)
        cache.set(cache_key, hits, timeout=self.window)

    def get_retry_after(self, request):
        cache_key = self._get_cache_key(request)
        hits = cache.get(cache_key, [])
        if not hits:
            return self.window
        oldest = min(hits)
        return max(1, int(oldest + self.window - time()))

    def get_response(self, request):
        retry_after = self.get_retry_after(request)
        if request.headers.get("Accept", "").startswith("application/json"):
            resp = JsonResponse({"error": self.error_msg, "retry_after": retry_after}, status=429)
        else:
            resp = HttpResponseForbidden(self.error_msg)
        resp["Retry-After"] = str(retry_after)
        return resp

    def __call__(self, view):
        @wraps(view)
        def _wrapped(request, *args, **kwargs):
            if not self.is_allowed(request):
                return self.get_response(request)
            self._record_hit(request)
            return view(request, *args, **kwargs)
        return _wrapped


def rate_limit(key_prefix, max_requests=10, window=60, error_msg="Quá nhiều yêu cầu. Vui lòng thử lại sau."):
    limiter = RateLimiter(key_prefix, max_requests, window, error_msg)
    return limiter.__call__