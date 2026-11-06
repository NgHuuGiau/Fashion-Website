"""SEO JSON-LD - Product / Breadcrumb / FAQ / Organization.
ponytail: 1 file templatetag, dung o base + product_detail, khong them app.
"""

from django import template
from django.utils.html import json_script
from django.utils.safestring import SafeString

register = template.Library()


def _jsonld_script(data):
    # json_script escapes HTML metacharacters; only the static MIME type changes here.
    rendered = str(json_script(data))
    # The serialized data is already escaped by json_script before this SafeString conversion.
    return SafeString(  # nosec B703
        rendered.replace('type="application/json"', 'type="application/ld+json"', 1)
    )


def _abs(request, path=""):
    try:
        return request.build_absolute_uri(path)
    except Exception:
        return path or "/"


@register.simple_tag(takes_context=True)
def jsonld_organization(context):
    request = context.get("request")
    data = {
        "@context": "https://schema.org",
        "@type": "ClothingStore",
        "name": "HUUGIAU Atelier",
        "url": _abs(request, "/"),
        "sameAs": [
            s
            for s in [
                getattr(
                    __import__("django.conf", fromlist=["settings"]).settings,
                    "SOCIAL_FACEBOOK",
                    "",
                ),
                getattr(
                    __import__("django.conf", fromlist=["settings"]).settings,
                    "SOCIAL_INSTAGRAM",
                    "",
                ),
                getattr(
                    __import__("django.conf", fromlist=["settings"]).settings,
                    "SOCIAL_TIKTOK",
                    "",
                ),
            ]
            if s
        ],
    }
    return _jsonld_script(data)


@register.simple_tag(takes_context=True)
def jsonld_product(context, product):
    request = context.get("request")
    try:
        price = str(
            product.get_effective_price()
            if hasattr(product, "get_effective_price")
            else product.price
        )
    except Exception:
        price = str(getattr(product, "price", "0"))
    reviews = getattr(product, "reviews", None)
    agg = None
    try:
        qs = reviews.filter(is_published=True) if reviews else []
        n = len(qs) if hasattr(qs, "__len__") else 0
        if n:
            avg = sum(getattr(r, "rating", 5) for r in qs) / n
            agg = {
                "@type": "AggregateRating",
                "ratingValue": round(avg, 1),
                "reviewCount": n,
            }
    except Exception:
        pass
    data = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": product.name,
        "url": _abs(
            request,
            product.get_absolute_url() if hasattr(product, "get_absolute_url") else "/",
        ),
        "image": [product.get_image()] if hasattr(product, "get_image") else [],
        "description": (product.description or "")[:500],
        "sku": getattr(product, "sku", "") or str(product.id),
        "brand": {
            "@type": "Brand",
            "name": getattr(product.brand, "name", "HUUGIAU")
            if getattr(product, "brand", None)
            else "HUUGIAU",
        },
        "offers": {
            "@type": "Offer",
            "priceCurrency": "VND",
            "price": price,
            "availability": "https://schema.org/InStock"
            if getattr(product, "available", True)
            else "https://schema.org/OutOfStock",
        },
    }
    if agg:
        data["aggregateRating"] = agg
    return _jsonld_script(data)


@register.simple_tag(takes_context=True)
def jsonld_breadcrumb(context, crumbs):
    items = []
    for i, (name, url) in enumerate(crumbs or [], 1):
        items.append(
            {
                "@type": "ListItem",
                "position": i,
                "name": name,
                "item": _abs(context.get("request"), url),
            }
        )
    data = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items,
    }
    return _jsonld_script(data)


@register.simple_tag
def jsonld_faq(faqs):
    qs = []
    for f in faqs or []:
        q = getattr(f, "question", str(f))
        a = getattr(f, "answer", "")
        qs.append(
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
        )
    data = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": qs}
    return _jsonld_script(data)
