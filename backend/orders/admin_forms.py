import re
from datetime import datetime

from django import forms

from products.models import Product
from .models import Coupon, Order
from .constants import BANKS


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name", "category", "slug", "description",
            "price", "available", "featured", "image", "image_url",
        ]

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price is not None and price <= 0:
            raise forms.ValidationError("Giá sản phẩm phải lớn hơn 0.")
        return price

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        if not name:
            raise forms.ValidationError("Tên sản phẩm không được để trống.")
        return name


class ProductVariantFormSet:
    @staticmethod
    def validate_variants(data):
        row_keys = data.getlist("variant_row_key[]")
        color_names = data.getlist("variant_color_name[]")
        color_codes = data.getlist("variant_color_code[]")
        sizes = data.getlist("variant_size[]")
        stocks = data.getlist("variant_stock[]")
        active_keys = set(data.getlist("variant_is_active[]"))

        max_rows = max(
            len(row_keys), len(color_names), len(color_codes), len(sizes), len(stocks),
        )
        cleaned = []
        errors = []

        for index in range(max_rows):
            color_name = (color_names[index] if index < len(color_names) else "").strip()
            color_code = (color_codes[index] if index < len(color_codes) else "").strip()
            size = (sizes[index] if index < len(sizes) else "").strip()
            stock_raw = (stocks[index] if index < len(stocks) else "").strip()
            row_key = row_keys[index] if index < len(row_keys) else f"row-{index + 1}"

            if not any([color_name, color_code, size, stock_raw]):
                continue

            if not color_name:
                errors.append(f"Dòng biến thể {index + 1} đang thiếu tên màu.")
            if not size:
                errors.append(f"Dòng biến thể {index + 1} đang thiếu size.")

            try:
                stock = int(stock_raw) if stock_raw else 0
                if stock < 0:
                    raise ValueError
            except (ValueError, TypeError):
                errors.append(f"Tồn kho biến thể ở dòng {index + 1} không hợp lệ.")
                continue

            cleaned.append({
                "color_name": color_name,
                "color_code": color_code or "#111111",
                "size": size,
                "stock": stock,
                "is_active": row_key in active_keys,
            })

        if errors:
            raise forms.ValidationError(errors)

        return cleaned


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = [
            "code", "discount_type", "value", "min_order_amount",
            "max_discount_amount", "starts_at", "ends_at", "usage_limit",
            "max_uses_per_user",
        ]

    def clean(self):
        cleaned_data = super().clean()
        starts_at = cleaned_data.get("starts_at")
        ends_at = cleaned_data.get("ends_at")

        if starts_at and ends_at and starts_at >= ends_at:
            raise forms.ValidationError("Thời gian bắt đầu phải trước thời gian kết thúc.")

        return cleaned_data

    def clean_value(self):
        value = self.cleaned_data.get("value")
        if value is not None and value <= 0:
            raise forms.ValidationError("Giá trị mã giảm giá phải lớn hơn 0.")
        return value


class OrderStatusForm(forms.Form):
    status = forms.ChoiceField(choices=Order.STATUS_CHOICES)
    is_paid = forms.BooleanField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get("status")
        is_paid = cleaned_data.get("is_paid")

        if status == "delivered" and not is_paid:
            raise forms.ValidationError("Đơn hàng hoàn thành phải được đánh dấu là đã thanh toán.")

        return cleaned_data


class OrderSearchForm(forms.Form):
    q = forms.CharField(required=False, label="Tìm kiếm")
    status = forms.ChoiceField(
        required=False,
        choices=[("", "Tất cả trạng thái")] + Order.STATUS_CHOICES,
    )
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))

    def clean_date_from(self):
        value = self.cleaned_data.get("date_from")
        if isinstance(value, str):
            try:
                return datetime.strptime(value, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                raise forms.ValidationError("Ngày không hợp lệ.")
        return value

    def clean_date_to(self):
        value = self.cleaned_data.get("date_to")
        if isinstance(value, str):
            try:
                return datetime.strptime(value, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                raise forms.ValidationError("Ngày không hợp lệ.")
        return value


class OrderEditForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "customer_name", "customer_email", "phone",
            "shipping_address", "note", "bank_code",
        ]

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "")
        if phone and not re.fullmatch(r"[0-9]{9,15}", phone):
            raise forms.ValidationError("Số điện thoại không hợp lệ, vui lòng chỉ nhập số từ 9 đến 15 chữ số.")
        return phone

    def clean(self):
        cleaned_data = super().clean()
        bank_code = cleaned_data.get("bank_code")
        if bank_code and bank_code not in BANKS:
            cleaned_data["bank_code"] = "VCB"
        return cleaned_data


class OrderLookupForm(forms.Form):
    order_id = forms.IntegerField(label="Mã đơn hàng", min_value=1)
    phone = forms.CharField(label="Số điện thoại", max_length=20)

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "")
        if not re.fullmatch(r"[0-9]{9,15}", phone):
            raise forms.ValidationError("Số điện thoại không hợp lệ.")
        return phone
