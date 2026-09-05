import re
from datetime import timedelta

from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, F, Q, Sum
from django.db.models.functions import TruncDate, TruncMonth
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.text import slugify

from products.constants import APPAREL_CATEGORY_SLUGS
from products.models import (
    Category,
    MAX_PRODUCT_GALLERY_IMAGES,
    Product,
    ProductImage,
    ProductVariant,
)
from users.permissions import (
    can_delete_product,
    can_manage_coupons,
    can_manage_inventory,
    can_manage_orders,
    can_manage_products,
    can_manage_users,
    is_admin,
    is_staff_member,
)

from .admin_forms import CouponForm, OrderStatusForm, ProductForm, ProductVariantFormSet
from .cart import safe_int
from .models import Coupon, Order, OrderItem
from .views.cart import apply_order_status_change

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024

DEFAULT_MATRIX_COLORS = [{"name": "Đen", "code": "#111111"}]
DEFAULT_MATRIX_SIZES = ["S", "M", "L", "XL"]


def _validate_uploaded_file(uploaded_file, errors, label):
    if not uploaded_file:
        return
    if uploaded_file.size > MAX_IMAGE_SIZE:
        errors.append(f"{label}: File không được quá 5MB.")
        return
    try:
        from PIL import Image
        import io

        Image.open(io.BytesIO(uploaded_file.read()))
        uploaded_file.seek(0)
    except Exception:
        errors.append(f"{label}: File không phải là ảnh hợp lệ.")


RECENT_ORDER_LIMIT = 200
LOW_STOCK_LIMIT = 10
REVENUE_DAYS_LIMIT = 14


def build_gallery_slot_rows(product=None):
    slots = []
    images_by_sort_order = {}
    if product:
        images_by_sort_order = {
            item.sort_order: item
            for item in product.gallery_images.order_by("sort_order", "id")[
                :MAX_PRODUCT_GALLERY_IMAGES
            ]
        }

    for index in range(MAX_PRODUCT_GALLERY_IMAGES):
        slots.append(
            {
                "slot_index": index,
                "label": f"Slot {index + 1}",
                "image": images_by_sort_order.get(index),
            }
        )
    return slots


