from functools import wraps
from time import time

from django.core.cache import cache
from django.http import JsonResponse, HttpResponseForbidden


def rate_limit(key_prefix, max_requests=10, window=60, error_msg="Quá nhiều yêu cầu. Vui lòng thử lại sau."):
    def decorator(view):
        @wraps(view)
        def _wrapped(request, *args, **kwargs):
            ip = request.META.get("REMOTE_ADDR") or "unknown"
            cache_key = f"rl:{key_prefix}:{ip}"
            now = time()
            hits = cache.get(cache_key, [])
            hits = [t for t in hits if t > now - window]
            if len(hits) >= max_requests:
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return JsonResponse({"error": error_msg}, status=429)
                return HttpResponseForbidden(error_msg)
            hits.append(now)
            cache.set(cache_key, hits, timeout=window)
            return view(request, *args, **kwargs)
        return _wrapped
    return decorator
