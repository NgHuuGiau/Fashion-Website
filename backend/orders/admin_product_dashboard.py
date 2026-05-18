from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.text import slugify

from products.models import Category, Product, ProductImage, ProductVariant

from .cart import safe_int
from .models import Coupon, Order


def build_gallery_slot_rows(product=None):
    slots = []
    images_by_sort_order = {}
    if product:
        images_by_sort_order = {item.sort_order: item for item in product.gallery_images.order_by("sort_order", "id")[:6]}

    for index in range(6):
        slots.append(
            {
                "slot_index": index,
                "label": f"Slot {index + 1}",
                "image": images_by_sort_order.get(index),
            }
        )
    return slots


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
            "variant_row_key": ["row-1"],
            "variant_color_name": ["Đen"],
            "variant_color_code": ["#111111"],
            "variant_size": ["M"],
            "variant_stock": ["0"],
            "variant_is_active": ["row-1"],
        }

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
        "variant_row_key": request.POST.getlist("variant_row_key[]"),
        "variant_color_name": request.POST.getlist("variant_color_name[]"),
        "variant_color_code": request.POST.getlist("variant_color_code[]"),
        "variant_size": request.POST.getlist("variant_size[]"),
        "variant_stock": request.POST.getlist("variant_stock[]"),
        "variant_is_active": request.POST.getlist("variant_is_active[]"),
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


def build_admin_dashboard_context(form_data=None, form_errors=None, editing_product=None):
    effective_form_data = form_data or build_admin_product_form_data()
    orders = Order.objects.all().prefetch_related("items__product")
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    status_counts = orders.aggregate(
        total=Count("id"),
        pending=Count("id", filter=Q(status="pending")),
        processing=Count("id", filter=Q(status="processing")),
        shipping=Count("id", filter=Q(status="shipping")),
        delivered=Count("id", filter=Q(status="delivered")),
        cancelled=Count("id", filter=Q(status="cancelled")),
    )
    total_revenue = orders.filter(status="delivered").aggregate(total=Sum("total_amount"))["total"] or 0
    month_revenue = (
        orders.filter(status="delivered", created_at__gte=month_start).aggregate(total=Sum("total_amount"))["total"] or 0
    )
    daily_revenue = (
        orders.filter(status="delivered")
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(total=Sum("total_amount"), orders_count=Count("id"))
        .order_by("-day")[:14]
    )

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
        "recent_orders": orders.order_by("-created_at")[:10],
        "low_stock_products": Product.objects.filter(available=True, stock__lte=5).order_by("stock", "name")[:10],
        "active_coupons": Coupon.objects.filter(is_active=True).count(),
        "product_categories": Category.objects.all(),
        "recent_products": Product.objects.select_related("category").order_by("-created"),
        "product_form": effective_form_data,
        "product_form_variant_rows": build_variant_rows(effective_form_data),
        "product_form_errors": form_errors or [],
        "editing_product": editing_product,
        "editing_product_gallery": editing_product.gallery_images.all()[:6] if editing_product else [],
        "editing_product_gallery_slots": build_gallery_slot_rows(editing_product),
    }


