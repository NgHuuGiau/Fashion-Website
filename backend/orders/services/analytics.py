"""Admin analytics - cohort / retention / LTV / RFM toi gian.
ponytail: 4 ham pure-query tren Order, khong them model, dung truc tiep tu dashboard.
"""

from datetime import timedelta

from django.db.models import Avg, Count, Max, Min, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone


def _base_qs():
    from orders.models import Order

    return Order.objects.filter(status="delivered")


def monthly_revenue(months=12):
    qs = (
        _base_qs()
        .annotate(m=TruncMonth("created_at"))
        .values("m")
        .annotate(revenue=Sum("total_amount"), orders=Count("id"))
        .order_by("m")
    )
    return list(qs)[-months:]


def cohort_retention(months=6):
    # ponytail: cohort = thang don dau tien, retention = % quay lai thang sau
    from orders.models import Order

    firsts = (
        Order.objects.filter(status="delivered", user__isnull=False)
        .values("user")
        .annotate(first=Min("created_at"))
    )
    out = []
    now = timezone.now()
    for row in list(firsts)[-2000:]:
        out.append(
            {
                "user_id": row["user"],
                "cohort": row["first"].strftime("%Y-%m") if row["first"] else "",
            }
        )
    # gom nhanh, khong query N+1
    cohorts = {}
    for r in out:
        cohorts.setdefault(r["cohort"], 0)
        cohorts[r["cohort"]] += 1
    cutoff = (now - timedelta(days=30 * months)).strftime("%Y-%m")
    return [
        {"cohort": k, "customers": v} for k, v in sorted(cohorts.items()) if k >= cutoff
    ]


def customer_ltv(limit=20):
    qs = (
        _base_qs()
        .values("user", "customer_email")
        .annotate(
            orders=Count("id"), revenue=Sum("total_amount"), last=Max("created_at")
        )
        .order_by("-revenue")[:limit]
    )
    return [
        {
            "user_id": r["user"],
            "email": r["customer_email"],
            "orders": r["orders"],
            "ltv": float(r["revenue"] or 0),
            "last_order": r["last"],
        }
        for r in qs
    ]


def rfm_segments():
    # ponytail: R/F/M don gian tu delivered - du cho dashboard, khoi ML
    now = timezone.now()
    qs = (
        _base_qs()
        .values("user")
        .annotate(
            recency=Max("created_at"),
            frequency=Count("id"),
            monetary=Sum("total_amount"),
        )
    )
    segs = {"champions": 0, "loyal": 0, "at_risk": 0, "new": 0}
    for r in qs[:5000]:
        f = r["frequency"] or 0
        m = float(r["monetary"] or 0)
        days = (now - r["recency"]).days if r["recency"] else 999
        if f >= 5 and m >= 2000000 and days <= 60:
            segs["champions"] += 1
        elif f >= 3 and days <= 90:
            segs["loyal"] += 1
        elif days > 120:
            segs["at_risk"] += 1
        else:
            segs["new"] += 1
    avg_ltv = _base_qs().aggregate(a=Avg("total_amount"))["a"] or 0
    return {"segments": segs, "avg_order_value": float(avg_ltv)}