def _size_token(size: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", (size or "").strip()) or "size"


def _matrix_post_to_arrays(post_data):
    sizes = [
        size.strip()
        for size in post_data.getlist("matrix_sizes")
        if size and size.strip()
    ]
    color_names = post_data.getlist("matrix_color_name[]")
    color_codes = post_data.getlist("matrix_color_code[]")
    active_indexes = {
        value.strip()
        for value in post_data.getlist("matrix_color_active[]")
        if value.strip()
    }

    row_keys, names, codes, size_list, stocks, active_keys = [], [], [], [], [], []
    for index, color_name in enumerate(color_names):
        color_code = color_codes[index] if index < len(color_codes) else "#111111"
        is_active = str(index) in active_indexes
        for size in sizes:
            token = _size_token(size)
            stock_raw = post_data.get(f"matrix_stock_{index}_{token}", "").strip()
            row_key = f"mat-{index}-{token}"
            row_keys.append(row_key)
            names.append(color_name.strip())
            codes.append(color_code.strip())
            size_list.append(size)
            stocks.append(stock_raw if stock_raw else "0")
            if is_active:
                active_keys.append(row_key)

    return {
        "variant_row_key": row_keys,
        "variant_color_name": names,
        "variant_color_code": codes,
        "variant_size": size_list,
        "variant_stock": stocks,
        "variant_is_active": active_keys,
    }


def build_admin_product_form_data(request=None):
    if request is None:
        return {
            "product_id": "",
            "category_id": "",
            "name": "",
            "price": "",
            "stock": "",
            "description": "",
            "image_url": "",
            "gallery_count": 0,
            "available": True,
            "featured": False,
            "variant_row_key": [
                f"row-{index + 1}" for index in range(len(DEFAULT_MATRIX_SIZES))
            ],
            "variant_color_name": [DEFAULT_MATRIX_COLORS[0]["name"]]
            * len(DEFAULT_MATRIX_SIZES),
            "variant_color_code": [DEFAULT_MATRIX_COLORS[0]["code"]]
            * len(DEFAULT_MATRIX_SIZES),
            "variant_size": list(DEFAULT_MATRIX_SIZES),
            "variant_stock": ["0"] * len(DEFAULT_MATRIX_SIZES),
            "variant_is_active": [
                f"row-{index + 1}" for index in range(len(DEFAULT_MATRIX_SIZES))
            ],
        }

    variant_arrays = (
        _matrix_post_to_arrays(request.POST)
        if "matrix_sizes" in request.POST
        else {
            "variant_row_key": request.POST.getlist("variant_row_key[]"),
            "variant_color_name": request.POST.getlist("variant_color_name[]"),
            "variant_color_code": request.POST.getlist("variant_color_code[]"),
            "variant_size": request.POST.getlist("variant_size[]"),
            "variant_stock": request.POST.getlist("variant_stock[]"),
            "variant_is_active": request.POST.getlist("variant_is_active[]"),
        }
    )

    return {
        "product_id": request.POST.get("product_id", "").strip(),
        "category_id": request.POST.get("category_id", "").strip(),
        "name": request.POST.get("name", "").strip(),
        "price": request.POST.get("price", "").strip(),
        "stock": request.POST.get("stock", "").strip(),
        "description": request.POST.get("description", "").strip(),
        "image_url": request.POST.get("image_url", "").strip(),
        "gallery_count": safe_int(
            request.POST.get("gallery_count", "0"), default=0, minimum=0
        ),
        "remove_gallery_image_ids": request.POST.getlist("remove_gallery_image_ids"),
        "available": request.POST.get("available") == "on",
        "featured": request.POST.get("featured") == "on",
        **variant_arrays,
    }


def build_admin_product_form_from_instance(product):
    variants = list(product.variants.order_by("color_name", "size"))
    if not variants:
        variants = [None]

    form_data = {
        "product_id": str(product.id),
        "category_id": str(product.category_id),
        "name": product.name,
        "price": str(int(product.price)),
        "stock": str(product.stock),
        "description": product.description,
        "image_url": product.image_url,
        "gallery_count": product.gallery_images.count(),
        "remove_gallery_image_ids": [],
        "available": product.available,
        "featured": product.featured,
        "variant_row_key": [],
        "variant_color_name": [],
        "variant_color_code": [],
        "variant_size": [],
        "variant_stock": [],
        "variant_is_active": [],
    }

    for index, variant in enumerate(variants, start=1):
        row_key = f"row-{index}"
        form_data["variant_row_key"].append(row_key)
        form_data["variant_color_name"].append(variant.color_name if variant else "Đen")
        form_data["variant_color_code"].append(
            variant.color_code if variant else "#111111"
        )
        form_data["variant_size"].append(variant.size if variant else "M")
        form_data["variant_stock"].append(str(variant.stock) if variant else "0")
        if variant is None or variant.is_active:
            form_data["variant_is_active"].append(row_key)

    return form_data


def build_variant_rows(form_data):
    variant_rows = []
    max_rows = max(
        len(form_data["variant_row_key"]),
        len(form_data["variant_color_name"]),
        len(form_data["variant_color_code"]),
        len(form_data["variant_size"]),
        len(form_data["variant_stock"]),
        1,
    )
    active_keys = set(form_data["variant_is_active"])
    for index in range(max_rows):
        row_key = (
            form_data["variant_row_key"][index]
            if index < len(form_data["variant_row_key"])
            else f"row-{index + 1}"
        )
        variant_rows.append(
            {
                "row_key": row_key,
                "color_name": form_data["variant_color_name"][index]
                if index < len(form_data["variant_color_name"])
                else "",
                "color_code": form_data["variant_color_code"][index]
                if index < len(form_data["variant_color_code"])
                else "#111111",
                "size": form_data["variant_size"][index]
                if index < len(form_data["variant_size"])
                else "",
                "stock": form_data["variant_stock"][index]
                if index < len(form_data["variant_stock"])
                else "0",
                "is_active": row_key in active_keys,
            }
        )
    return variant_rows


def build_variant_matrix(form_data):
    rows = build_variant_rows(form_data)

    color_rows = []
    color_index_by_key = {}
    size_index_by_key = {}
    sizes = []
    cell_stock = {}

    for row in rows:
        color_name = row["color_name"].strip()
        size = row["size"].strip().upper()
        if not any([color_name, size, row["stock"]]):
            continue
        color_key = color_name.casefold()
        if color_key not in color_index_by_key:
            color_index_by_key[color_key] = len(color_rows)
            color_rows.append(
                {
                    "index": len(color_rows),
                    "name": color_name,
                    "code": row["color_code"].strip() or "#111111",
                    "is_active": row["is_active"],
                }
            )
        if size and size not in size_index_by_key:
            size_index_by_key[size] = len(sizes)
            sizes.append(size)
        if size:
            cell_stock[(color_index_by_key[color_key], size_index_by_key[size])] = str(
                row["stock"]
            )

    for color in color_rows:
        color["stocks"] = [
            {
                "size": size,
                "token": _size_token(size),
                "stock": cell_stock.get((color["index"], index), "0"),
            }
            for index, size in enumerate(sizes)
        ]

    return {"colors": color_rows, "sizes": sizes}


def build_admin_dashboard_context(
    form_data=None,
    form_errors=None,
    editing_product=None,
    order_status=None,
    order_q=None,
    current_user=None,
    inventory_status=None,
    inventory_q=None,
):
    effective_form_data = form_data or build_admin_product_form_data()
    all_orders = Order.objects.all().prefetch_related("items__product")
    orders_qs = all_orders
    if order_status:
        orders_qs = orders_qs.filter(status=order_status)
    if order_q:
        orders_qs = orders_qs.filter(
            Q(id__icontains=order_q)
            | Q(customer_name__icontains=order_q)
            | Q(phone__icontains=order_q)
        )
    orders = orders_qs
    from .views import decorate_order_tracking

    now = timezone.now()
    today = timezone.localdate()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    combined = all_orders.aggregate(
        total=Count("id"),
        pending=Count("id", filter=Q(status="pending")),
        processing=Count("id", filter=Q(status="processing")),
        shipping=Count("id", filter=Q(status="shipping")),
        delivered=Count("id", filter=Q(status="delivered")),
        cancelled=Count("id", filter=Q(status="cancelled")),
        total_revenue=Sum("total_amount", filter=Q(status="delivered")),
        month_revenue=Sum(
            "total_amount", filter=Q(status="delivered", created_at__gte=month_start)
        ),
        today_orders=Count("id", filter=Q(created_at__date=today)),
        today_revenue=Sum(
            "total_amount", filter=Q(status="delivered", created_at__date=today)
        ),
    )
    daily_revenue = (
        all_orders.filter(status="delivered")
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(total=Sum("total_amount"), orders_count=Count("id"))
        .order_by("-day")[:REVENUE_DAYS_LIMIT]
    )

    revenue_by_day = {item["day"]: int(item["total"] or 0) for item in daily_revenue}
    chart_days = [today - timedelta(days=offset) for offset in range(6, -1, -1)]
    previous_days = [today - timedelta(days=offset) for offset in range(13, 6, -1)]
    current_total = sum(revenue_by_day.get(day, 0) for day in chart_days)
    previous_total = sum(revenue_by_day.get(day, 0) for day in previous_days)
    growth_pct = (
        ((current_total - previous_total) / previous_total * 100)
        if previous_total
        else 0
    )
    chart_max = max([revenue_by_day.get(day, 0) for day in chart_days] or [0]) or 1
    weekday_labels = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]
    revenue_chart = [
        {
            "day": day,
            "label": weekday_labels[day.weekday()],
            "date_label": day.strftime("%d/%m"),
            "total": revenue_by_day.get(day, 0),
            "orders_count": next(
                (
                    int(item["orders_count"] or 0)
                    for item in daily_revenue
                    if item["day"] == day
                ),
                0,
            ),
            "height": max(8, int((revenue_by_day.get(day, 0) / chart_max) * 100))
            if revenue_by_day.get(day, 0)
            else 8,
        }
        for day in chart_days
    ]
    if previous_total == 0 and current_total == 0:
        growth_label = "Chưa có doanh thu 7 ngày"
        growth_class = "is-flat"
    elif previous_total == 0:
        growth_label = "Tăng từ nền 0đ"
        growth_class = "is-up"
    elif current_total > previous_total:
        growth_label = f"Tăng {abs(growth_pct):.0f}% so với 7 ngày trước"
        growth_class = "is-up"
    elif current_total < previous_total:
        growth_label = f"Giảm {abs(growth_pct):.0f}% so với 7 ngày trước"
        growth_class = "is-down"
    else:
        growth_label = "Ổn định so với 7 ngày trước"
        growth_class = "is-flat"

    monthly_revenue = []
    month_agg = (
        all_orders.filter(status="delivered")
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(total=Sum("total_amount"), orders_count=Count("id"))
        .order_by("-month")[:12]
    )
    revenue_by_month = {}

    for item in reversed(month_agg):
        if item["month"] is None:
            continue
        revenue_by_month[item["month"].strftime("%Y-%m")] = {
            "revenue": int(item["total"] or 0),
            "orders_count": int(item["orders_count"] or 0),
        }
    month_labels = []
    for offset in range(11, -1, -1):
        cursor = (today.replace(day=1) - timedelta(days=offset * 31)).replace(day=1)
        month_labels.append(cursor)

    for month_date in month_labels:
        key = month_date.strftime("%Y-%m")
        row = revenue_by_month.get(key, {"revenue": 0, "orders_count": 0})
        monthly_revenue.append(
            {
                "key": key,
                "label": f"Tháng {month_date.month}/{month_date.year}",
                "revenue": int(row["revenue"]),
                "orders_count": int(row["orders_count"]),
                "height": 8,
            }
        )
    if monthly_revenue:
        month_max = max((row["revenue"] for row in monthly_revenue), default=0) or 1
        for row in monthly_revenue:
            row["height"] = (
                max(8, int((row["revenue"] / month_max) * 100)) if row["revenue"] else 8
            )

    total_revenue = combined.pop("total_revenue") or 0
    month_revenue = combined.pop("month_revenue") or 0
    today_orders = combined.pop("today_orders") or 0
    today_revenue = combined.pop("today_revenue") or 0
    status_counts = combined
    UserModel = get_user_model()
    today_new_accounts = UserModel.objects.filter(date_joined__date=today).count()

    daily_orders = (
        all_orders.annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(orders_count=Count("id"))
        .order_by("-day")[:REVENUE_DAYS_LIMIT]
    )
    orders_by_day = {
        item["day"]: int(item["orders_count"] or 0) for item in daily_orders
    }
    orders_max = max([orders_by_day.get(day, 0) for day in chart_days] or [0]) or 1
    orders_chart = [
        {
            "day": day,
            "label": weekday_labels[day.weekday()],
            "date_label": day.strftime("%d/%m"),
            "total": orders_by_day.get(day, 0),
            "height": max(8, int((orders_by_day.get(day, 0) / orders_max) * 100))
            if orders_by_day.get(day, 0)
            else 8,
        }
        for day in chart_days
    ]

    top_products = [
        {
            "name": item["product__name"],
            "quantity": int(item["quantity"] or 0),
            "revenue": int(item["revenue"] or 0),
        }
        for item in (
            OrderItem.objects.filter(order__status="delivered")
            .annotate(subtotal=F("quantity") * F("price"))
            .values("product__name")
            .annotate(quantity=Sum("quantity"), revenue=Sum("subtotal"))
            .order_by("-quantity")[:5]
        )
    ]

    category_revenue = [
        {
            "name": item["product__category__name"] or "Chưa phân loại",
            "revenue": int(item["revenue"] or 0),
        }
        for item in (
            OrderItem.objects.filter(order__status="delivered")
            .annotate(subtotal=F("quantity") * F("price"))
            .values("product__category__name")
            .annotate(revenue=Sum("subtotal"))
            .order_by("-revenue")[:6]
        )
    ]
    category_max = max([item["revenue"] for item in category_revenue] or [0]) or 1
    for item in category_revenue:
        item["height"] = (
            max(8, int((item["revenue"] / category_max) * 100))
            if item["revenue"]
            else 8
        )

    top_max = max([item["quantity"] for item in top_products] or [0]) or 1
    for item in top_products:
        item["height"] = (
            max(8, int((item["quantity"] / top_max) * 100)) if item["quantity"] else 8
        )

    status_chart = [
        {
            "key": "pending",
            "label": "Chờ xử lý",
            "total": status_counts["pending"],
        },
        {
            "key": "processing",
            "label": "Đang xử lý",
            "total": status_counts["processing"],
        },
        {
            "key": "shipping",
            "label": "Đang giao",
            "total": status_counts["shipping"],
        },
        {
            "key": "delivered",
            "label": "Hoàn thành",
            "total": status_counts["delivered"],
        },
        {
            "key": "cancelled",
            "label": "Đã hủy",
            "total": status_counts["cancelled"],
        },
    ]
    status_max = max([item["total"] for item in status_chart] or [0]) or 1
    for item in status_chart:
        item["height"] = (
            max(8, int((item["total"] / status_max) * 100)) if item["total"] else 8
        )

    status_color_map = {
        "pending": "#d97706",
        "processing": "#0ea5e9",
        "shipping": "#7c3aed",
        "delivered": "#16a34a",
        "cancelled": "#dc2626",
    }
    status_total = status_counts["total"] or 1
    running_offset = 25.0
    for item in status_chart:
        item["color"] = status_color_map[item["key"]]
        item["pct"] = round((item["total"] / status_total) * 100, 1)
        item["offset"] = running_offset
        running_offset = running_offset - item["pct"]

    inventory_product_qs = Product.objects.select_related("category")
    if inventory_status == "out":
        inventory_product_qs = inventory_product_qs.filter(stock=0)
    elif inventory_status == "low":
        inventory_product_qs = inventory_product_qs.filter(
            available=True, stock__gte=1, stock__lte=LOW_STOCK_LIMIT
        )
    elif inventory_status == "hidden":
        inventory_product_qs = inventory_product_qs.filter(
            available=False, stock__gte=1
        )
    if inventory_q:
        inventory_product_qs = inventory_product_qs.filter(
            Q(name__icontains=inventory_q) | Q(category__name__icontains=inventory_q)
        )
    inventory_products = list(
        inventory_product_qs.prefetch_related("variants").order_by("stock", "name")
    )

    inventory_totals = Product.objects.aggregate(
        total_units=Sum("stock"),
        stock_value=Sum(F("stock") * F("price")),
    )
    inventory_stats = {
        "total_products": Product.objects.count(),
        "total_units": inventory_totals["total_units"] or 0,
        "stock_value": int(inventory_totals["stock_value"] or 0),
        "out_of_stock": Product.objects.filter(stock=0).count(),
        "low_stock": Product.objects.filter(
            available=True, stock__gte=1, stock__lte=LOW_STOCK_LIMIT
        ).count(),
        "hidden_products": Product.objects.filter(
            available=False, stock__gte=1
        ).count(),
    }

    current_user = current_user or UserModel()
    permissions = {
        "is_admin": is_admin(current_user),
        "is_staff_member": is_staff_member(current_user),
        "can_manage_orders": can_manage_orders(current_user),
        "can_manage_inventory": can_manage_inventory(current_user),
        "can_manage_products": can_manage_products(current_user),
        "can_delete_product": can_delete_product(current_user),
        "can_manage_coupons": can_manage_coupons(current_user),
        "can_manage_users": can_manage_users(current_user),
    }

    return {
        "total_orders": status_counts["total"],
        "pending_orders": status_counts["pending"],
        "processing_orders": status_counts["processing"],
        "shipping_orders": status_counts["shipping"],
        "delivered_orders": status_counts["delivered"],
        "cancelled_orders": status_counts["cancelled"],
        "total_revenue": total_revenue,
        "month_revenue": month_revenue,
        "daily_revenue": daily_revenue,
        "revenue_chart": revenue_chart,
        "monthly_revenue": monthly_revenue,
        "orders_chart": orders_chart,
        "top_products": top_products,
        "category_revenue": category_revenue,
        "status_chart": status_chart,
        "revenue_current_total": current_total,
        "revenue_previous_total": previous_total,
        "revenue_growth_pct": growth_pct,
        "revenue_growth_label": growth_label,
        "revenue_growth_class": growth_class,
        "today_orders": today_orders,
        "today_revenue": today_revenue,
        "today_new_accounts": today_new_accounts,
        "recent_orders": [
            decorate_order_tracking(order)
            for order in orders.order_by("-created_at")[:RECENT_ORDER_LIMIT]
        ],
        "low_stock_products": Product.objects.filter(
            available=True, stock__lte=5
        ).order_by("stock", "name")[:LOW_STOCK_LIMIT],
        "active_coupons": Coupon.objects.filter(is_active=True).count(),
        "product_categories": Category.objects.all(),
        "coupons": Coupon.objects.all().order_by("-created_at"),
        "recent_products": Product.objects.select_related("category").order_by(
            "-created"
        ),
        "product_form": effective_form_data,
        "product_form_variant_rows": build_variant_rows(effective_form_data),
        "variant_matrix": build_variant_matrix(effective_form_data),
        "product_form_errors": form_errors or [],
        "editing_product": editing_product,
        "editing_product_gallery": (
            editing_product.gallery_images.all()[:MAX_PRODUCT_GALLERY_IMAGES]
            if editing_product
            else []
        ),
        "editing_product_gallery_slots": build_gallery_slot_rows(editing_product),
        "inventory_stats": inventory_stats,
        "inventory_products": inventory_products,
        "inventory_status": inventory_status or "",
        "inventory_q": inventory_q or "",
        "low_stock_limit": LOW_STOCK_LIMIT,
        "permissions": permissions,
        "manage_users": UserModel.objects.all().order_by(
            "-is_superuser", "-is_staff", "username"
        ),
        "staff_count": UserModel.objects.filter(is_staff=True).count(),
    }


