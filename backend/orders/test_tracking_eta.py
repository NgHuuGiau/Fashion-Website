from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product

from .models import Order, OrderItem
from .views import estimate_delivery_days


class OrderTrackingEtaTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="buyer_eta", password="StrongPass123!")
        self.other_user = User.objects.create_user(username="other_eta", password="StrongPass123!")
        self.category = Category.objects.create(name="Áo", slug="ao")
        self.product = Product.objects.create(
            category=self.category,
            name="Áo theo dõi",
            slug="ao-theo-doi",
            price=350000,
            stock=10,
            available=True,
        )

    def make_order(self, user, status, address):
        order = Order.objects.create(
            user=user,
            customer_name="Buyer",
            customer_email="buyer@test.com",
            phone="0909000000",
            shipping_address=address,
            payment_method="cod",
            total_amount=350000,
            subtotal_amount=320000,
            shipping_fee=30000,
            status=status,
        )
        OrderItem.objects.create(order=order, product=self.product, quantity=1, price=350000)
        return order

    def test_estimate_delivery_days_by_region(self):
        self.assertEqual(estimate_delivery_days("Quận 1, TP HCM"), 2)
        self.assertEqual(estimate_delivery_days("Dĩ An, Bình Dương"), 3)
        self.assertEqual(estimate_delivery_days("Cầu Giấy, Hà Nội"), 7)
        self.assertEqual(estimate_delivery_days("Đà Nẵng"), 5)

    def test_my_orders_only_shows_logged_in_users_orders_and_prioritizes_shipping(self):
        self.client.login(username="buyer_eta", password="StrongPass123!")
        shipping_order = self.make_order(self.user, "shipping", "Quận 7, TP HCM")
        self.make_order(self.user, "pending", "Đà Nẵng")
        self.make_order(self.other_user, "shipping", "Hà Nội")

        response = self.client.get(reverse("orders:my_orders"))

        self.assertEqual(response.status_code, 200)
        orders = response.context["orders"]
        self.assertEqual(orders[0].id, shipping_order.id)
        self.assertEqual(response.context["active_tracking_order"].id, shipping_order.id)
        self.assertContains(response, "Dự kiến giao")
        self.assertNotContains(response, f"#{Order.objects.filter(user=self.other_user).first().id}")

    def test_order_review_has_eta_context(self):
        self.client.login(username="buyer_eta", password="StrongPass123!")
        order = self.make_order(self.user, "shipping", "Hà Nội")

        response = self.client.get(reverse("orders:order_review", kwargs={"order_id": order.id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["tracking_order"].eta_days, 7)
