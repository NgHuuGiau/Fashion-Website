import re
from datetime import timedelta

from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.text import slugify

from products.constants import APPAREL_CATEGORY_SLUGS
from products.models import Category, MAX_PRODUCT_GALLERY_IMAGES, Product, ProductImage, ProductVariant

from .admin_forms import CouponForm, OrderStatusForm, ProductForm, ProductVariantFormSet
from .cart import safe_int
from .models import Coupon, Order

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
            for item in product.gallery_images.order_by("sort_order", "id")[:MAX_PRODUCT_GALLERY_IMAGES]
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
    sizes = [size.strip() for size in post_data.getlist("matrix_sizes") if size and size.strip()]
    color_names = post_data.getlist("matrix_color_name[]")
    color_codes = post_data.getlist("matrix_color_code[]")
    active_indexes = {value.strip() for value in post_data.getlist("matrix_color_active[]") if value.strip()}

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
            "variant_row_key": [f"row-{index + 1}" for index in range(len(DEFAULT_MATRIX_SIZES))],
            "variant_color_name": [DEFAULT_MATRIX_COLORS[0]["name"]] * len(DEFAULT_MATRIX_SIZES),
            "variant_color_code": [DEFAULT_MATRIX_COLORS[0]["code"]] * len(DEFAULT_MATRIX_SIZES),
            "variant_size": list(DEFAULT_MATRIX_SIZES),
            "variant_stock": ["0"] * len(DEFAULT_MATRIX_SIZES),
            "variant_is_active": [f"row-{index + 1}" for index in range(len(DEFAULT_MATRIX_SIZES))],
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
        "gallery_count": safe_int(request.POST.get("gallery_count", "0"), default=0, minimum=0),
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
        form_data["variant_color_code"].append(variant.color_code if variant else "#111111")
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
        row_key = form_data["variant_row_key"][index] if index < len(form_data["variant_row_key"]) else f"row-{index + 1}"
        variant_rows.append(
            {
                "row_key": row_key,
                "color_name": form_data["variant_color_name"][index] if index < len(form_data["variant_color_name"]) else "",
                "color_code": form_data["variant_color_code"][index] if index < len(form_data["variant_color_code"]) else "#111111",
                "size": form_data["variant_size"][index] if index < len(form_data["variant_size"]) else "",
                "stock": form_data["variant_stock"][index] if index < len(form_data["variant_stock"]) else "0",
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
            cell_stock[(color_index_by_key[color_key], size_index_by_key[size])] = str(row["stock"])

    for color in color_rows:
        color["stocks"] = [
            {"size": size, "token": _size_token(size), "stock": cell_stock.get((color["index"], index), "0")}
            for index, size in enumerate(sizes)
        ]

    return {"colors": color_rows, "sizes": sizes}


def build_admin_dashboard_context(form_data=None, form_errors=None, editing_product=None, order_status=None, order_q=None):
    effective_form_data = form_data or build_admin_product_form_data()
    all_orders = Order.objects.all().prefetch_related("items__product")
    orders_qs = all_orders
    if order_status:
        orders_qs = orders_qs.filter(status=order_status)
    if order_q:
        orders_qs = orders_qs.filter(
            Q(id__icontains=order_q) | Q(customer_name__icontains=order_q) | Q(phone__icontains=order_q)
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
        month_revenue=Sum("total_amount", filter=Q(status="delivered", created_at__gte=month_start)),
        today_orders=Count("id", filter=Q(created_at__date=today)),
        today_revenue=Sum("total_amount", filter=Q(status="delivered", created_at__date=today)),
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
    growth_pct = ((current_total - previous_total) / previous_total * 100) if previous_total else 0
    chart_max = max([revenue_by_day.get(day, 0) for day in chart_days] or [0]) or 1
    weekday_labels = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]
    revenue_chart = [
        {
            "day": day,
            "label": weekday_labels[day.weekday()],
            "date_label": day.strftime("%d/%m"),
            "total": revenue_by_day.get(day, 0),
            "orders_count": next(
                (int(item["orders_count"] or 0) for item in daily_revenue if item["day"] == day),
                0,
            ),
            "height": max(8, int((revenue_by_day.get(day, 0) / chart_max) * 100)) if revenue_by_day.get(day, 0) else 8,
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

    total_revenue = combined.pop("total_revenue") or 0
    month_revenue = combined.pop("month_revenue") or 0
    today_orders = combined.pop("today_orders") or 0
    today_revenue = combined.pop("today_revenue") or 0
    status_counts = combined
    UserModel = get_user_model()
    today_new_accounts = UserModel.objects.filter(date_joined__date=today).count()

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
        "revenue_current_total": current_total,
        "revenue_previous_total": previous_total,
        "revenue_growth_pct": growth_pct,
        "revenue_growth_label": growth_label,
        "revenue_growth_class": growth_class,
        "today_orders": today_orders,
        "today_revenue": today_revenue,
        "today_new_accounts": today_new_accounts,
        "recent_orders": [decorate_order_tracking(order) for order in orders.order_by("-created_at")[:RECENT_ORDER_LIMIT]],
        "low_stock_products": Product.objects.filter(available=True, stock__lte=5).order_by("stock", "name")[:LOW_STOCK_LIMIT],
        "active_coupons": Coupon.objects.filter(is_active=True).count(),
        "product_categories": Category.objects.all(),
        "coupons": Coupon.objects.all().order_by("-created_at"),
        "recent_products": Product.objects.select_related("category").order_by("-created"),
        "product_form": effective_form_data,
        "product_form_variant_rows": build_variant_rows(effective_form_data),
        "variant_matrix": build_variant_matrix(effective_form_data),
        "product_form_errors": form_errors or [],
        "editing_product": editing_product,
        "editing_product_gallery": (
            editing_product.gallery_images.all()[:MAX_PRODUCT_GALLERY_IMAGES] if editing_product else []
        ),
        "editing_product_gallery_slots": build_gallery_slot_rows(editing_product),
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
                label = {"category": "Danh mục", "name": "Tên sản phẩm", "price": "Giá bán", "image": "Ảnh đại diện", "image_url": "URL ảnh đại diện", "description": "Mô tả"}.get(field, field)
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

    remove_gallery_image_ids = {str(item).strip() for item in request.POST.getlist("remove_gallery_image_ids") if str(item).strip()}
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
            product.gallery_images.exclude(id__in=remove_gallery_image_ids).exclude(sort_order__in=slot_remove_indexes).count()
        )
        existing_gallery_count = min(existing_gallery_count + len(slot_uploads), MAX_PRODUCT_GALLERY_IMAGES)

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
            errors.append(f"Biến thể {row['color_name']} / {row['size']} đang bị trùng.")
            break
        seen_variants.add(key)

    if errors:
        form_data = build_admin_product_form_data(request)
        return None, form_data, errors, None

    if requires_variant or variant_rows:
        stock = sum(item["stock"] for item in variant_rows if item["is_active"])

    slug_base = slugify(cd["name"]) or f"san-pham-{timezone.now().strftime('%Y%m%d%H%M%S')}"
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
                product.gallery_images.filter(sort_order__in=slot_remove_indexes).delete()

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
            for item in product.gallery_images.order_by("sort_order", "id")[:MAX_PRODUCT_GALLERY_IMAGES]
        }
        for slot_index, image_file in slot_uploads:
            existing_image = existing_images_by_sort.get(slot_index)
            if existing_image:
                existing_image.image = image_file
                existing_image.sort_order = slot_index
                existing_image.save(update_fields=["image", "sort_order"])
            else:
                ProductImage.objects.create(product=product, image=image_file, sort_order=slot_index)

        current_gallery_count = product.gallery_images.count()
        for offset, image_file in enumerate(uploaded_gallery_images, start=current_gallery_count):
            if offset >= MAX_PRODUCT_GALLERY_IMAGES:
                break
            ProductImage.objects.create(product=product, image=image_file, sort_order=offset)
        for index, item in enumerate(product.gallery_images.order_by("sort_order", "id")):
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
    if not request.user.is_staff:
        messages.error(request, "Bạn không có quyền truy cập trang này.")
        return redirect("products:product_list")

    order_status = request.GET.get("order_status", "").strip() or None
    order_q = request.GET.get("order_q", "").strip() or None

    if request.method == "POST":
        action = request.POST.get("action", "save_product").strip()

        if action == "update_order_status":
            order_id = request.POST.get("order_id")
            status_post = request.POST.copy()
            status_post["status"] = status_post.get("new_status", "")
            status_post.pop("new_status", None)
            order_status_form = OrderStatusForm(status_post)
            if order_status_form.is_valid():
                order = get_object_or_404(Order, id=order_id)
                order.status = order_status_form.cleaned_data["status"]
                order.is_paid = order_status_form.cleaned_data.get("is_paid", False)
                order.save(update_fields=["status", "is_paid", "updated_at"])
                messages.success(request, f"Đơn #{order.id} đã chuyển sang trạng thái '{dict(Order.STATUS_CHOICES).get(order.status)}'.")
            else:
                for err in order_status_form.errors.get("__all__", order_status_form.errors.get("status", [])):
                    messages.error(request, err)
            return redirect("orders:admin_dashboard")

        if action == "save_coupon":
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
            coupon = get_object_or_404(Coupon, id=request.POST.get("coupon_id"))
            code = coupon.code
            coupon.delete()
            messages.success(request, f"Đã xóa mã '{code}'.")
            return redirect("orders:admin_dashboard")

        if action == "bulk_toggle_available":
            product_ids = request.POST.get("product_ids", "")
            make_available = request.POST.get("make_available") == "1"
            ids = [pid for pid in product_ids.split(",") if pid.strip().isdigit()]
            if ids:
                count = Product.objects.filter(id__in=ids).update(available=make_available)
                label = "hiện" if make_available else "ẩn"
                messages.success(request, f"Đã {label} {count} sản phẩm.")
            return redirect("orders:admin_dashboard")

        if action == "delete_product":
            product = get_object_or_404(Product, id=request.POST.get("product_id"))
            product_name = product.name
            product.delete()
            messages.success(request, f"Đã xóa sản phẩm '{product_name}'.")
            return redirect("orders:admin_dashboard")

        if action == "mark_out_of_stock":
            product = get_object_or_404(Product, id=request.POST.get("product_id"))
            mark_product_out_of_stock(product)
            messages.success(request, f"Đã đánh dấu '{product.name}' là hết hàng.")
            return redirect("orders:admin_dashboard")

        product_id = request.POST.get("product_id", "").strip()
        editing_product = Product.objects.filter(id=product_id).first() if product_id else None
        product, form_data, errors, action_label = save_admin_product(request, product=editing_product)
        if product:
            messages.success(request, f"Đã {action_label} sản phẩm '{product.name}' thành công.")
            return redirect("orders:admin_dashboard")

        return render(
            request,
            "admin/admin_dashboard.html",
            build_admin_dashboard_context(form_data=form_data, form_errors=errors, editing_product=editing_product, order_status=order_status or None, order_q=order_q or None),
        )

    editing_product = None
    form_data = None
    edit_id = request.GET.get("edit", "").strip()
    if edit_id:
        editing_product = get_object_or_404(Product.objects.prefetch_related("variants"), id=edit_id)
        form_data = build_admin_product_form_from_instance(editing_product)

    return render(
        request,
        "admin/admin_dashboard.html",
        build_admin_dashboard_context(form_data=form_data, editing_product=editing_product, order_status=order_status, order_q=order_q),
    )