def save_admin_product(request, product=None):
    is_update = product is not None
    post_data = request.POST.copy()
    post_data["category"] = post_data.get("category_id", "")
    if "category_id" in post_data:
        del post_data["category_id"]
    post_data.pop("slug", None)
    if "matrix_sizes" in post_data:
        matrix_arrays = _matrix_post_to_arrays(post_data)
        for key, values in matrix_arrays.items():
            post_data.setlist(key + "[]", values)

    form = ProductForm(post_data, request.FILES, instance=product)
    form.fields.pop("slug", None)

    if not form.is_valid():
        errors = []
        for field, field_errors in form.errors.items():
            for err in field_errors:
                label = {
                    "category": "Danh mục",
                    "name": "Tên sản phẩm",
                    "price": "Giá bán",
                    "image": "Ảnh đại diện",
                    "image_url": "URL ảnh đại diện",
                    "description": "Mô tả",
                }.get(field, field)
                errors.append(f"{label}: {err}")
        form_data = build_admin_product_form_data(request)
        return None, form_data, errors, None

    cd = form.cleaned_data
    errors = []

    try:
        variant_rows = ProductVariantFormSet.validate_variants(post_data)
    except forms.ValidationError as e:
        errors.extend(e.messages)
        variant_rows = []

    main_image = request.FILES.get("image")
    if main_image:
        _validate_uploaded_file(main_image, errors, "Ảnh đại diện")

    uploaded_gallery_images = []
    for item in request.FILES.getlist("gallery_images"):
        if item:
            _validate_uploaded_file(item, errors, "Ảnh gallery")
            uploaded_gallery_images.append(item)

    remove_gallery_image_ids = {
        str(item).strip()
        for item in request.POST.getlist("remove_gallery_image_ids")
        if str(item).strip()
    }
    slot_uploads = []
    slot_remove_indexes = set()

    for index in range(MAX_PRODUCT_GALLERY_IMAGES):
        uploaded_file = request.FILES.get(f"gallery_slot_{index}")
        remove_requested = request.POST.get(f"remove_gallery_slot_{index}") == "on"
        if uploaded_file:
            _validate_uploaded_file(uploaded_file, errors, f"Slot {index + 1}")
            slot_uploads.append((index, uploaded_file))
        if remove_requested:
            slot_remove_indexes.add(index)

    category = cd["category"]

    stock_input = (request.POST.get("stock", "") or "").strip()
    stock = safe_int(stock_input, default=0, minimum=0)

    existing_base_count = 0
    existing_gallery_count = 0
    if product:
        existing_base_count = 1 if (product.image or product.image_url) else 0
        existing_gallery_count = (
            product.gallery_images.exclude(id__in=remove_gallery_image_ids)
            .exclude(sort_order__in=slot_remove_indexes)
            .count()
        )
        existing_gallery_count = min(
            existing_gallery_count + len(slot_uploads), MAX_PRODUCT_GALLERY_IMAGES
        )

    new_base_count = 1 if (request.FILES.get("image") or cd.get("image_url")) else 0
    if not new_base_count and product:
        new_base_count = existing_base_count

    total_images_after_save = new_base_count + min(
        MAX_PRODUCT_GALLERY_IMAGES,
        existing_gallery_count + len(uploaded_gallery_images),
    )
    if total_images_after_save > MAX_PRODUCT_GALLERY_IMAGES:
        errors.append(
            f"Mỗi sản phẩm chỉ được tối đa {MAX_PRODUCT_GALLERY_IMAGES} hình ảnh. "
            f"Bạn có thể để 0 đến {MAX_PRODUCT_GALLERY_IMAGES} hình, nhưng không được vượt quá {MAX_PRODUCT_GALLERY_IMAGES}."
        )

    requires_variant = bool(category and category.slug in APPAREL_CATEGORY_SLUGS)
    if requires_variant and not variant_rows:
        errors.append("Danh mục áo/quần cần ít nhất một biến thể màu và size.")

    seen_variants = set()
    for row in variant_rows:
        key = (row["color_name"].casefold(), row["size"].casefold())
        if key in seen_variants:
            errors.append(
                f"Biến thể {row['color_name']} / {row['size']} đang bị trùng."
            )
            break
        seen_variants.add(key)

    if errors:
        form_data = build_admin_product_form_data(request)
        return None, form_data, errors, None

    if requires_variant or variant_rows:
        stock = sum(item["stock"] for item in variant_rows if item["is_active"])

    slug_base = (
        slugify(cd["name"]) or f"san-pham-{timezone.now().strftime('%Y%m%d%H%M%S')}"
    )
    slug = product.slug if product else slug_base
    if product is None or product.name != cd["name"]:
        slug = slug_base
        slug_qs = Product.objects.all()
        if product:
            slug_qs = slug_qs.exclude(id=product.id)
        counter = 2
        while slug_qs.filter(slug=slug).exists():
            slug = f"{slug_base}-{counter}"
            counter += 1

    with transaction.atomic():
        if product is None:
            product = Product.objects.create(
                category=category,
                name=cd["name"],
                slug=slug,
                image=request.FILES.get("image"),
                image_url=cd.get("image_url", ""),
                description=cd.get("description", ""),
                price=cd["price"],
                stock=stock,
                available=cd.get("available", False),
                featured=cd.get("featured", False),
            )
        else:
            product.category = category
            product.name = cd["name"]
            product.slug = slug
            if request.FILES.get("image"):
                product.image = request.FILES.get("image")
            product.image_url = cd.get("image_url", "")
            product.description = cd.get("description", "")
            product.price = cd["price"]
            product.stock = stock
            product.available = cd.get("available", False)
            product.featured = cd.get("featured", False)
            product.save()
            product.variants.all().delete()
            if remove_gallery_image_ids:
                product.gallery_images.filter(id__in=remove_gallery_image_ids).delete()
            if slot_remove_indexes:
                product.gallery_images.filter(
                    sort_order__in=slot_remove_indexes
                ).delete()

        for row in variant_rows:
            ProductVariant.objects.create(
                product=product,
                color_name=row["color_name"],
                color_code=row["color_code"],
                size=row["size"],
                stock=row["stock"],
                is_active=row["is_active"],
            )

        existing_images_by_sort = {
            item.sort_order: item
            for item in product.gallery_images.order_by("sort_order", "id")[
                :MAX_PRODUCT_GALLERY_IMAGES
            ]
        }
        for slot_index, image_file in slot_uploads:
            existing_image = existing_images_by_sort.get(slot_index)
            if existing_image:
                existing_image.image = image_file
                existing_image.sort_order = slot_index
                existing_image.save(update_fields=["image", "sort_order"])
            else:
                ProductImage.objects.create(
                    product=product, image=image_file, sort_order=slot_index
                )

        current_gallery_count = product.gallery_images.count()
        for offset, image_file in enumerate(
            uploaded_gallery_images, start=current_gallery_count
        ):
            if offset >= MAX_PRODUCT_GALLERY_IMAGES:
                break
            ProductImage.objects.create(
                product=product, image=image_file, sort_order=offset
            )
        for index, item in enumerate(
            product.gallery_images.order_by("sort_order", "id")
        ):
            if index >= MAX_PRODUCT_GALLERY_IMAGES:
                item.delete()
                continue
            if item.sort_order != index:
                item.sort_order = index
                item.save(update_fields=["sort_order"])

    action_label = "cập nhật" if is_update else "tạo"
    return product, build_admin_product_form_data(), [], action_label


