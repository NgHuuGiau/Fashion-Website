from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from products.models import Category
from users.test_client import VerifiedStaffClient
from .admin_forms import (
    CouponForm,
    OrderEditForm,
    OrderSearchForm,
    OrderStatusForm,
    ProductForm,
)
from .models import Coupon, Order


class AdminFormsTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Ao", slug="ao")

    def test_product_form_valid(self):
        form = ProductForm(
            data={
                "name": "Ao test",
                "category": self.category.id,
                "slug": "ao-test",
                "price": 500000,
                "available": True,
            }
        )
        self.assertTrue(form.is_valid())

    def test_product_form_invalid_price(self):
        form = ProductForm(
            data={
                "name": "Ao invalid",
                "category": self.category.id,
                "slug": "ao-invalid",
                "price": 0,
                "available": True,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("Giá sản phẩm phải lớn hơn 0.", form.errors["price"])

    def test_coupon_form_valid(self):
        form = CouponForm(
            data={
                "code": "TEST10",
                "discount_type": "percent",
                "value": 10,
                "min_order_amount": 100000,
                "is_active": True,
                "used_count": 0,
            }
        )
        self.assertTrue(form.is_valid())

    def test_coupon_form_invalid_dates(self):
        form = CouponForm(
            data={
                "code": "DATES",
                "discount_type": "percent",
                "value": 10,
                "min_order_amount": 0,
                "is_active": True,
                "used_count": 0,
                "starts_at": "2025-01-01",
                "ends_at": "2024-01-01",
            }
        )
        self.assertFalse(form.is_valid())

    def test_coupon_form_gift_requires_product(self):
        form = CouponForm(
            data={
                "code": "GIFT1",
                "discount_type": "gift",
                "value": 0,
                "min_order_amount": 500000,
                "is_active": True,
                "used_count": 0,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("Quà tặng", str(form.errors))

    def test_order_status_form_valid(self):
        form = OrderStatusForm(data={"status": "shipping", "is_paid": False})
        self.assertTrue(form.is_valid())

    def test_order_status_form_delivered_requires_paid(self):
        form = OrderStatusForm(data={"status": "delivered", "is_paid": False})
        self.assertFalse(form.is_valid())

    def test_order_search_form_valid(self):
        form = OrderSearchForm(data={"q": "test", "status": "pending"})
        self.assertTrue(form.is_valid())


class CsvExportTest(TestCase):
    client_class = VerifiedStaffClient

    def setUp(self):

        self.staff = User.objects.create_user(
            username="admin", password="admin123!", is_staff=True
        )
        self.user = User.objects.create_user(username="customer", password="pass123!")
        from .models import Order

        Order.objects.create(
            user=self.user,
            customer_name="Test",
            customer_email="t@t.com",
            phone="0909",
            shipping_address="HCM",
            payment_method="cod",
            total_amount=200000,
            subtotal_amount=200000,
            shipping_fee=30000,
            discount_amount=0,
            status="pending",
            is_paid=False,
        )

    def test_export_requires_staff(self):
        self.client.login(username="customer", password="pass123!")
        response = self.client.get(reverse("orders:admin_export_orders"))
        self.assertEqual(response.status_code, 404)

    def test_export_returns_csv(self):
        self.client.login(username="admin", password="admin123!")
        response = self.client.get(reverse("orders:admin_export_orders"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8-sig")
        self.assertIn("Mã ĐH", response.content.decode("utf-8-sig"))
        self.assertIn("Test", response.content.decode("utf-8-sig"))

    def test_export_filters_by_status(self):
        self.client.login(username="admin", password="admin123!")

        Order.objects.create(
            user=self.user,
            customer_name="Shipped",
            customer_email="s@t.com",
            phone="0909",
            shipping_address="HCM",
            payment_method="cod",
            total_amount=100000,
            status="shipping",
            is_paid=False,
        )
        response = self.client.get(
            reverse("orders:admin_export_orders"), {"status": "shipping"}
        )
        self.assertIn("Shipped", response.content.decode("utf-8-sig"))


class AdminDashboardFormIntegrationTest(TestCase):
    client_class = VerifiedStaffClient

    def setUp(self):

        self.staff = User.objects.create_user(
            username="staff", password="pass123!", is_staff=True
        )
        self.admin = User.objects.create_superuser(
            username="admin", password="pass123!"
        )
        from .models import Coupon

        self.coupon = Coupon.objects.create(
            code="TEST10",
            discount_type="percent",
            value=10,
            min_order_amount=100000,
            is_active=True,
        )

    def test_dashboard_save_coupon_uses_coupon_form(self):
        self.client.login(username="admin", password="pass123!")
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {
                "action": "save_coupon",
                "code": "NEW20",
                "discount_type": "percent",
                "value": "20",
                "min_order_amount": "50000",
                "is_active": "on",
                "used_count": "0",
            },
        )
        self.assertEqual(response.status_code, 302)

        self.assertTrue(Coupon.objects.filter(code="NEW20", value=20).exists())

    def test_dashboard_coupon_form_invalid_shows_error(self):
        self.client.login(username="admin", password="pass123!")
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {
                "action": "save_coupon",
                "code": "",
                "discount_type": "percent",
                "value": "-5",
                "min_order_amount": "0",
                "is_active": "on",
            },
        )
        self.assertEqual(response.status_code, 302)

    def test_dashboard_save_coupon_denied_for_staff(self):
        self.client.login(username="staff", password="pass123!")
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {
                "action": "save_coupon",
                "code": "STAFFNO",
                "discount_type": "percent",
                "value": "20",
                "min_order_amount": "50000",
                "is_active": "on",
            },
        )
        self.assertEqual(response.status_code, 302)

        self.assertFalse(Coupon.objects.filter(code="STAFFNO").exists())

    def test_dashboard_delete_coupon_denied_for_staff(self):
        self.client.login(username="staff", password="pass123!")
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {"action": "delete_coupon", "coupon_id": self.coupon.id},
        )
        self.assertEqual(response.status_code, 302)

        self.assertTrue(Coupon.objects.filter(id=self.coupon.id).exists())

    def test_dashboard_update_order_status_uses_order_status_form(self):
        self.client.login(username="staff", password="pass123!")

        order = Order.objects.create(
            user=self.staff,
            customer_name="Test",
            phone="0909",
            shipping_address="HCM",
            payment_method="cod",
            total_amount=100000,
            status="pending",
            is_paid=False,
        )
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {
                "action": "update_order_status",
                "order_id": order.id,
                "new_status": "shipping",
            },
        )
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.status, "shipping")

    def test_dashboard_delivered_requires_paid(self):
        self.client.login(username="staff", password="pass123!")

        order = Order.objects.create(
            user=self.staff,
            customer_name="Test",
            phone="0909",
            shipping_address="HCM",
            payment_method="cod",
            total_amount=100000,
            status="shipping",
            is_paid=False,
        )
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {
                "action": "update_order_status",
                "order_id": order.id,
                "new_status": "delivered",
            },
        )
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.status, "shipping")


class AdminFormsEdgeTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Ao", slug="ao")

    def test_product_form_empty_name_invalid(self):
        form = ProductForm(
            data={"name": "  ", "category": self.category.id, "price": 100000}
        )
        self.assertFalse(form.is_valid())

    def test_variant_formset_validation_errors(self):
        from django import forms
        from django.http import QueryDict
        from .admin_forms import ProductVariantFormSet

        data = QueryDict(
            "variant_row_key[]=row-1&variant_row_key[]=row-2"
            "&variant_color_name[]=Do&variant_color_name[]="
            "&variant_size[]=M&variant_size[]="
            "&variant_stock[]=3&variant_stock[]=abc"
        )
        with self.assertRaises(forms.ValidationError) as ctx:
            ProductVariantFormSet.validate_variants(data)
        errors = str(ctx.exception)
        self.assertIn("thiếu size", errors)
        self.assertIn("Tồn kho biến thể ở dòng 2", errors)

    def test_variant_formset_valid(self):
        from django.http import QueryDict
        from .admin_forms import ProductVariantFormSet

        data = QueryDict(
            "variant_row_key[]=row-1"
            "&variant_color_name[]=Den"
            "&variant_color_code[]=#111111"
            "&variant_size[]=L"
            "&variant_stock[]=5"
            "&variant_is_active[]=row-1"
        )
        cleaned = ProductVariantFormSet.validate_variants(data)
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned[0]["stock"], 5)
        self.assertTrue(cleaned[0]["is_active"])

    def test_variant_formset_skips_empty_rows(self):
        from django.http import QueryDict
        from .admin_forms import ProductVariantFormSet

        data = QueryDict(
            "variant_row_key[]=row-1&variant_row_key[]=row-2"
            "&variant_color_name[]=Den&variant_color_name[]="
            "&variant_size[]=L&variant_size[]="
            "&variant_stock[]=&variant_stock[]="
        )
        cleaned = ProductVariantFormSet.validate_variants(data)
        self.assertEqual(len(cleaned), 1)

    def test_order_search_form_invalid_dates(self):
        from .admin_forms import OrderSearchForm

        form = OrderSearchForm(data={"date_from": "not-a-date", "date_to": "also-bad"})
        self.assertFalse(form.is_valid())

    def test_order_edit_form_does_not_expose_shop_bank(self):

        form = OrderEditForm(
            data={
                "customer_name": "T",
                "customer_email": "",
                "phone": "0912345678",
                "shipping_address": "HCM",
                "bank_code": "UNKNOWN",
            }
        )
        self.assertTrue(form.is_valid())
        self.assertNotIn("bank_code", form.fields)