def save_admin_product(request, product=None):
    form_data = build_admin_product_form_data(request)
    errors = []
    uploaded_gallery_images = [item for item in request.FILES.getlist("gallery_images") if item]
    remove_gallery_image_ids = {str(item).strip() for item in form_data["remove_gallery_image_ids"] if str(item).strip()}
    slot_uploads = []
    slot_remove_indexes = set()

    for index in range(6):
        uploaded_file = request.FILES.get(f"gallery_slot_{index}")
        remove_requested = request.POST.get(f"remove_gallery_slot_{index}") == "on"
        if uploaded_file:
            slot_uploads.append((index, uploaded_file))
        if remove_requested:
            slot_remove_indexes.add(index)

    category = Category.objects.filter(id=form_data["category_id"]).first()
    if not category:
        errors.append("Vui lòng chọn danh mục sản phẩm.")

    if not form_data["name"]:
        errors.append("Vui lòng nhập tên sản phẩm.")

    price_input = (form_data["price"] or "").replace(",", "").strip()
    price = int(price_input) if price_input.isdigit() else None
    if price is None:
        errors.append("Giá sản phẩm không hợp lệ.")

    stock_input = (form_data["stock"] or "").strip()
    stock = safe_int(stock_input, default=0, minimum=0)
    if stock_input and str(stock) != stock_input:
        errors.append("Tồn kho tổng không hợp lệ.")

    existing_base_count = 0
    existing_gallery_count = 0
    if product:
        existing_base_count = 1 if (product.image or product.image_url) else 0
        existing_gallery_count = (
            product.gallery_images.exclude(id__in=remove_gallery_image_ids).exclude(sort_order__in=slot_remove_indexes).count()
        )
        existing_gallery_count = min(existing_gallery_count + len(slot_uploads), 6)

    new_base_count = 1 if (request.FILES.get("image") or form_data["image_url"]) else 0
    if not new_base_count and product:
        new_base_count = existing_base_count

    total_images_after_save = new_base_count + min(6, existing_gallery_count + len(uploaded_gallery_images))
    if total_images_after_save > 6:
        errors.append("Mỗi sản phẩm chỉ được tối đa 6 hình ảnh. Bạn có thể để 0 đến 6 hình, nhưng không được vượt quá 6.")

    variant_rows = []
    max_rows = max(
        len(form_data["variant_row_key"]),
        len(form_data["variant_color_name"]),
        len(form_data["variant_color_code"]),
        len(form_data["variant_size"]),
        len(form_data["variant_stock"]),
    )
    active_keys = set(form_data["variant_is_active"])

    for index in range(max_rows):
        row_key = form_data["variant_row_key"][index].strip() if index < len(form_data["variant_row_key"]) else f"row-{index + 1}"
        color_name = form_data["variant_color_name"][index].strip() if index < len(form_data["variant_color_name"]) else ""
        color_code = form_data["variant_color_code"][index].strip() if index < len(form_data["variant_color_code"]) else ""
        size = form_data["variant_size"][index].strip() if index < len(form_data["variant_size"]) else ""
        stock_raw = form_data["variant_stock"][index].strip() if index < len(form_data["variant_stock"]) else ""

        if not any([color_name, color_code, size, stock_raw]):
            continue

        variant_stock = safe_int(stock_raw, default=-1, minimum=-1)
        if variant_stock < 0:
            errors.append(f"Tồn kho biến thể ở dòng {index + 1} không hợp lệ.")
            continue
        if not color_name:
            errors.append(f"Dòng biến thể {index + 1} đang thiếu tên màu.")
        if not size:
            errors.append(f"Dòng biến thể {index + 1} đang thiếu size.")

        variant_rows.append(
            {
                "color_name": color_name,
                "color_code": color_code or "#111111",
                "size": size,
                "stock": variant_stock,
                "is_active": row_key in active_keys,
            }
        )

    requires_variant = bool(category and category.slug in {"ao", "quan"})
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
        return None, form_data, errors, None

    if requires_variant or variant_rows:
        stock = sum(item["stock"] for item in variant_rows if item["is_active"])
        form_data["stock"] = str(stock)

    slug_base = slugify(form_data["name"]) or f"san-pham-{timezone.now().strftime('%Y%m%d%H%M%S')}"
    slug = product.slug if product else slug_base
    if product is None or product.name != form_data["name"]:
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
                name=form_data["name"],
                slug=slug,
                image=request.FILES.get("image"),
                image_url=form_data["image_url"],
                description=form_data["description"],
                price=price,
                stock=stock,
                available=form_data["available"],
                featured=form_data["featured"],
            )
        else:
            product.category = category
            product.name = form_data["name"]
            product.slug = slug
            if request.FILES.get("image"):
                product.image = request.FILES.get("image")
            product.image_url = form_data["image_url"]
            product.description = form_data["description"]
            product.price = price
            product.stock = stock
            product.available = form_data["available"]
            product.featured = form_data["featured"]
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

        existing_images_by_sort = {item.sort_order: item for item in product.gallery_images.order_by("sort_order", "id")[:6]}
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
            if offset >= 6:
                break
            ProductImage.objects.create(product=product, image=image_file, sort_order=offset)
        for index, item in enumerate(product.gallery_images.order_by("sort_order", "id")):
            if index >= 6:
                item.delete()
                continue
            if item.sort_order != index:
                item.sort_order = index
                item.save(update_fields=["sort_order"])

    action_label = "cập nhật" if form_data["product_id"] else "tạo"
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

    if request.method == "POST":
        action = request.POST.get("action", "save_product").strip()

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
            build_admin_dashboard_context(form_data=form_data, form_errors=errors, editing_product=editing_product),
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
        build_admin_dashboard_context(form_data=form_data, editing_product=editing_product),
    )