def mark_product_out_of_stock(product):
    with transaction.atomic():
        product.variants.update(stock=0, is_active=False)
        product.stock = 0
        product.available = False
        product.featured = False
        product.save(update_fields=["stock", "available", "featured", "updated"])


@login_required
def admin_dashboard(request):
    if not is_staff_member(request.user):
        messages.error(request, "Bạn không có quyền truy cập trang này.")
        return redirect("products:product_list")

    order_status = request.GET.get("order_status", "").strip() or None
    order_q = request.GET.get("order_q", "").strip() or None
    inventory_status = request.GET.get("inventory_status", "").strip()
    inventory_q = request.GET.get("inventory_q", "").strip()

    if request.method == "POST":
        action = request.POST.get("action", "save_product").strip()

        if action == "update_order_status":
            if not can_manage_orders(request.user):
                messages.error(request, "Bạn không có quyền cập nhật đơn hàng.")
                return redirect("orders:admin_dashboard")
            order_id = request.POST.get("order_id")
            status_post = request.POST.copy()
            status_post["status"] = status_post.get("new_status", "")
            status_post.pop("new_status", None)
            order_status_form = OrderStatusForm(status_post)
            if order_status_form.is_valid():
                order = get_object_or_404(Order, id=order_id)
                try:
                    apply_order_status_change(
                        order,
                        order_status_form.cleaned_data["status"],
                        order_status_form.cleaned_data.get("is_paid", False),
                    )
                except ValueError as exc:
                    messages.error(request, str(exc))
                    return redirect("orders:admin_dashboard")
                messages.success(
                    request,
                    f"Đơn #{order.id} đã chuyển sang trạng thái '{dict(Order.STATUS_CHOICES).get(order.status)}'.",
                )
            else:
                for err in order_status_form.errors.get(
                    "__all__", order_status_form.errors.get("status", [])
                ):
                    messages.error(request, err)
            return redirect("orders:admin_dashboard")

        if action == "refund_order":
            if not can_manage_orders(request.user):
                messages.error(request, "Bạn không có quyền xử lý đơn hàng.")
                return redirect("orders:admin_dashboard")
            order = get_object_or_404(Order, id=request.POST.get("order_id"))
            if order.status == "cancelled":
                messages.error(
                    request, f"Đơn #{order.id} đã được hủy/hoàn tiền trước đó."
                )
                return redirect("orders:admin_dashboard")
            was_paid = order.is_paid
            amount = int(order.total_amount)
            try:
                apply_order_status_change(order, "cancelled", is_paid=False)
            except ValueError as exc:
                messages.error(request, str(exc))
                return redirect("orders:admin_dashboard")
            refund_note = f"[REFUND {amount}đ] {request.user.username} {timezone.now():%d/%m/%Y %H:%M}"
            order.note = (
                f"{order.note}\n{refund_note}".strip() if order.note else refund_note
            )
            order.save(update_fields=["note", "updated_at"])
            if was_paid:
                messages.success(
                    request, f"Đã hoàn tiền {amount:,}đ cho đơn #{order.id}."
                )
            else:
                messages.success(request, f"Đã hủy đơn #{order.id} và trả hàng về kho.")
            return redirect("orders:admin_dashboard")

        if action == "save_coupon":
            if not can_manage_coupons(request.user):
                messages.error(request, "Chỉ quản trị viên được quản lý mã giảm giá.")
                return redirect("orders:admin_dashboard")
            coupon_form = CouponForm(request.POST)
            if coupon_form.is_valid():
                coupon_id = request.POST.get("coupon_id", "").strip()
                cd = coupon_form.cleaned_data
                if coupon_id:
                    coupon = get_object_or_404(Coupon, id=coupon_id)
                    for field, value in cd.items():
                        setattr(coupon, field, value)
                    coupon.save()
                    messages.success(request, f"Đã cập nhật mã '{cd['code']}'.")
                else:
                    cd.pop("usage_limit", None)
                    cd.pop("used_count", None)
                    Coupon.objects.create(**cd)
                    messages.success(request, f"Đã tạo mã '{cd['code']}'.")
                return redirect("orders:admin_dashboard")
            for field, field_errors in coupon_form.errors.items():
                for err in field_errors:
                    messages.error(request, f"{field}: {err}")
            return redirect("orders:admin_dashboard")

        if action == "delete_coupon":
            if not can_manage_coupons(request.user):
                messages.error(request, "Chỉ quản trị viên được quản lý mã giảm giá.")
                return redirect("orders:admin_dashboard")
            coupon = get_object_or_404(Coupon, id=request.POST.get("coupon_id"))
            code = coupon.code
            coupon.delete()
            messages.success(request, f"Đã xóa mã '{code}'.")
            return redirect("orders:admin_dashboard")

        if action == "create_user":
            if not can_manage_users(request.user):
                messages.error(request, "Chỉ quản trị viên được tạo tài khoản.")
                return redirect("orders:admin_dashboard")
            username = request.POST.get("username", "").strip()
            password = request.POST.get("password", "")
            email = request.POST.get("email", "").strip()
            new_role = request.POST.get("role", "").strip()
            if new_role not in ("admin", "staff", "user"):
                messages.error(request, "Vai trò không hợp lệ.")
                return redirect("orders:admin_dashboard")
            if not username:
                messages.error(request, "Tên đăng nhập không được để trống.")
                return redirect("orders:admin_dashboard")
            if len(password) < 8:
                messages.error(request, "Mật khẩu phải có ít nhất 8 ký tự.")
                return redirect("orders:admin_dashboard")
            UserModel = get_user_model()
            if UserModel.objects.filter(username=username).exists():
                messages.error(request, f"Tên đăng nhập '{username}' đã tồn tại.")
                return redirect("orders:admin_dashboard")
            new_user = UserModel.objects.create_user(
                username=username, password=password, email=email
            )
            if new_role == "admin":
                new_user.is_staff = True
                new_user.is_superuser = True
            elif new_role == "staff":
                new_user.is_staff = True
            new_user.save(update_fields=["is_staff", "is_superuser"])
            role_labels = {
                "admin": "quản trị viên",
                "staff": "nhân viên",
                "user": "khách hàng",
            }
            messages.success(
                request, f"Đã tạo tài khoản '{username}' ({role_labels[new_role]})."
            )
            return redirect("orders:admin_dashboard")

        if action == "delete_user":
            if not can_manage_users(request.user):
                messages.error(request, "Chỉ quản trị viên được xóa tài khoản.")
                return redirect("orders:admin_dashboard")
            UserModel = get_user_model()
            target = get_object_or_404(UserModel, id=request.POST.get("user_id"))
            if target.id == request.user.id:
                messages.error(request, "Không thể xóa tài khoản của chính bạn.")
                return redirect("orders:admin_dashboard")
            if target.is_superuser:
                remaining_admins = (
                    UserModel.objects.filter(is_superuser=True)
                    .exclude(id=target.id)
                    .count()
                )
                if remaining_admins == 0:
                    messages.error(request, "Không thể xóa quản trị viên cuối cùng.")
                    return redirect("orders:admin_dashboard")
            username = target.username
            target.delete()
            messages.success(request, f"Đã xóa tài khoản '{username}'.")
            return redirect("orders:admin_dashboard")

        if action == "set_user_role":
            if not can_manage_users(request.user):
                messages.error(request, "Chỉ quản trị viên được phân quyền tài khoản.")
                return redirect("orders:admin_dashboard")
            target = get_object_or_404(get_user_model(), id=request.POST.get("user_id"))
            target_role = request.POST.get("role", "").strip()
            if target_role not in ("admin", "staff", "user"):
                messages.error(request, "Vai trò không hợp lệ.")
                return redirect("orders:admin_dashboard")

            if target_role != "admin":
                remaining_admins = (
                    get_user_model()
                    .objects.filter(is_superuser=True)
                    .exclude(id=target.id)
                    .count()
                )
                if target.is_superuser and remaining_admins == 0:
                    messages.error(
                        request, "Không thể gỡ quyền quản trị viên cuối cùng."
                    )
                    return redirect("orders:admin_dashboard")

            if target_role == "admin":
                target.is_staff = True
                target.is_superuser = True
            elif target_role == "staff":
                target.is_staff = True
                target.is_superuser = False
            else:
                target.is_staff = False
                target.is_superuser = False
            target.save(update_fields=["is_staff", "is_superuser"])
            labels = {
                "admin": "quản trị viên",
                "staff": "nhân viên",
                "user": "khách hàng",
            }
            messages.success(
                request,
                f"Đã đặt vai trò '{labels[target_role]}' cho '{target.username}'.",
            )
            return redirect("orders:admin_dashboard")

        if action == "bulk_toggle_available":
            if not can_manage_products(request.user):
                messages.error(request, "Bạn không có quyền quản lý sản phẩm.")
                return redirect("orders:admin_dashboard")
            product_ids = request.POST.get("product_ids", "")
            make_available = request.POST.get("make_available") == "1"
            ids = [pid for pid in product_ids.split(",") if pid.strip().isdigit()]
            if ids:
                count = Product.objects.filter(id__in=ids).update(
                    available=make_available
                )
                label = "hiện" if make_available else "ẩn"
                messages.success(request, f"Đã {label} {count} sản phẩm.")
            return redirect("orders:admin_dashboard")

        if action == "delete_product":
            if not can_delete_product(request.user):
                messages.error(request, "Chỉ quản trị viên được xóa sản phẩm.")
                return redirect("orders:admin_dashboard")
            product = get_object_or_404(Product, id=request.POST.get("product_id"))
            product_name = product.name
            product.delete()
            messages.success(request, f"Đã xóa sản phẩm '{product_name}'.")
            return redirect("orders:admin_dashboard")

        if action == "mark_out_of_stock":
            if not can_manage_products(request.user):
                messages.error(request, "Bạn không có quyền quản lý sản phẩm.")
                return redirect("orders:admin_dashboard")
            product = get_object_or_404(Product, id=request.POST.get("product_id"))
            mark_product_out_of_stock(product)
            messages.success(request, f"Đã đánh dấu '{product.name}' là hết hàng.")
            return redirect("orders:admin_dashboard")

        product_id = request.POST.get("product_id", "").strip()
        editing_product = (
            Product.objects.filter(id=product_id).first() if product_id else None
        )
        product, form_data, errors, action_label = save_admin_product(
            request, product=editing_product
        )
        if product:
            messages.success(
                request, f"Đã {action_label} sản phẩm '{product.name}' thành công."
            )
            return redirect("orders:admin_dashboard")

        return render(
            request,
            "admin/admin_dashboard.html",
            build_admin_dashboard_context(
                form_data=form_data,
                form_errors=errors,
                editing_product=editing_product,
                order_status=order_status or None,
                order_q=order_q or None,
                current_user=request.user,
                inventory_status=inventory_status,
                inventory_q=inventory_q,
            ),
        )

    editing_product = None
    form_data = None
    edit_id = request.GET.get("edit", "").strip()
    if edit_id:
        editing_product = get_object_or_404(
            Product.objects.prefetch_related("variants"), id=edit_id
        )
        form_data = build_admin_product_form_from_instance(editing_product)

    return render(
        request,
        "admin/admin_dashboard.html",
        build_admin_dashboard_context(
            form_data=form_data,
            editing_product=editing_product,
            order_status=order_status,
            order_q=order_q,
            current_user=request.user,
            inventory_status=inventory_status,
            inventory_q=inventory_q,
        ),
    )
