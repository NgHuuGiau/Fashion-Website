import logging

from django.http import Http404
from django.shortcuts import render

from .pages import META_FALLBACK, PAGES

logger = logging.getLogger(__name__)


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
