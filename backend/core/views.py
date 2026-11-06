import logging
from datetime import datetime

from django.conf import settings
from django.db import connection
from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.core.cache import cache

from .pages import META_FALLBACK, PAGES

logger = logging.getLogger(__name__)


def health_live(request):
    """Liveness probe - app is running."""
    return JsonResponse(
        {"status": "alive", "timestamp": datetime.utcnow().isoformat() + "Z"}
    )


def health_ready(request):
    """Readiness probe - DB, cache, search reachable."""
    checks = {}
    healthy = True

    # Database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        checks["database"] = "ok"
    except Exception:
        logger.exception("Readiness check: database unavailable")
        checks["database"] = "unavailable"
        healthy = False

    # Cache (Redis)
    try:
        cache.set("healthcheck", "ok", 10)
        if cache.get("healthcheck") == "ok":
            checks["cache"] = "ok"
        else:
            checks["cache"] = "unavailable"
            healthy = False
    except Exception:
        logger.exception("Readiness check: cache unavailable")
        checks["cache"] = "unavailable"
        healthy = False

    # Meilisearch
    try:
        import requests

        meili_host = getattr(settings, "MEILISEARCH_HOST", "http://localhost:7700")
        meili_key = getattr(settings, "MEILISEARCH_API_KEY", "")
        headers = {"Authorization": f"Bearer {meili_key}"} if meili_key else {}
        r = requests.get(f"{meili_host.rstrip('/')}/health", headers=headers, timeout=2)
        if r.status_code == 200 and r.json().get("status") == "available":
            checks["meilisearch"] = "ok"
        else:
            checks["meilisearch"] = "unavailable"
            healthy = False
    except Exception:
        logger.exception("Readiness check: meilisearch unavailable")
        checks["meilisearch"] = "unavailable"
        healthy = False

    status = 200 if healthy else 503
    return JsonResponse(
        {
            "status": "ready" if healthy else "not ready",
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
        status=status,
    )


def handler404(request, exception):
    return render(request, "404.html", status=404)


def handler500(request):
    logger.exception("Internal server error")
    return render(request, "500.html", status=500)


def static_page(request, slug):
    page = PAGES.get(slug)
    if not page:
        raise Http404
    return render(
        request,
        "pages/static_page.html",
        {
            "page_title": page["title"],
            "page_body": page["body_html"],
            "meta_description": page.get("meta", META_FALLBACK),
        },
    )


def faq_page(request):
    from products.models import SupportFAQ

    faqs = SupportFAQ.objects.filter(is_active=True).order_by("priority", "id")
    return render(
        request,
        "pages/faq.html",
        {
            "faqs": faqs,
            "meta_description": META_FALLBACK,
        },
    )
