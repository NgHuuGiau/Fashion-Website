from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from products.models import Category, Product


class PublishDemoCatalogTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Áo", slug="ao")
        self.product = Product.objects.create(
            category=self.category, name="Áo test", slug="ao-test", price=100000
        )

    def test_publishes_products_with_stock_and_variants(self):
        with override_settings(DEBUG=True):
            call_command("publish_demo_catalog", count=1, stock=5, stdout=StringIO())

        self.product.refresh_from_db()
        self.assertTrue(self.product.available)
        self.assertEqual(self.product.stock, 15)
        self.assertEqual(self.product.variants.filter(is_active=True).count(), 3)

    def test_refuses_when_debug_disabled(self):
        with override_settings(DEBUG=False):
            with self.assertRaises(CommandError):
                call_command("publish_demo_catalog", count=1, stdout=StringIO())

        self.product.refresh_from_db()
        self.assertEqual(self.product.variants.count(), 0)
