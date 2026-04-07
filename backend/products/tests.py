import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Category, Product, ProductVariant, WishlistItem



# --------------------------------------
# | KHỐI LỚP (CLASS): PRODUCTVIEWSTEST |
# --------------------------------------
class ProductViewsTest(TestCase):

    # -------------------------------
    # | HÀM XỬ LÝ (FUNCTION): SETUP |
    # -------------------------------
    def setUp(self):
        self.ao = Category.objects.create(name="Áo", slug="ao")
        self.quan = Category.objects.create(name="Quần", slug="quan")
        self.pk = Category.objects.create(name="Phụ kiện", slug="phu-kien")

        self.product_ao = Product.objects.create(
            category=self.ao,
            name="Áo test",
            slug="ao-test",
            description="Mô tả áo",
            price=350000,
            stock=20,
            available=True,
            featured=True,
        )
        self.product_quan = Product.objects.create(
            category=self.quan,
            name="Quần test",
            slug="quan-test",
            description="Mô tả quần",
            price=450000,
            stock=10,
            available=True,
        )
        self.product_hidden = Product.objects.create(
            category=self.pk,
            name="Ẩn test",
            slug="an-test",
            description="Không hiển thị",
            price=100000,
            stock=0,
            available=False,
        )

        ProductVariant.objects.create(
            product=self.product_ao,
            color_name="Den",
            color_code="#111111",
            size="M",
            stock=5,
            is_active=True,
        )
        ProductVariant.objects.create(
            product=self.product_ao,
            color_name="Do",
            color_code="#c1121f",
            size="L",
            stock=7,
            is_active=True,
        )


    # ---------------------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): TEST_PRODUCT_LIST_PAGE_OK |
    # ---------------------------------------------------
    def test_product_list_page_ok(self):
        response = self.client.get(reverse("products:product_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Áo test")
        self.assertNotContains(response, "Quần test")


    # ----------------------------------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): TEST_PRODUCT_LIST_EXCLUDES_UNAVAILABLE |
    # ----------------------------------------------------------------
    def test_product_list_excludes_unavailable(self):
        response = self.client.get(reverse("products:product_list"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Ẩn test")


    # --------------------------------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): TEST_PRODUCT_LIST_FILTER_BY_CATEGORY |
    # --------------------------------------------------------------
    def test_product_list_filter_by_category(self):
        response = self.client.get(reverse("products:product_list"), {"category": "ao"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Áo test")
        self.assertNotContains(response, "Quần test")


    # ----------------------------------------------------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): TEST_PRODUCT_LIST_FILTER_BY_INVALID_CATEGORY_RETURNS_404 |
    # ----------------------------------------------------------------------------------
    def test_product_list_filter_by_invalid_category_returns_404(self):
        response = self.client.get(reverse("products:product_list"), {"category": "khong-ton-tai"})
        self.assertEqual(response.status_code, 404)


    # ----------------------------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): TEST_PRODUCT_LIST_KEYWORD_SEARCH |
    # ----------------------------------------------------------
    def test_product_list_keyword_search(self):
        response = self.client.get(reverse("products:product_list"), {"q": "quần"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Quần test")
        self.assertNotContains(response, "Áo test")


    # ----------------------------------------------------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): TEST_PRODUCT_LIST_KEYWORD_SEARCH_WITHOUT_ACCENT_AND_CASE |
    # ----------------------------------------------------------------------------------
    def test_product_list_keyword_search_without_accent_and_case(self):
        response = self.client.get(reverse("products:product_list"), {"q": "AO"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Áo test")
        self.assertNotContains(response, "Quần test")


    # -----------------------------------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): TEST_PRODUCT_LIST_FILTER_BY_PRICE_RANGE |
    # -----------------------------------------------------------------
    def test_product_list_filter_by_price_range(self):
        response = self.client.get(reverse("products:product_list"), {"min_price": "300000", "max_price": "399000"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Áo test")
        self.assertNotContains(response, "Quần test")


    # -----------------------------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): TEST_PRODUCT_LIST_SORT_PRICE_DESC |
    # -----------------------------------------------------------
    def test_product_list_sort_price_desc(self):
        response = self.client.get(reverse("products:product_list"), {"sort": "price_desc", "min_price": "1"})
        self.assertEqual(response.status_code, 200)
        products = response.context["products"]
        self.assertGreaterEqual(len(products), 2)
        self.assertEqual(products[0].id, self.product_quan.id)


    # ------------------------------------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): TEST_PRODUCT_LIST_HAS_PAGINATION_CONTEXT |
    # ------------------------------------------------------------------
    def test_product_list_has_pagination_context(self):
        for i in range(20):
            Product.objects.create(
                category=self.pk,
                name=f"Phu kien {i}",
                slug=f"phu-kien-{i}",
                description="phu kien",
                price=100000 + i,
                stock=10,
                available=True,
            )

        response = self.client.get(reverse("products:product_list"), {"sort": "name_asc", "min_price": "1", "page": 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["products"].number, 2)
        self.assertTrue(response.context["products"].has_previous())


    # -----------------------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): TEST_PRODUCT_DETAIL_PAGE_OK |
    # -----------------------------------------------------
    def test_product_detail_page_ok(self):
        response = self.client.get(
            reverse("products:product_detail", kwargs={"pk": self.product_ao.id, "slug": self.product_ao.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Áo test")


    # -----------------------------------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): TEST_PRODUCT_DETAIL_404_WHEN_WRONG_SLUG |
    # -----------------------------------------------------------------
    def test_product_detail_404_when_wrong_slug(self):
        response = self.client.get(
            reverse("products:product_detail", kwargs={"pk": self.product_ao.id, "slug": "sai-slug"})
        )
        self.assertEqual(response.status_code, 404)


    # ---------------------------------------------------------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): TEST_PRODUCT_DETAIL_CONTEXT_CONTAINS_VARIANT_JSON_AND_DEFAULT |
    # ---------------------------------------------------------------------------------------
    def test_product_detail_context_contains_variant_json_and_default(self):
        response = self.client.get(
            reverse("products:product_detail", kwargs={"pk": self.product_ao.id, "slug": self.product_ao.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["requires_variant"])
        self.assertEqual(response.context["default_color"], "Den")
        self.assertEqual(response.context["default_size"], "M")

        payload = json.loads(response.context["variant_data_json"])
        self.assertGreaterEqual(len(payload), 2)
        self.assertIn("color_name", payload[0])
        self.assertIn("size", payload[0])


    # ------------------------------------------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): TEST_ACCESSORY_DETAIL_DOES_NOT_REQUIRE_VARIANT |
    # ------------------------------------------------------------------------
    def test_accessory_detail_does_not_require_variant(self):
        accessory = Product.objects.create(
            category=self.pk,
            name="Túi test",
            slug="tui-test",
            description="Phụ kiện test",
            price=200000,
            stock=4,
            available=True,
        )
        response = self.client.get(
            reverse("products:product_detail", kwargs={"pk": accessory.id, "slug": accessory.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["requires_variant"])



# -----------------------------------------
# | KHỐI LỚP (CLASS): WISHLISTFEATURETEST |
# -----------------------------------------
class WishlistFeatureTest(TestCase):

    # -------------------------------
    # | HÀM XỬ LÝ (FUNCTION): SETUP |
    # -------------------------------
    def setUp(self):
        self.category = Category.objects.create(name="Áo", slug="ao")
        self.product = Product.objects.create(
            category=self.category,
            name="Áo wishlist",
            slug="ao-wishlist",
            description="wishlist",
            price=320000,
            stock=5,
            available=True,
        )
        self.user = User.objects.create_user(username="wishuser", password="StrongPass123@")


    # ------------------------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): TEST_WISHLIST_REQUIRES_LOGIN |
    # ------------------------------------------------------
    def test_wishlist_requires_login(self):
        response = self.client.get(reverse("products:wishlist_list"))
        self.assertEqual(response.status_code, 302)


    # -------------------------------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): TEST_TOGGLE_WISHLIST_ADD_AND_REMOVE |
    # -------------------------------------------------------------
    def test_toggle_wishlist_add_and_remove(self):
        self.client.login(username="wishuser", password="StrongPass123@")

        add_response = self.client.post(reverse("products:wishlist_toggle", kwargs={"product_id": self.product.id}))
        self.assertEqual(add_response.status_code, 302)
        self.assertTrue(WishlistItem.objects.filter(user=self.user, product=self.product).exists())

        remove_response = self.client.post(reverse("products:wishlist_toggle", kwargs={"product_id": self.product.id}))
        self.assertEqual(remove_response.status_code, 302)
        self.assertFalse(WishlistItem.objects.filter(user=self.user, product=self.product).exists())


    # --------------------------------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): TEST_WISHLIST_TOGGLE_GET_NOT_ALLOWED |
    # --------------------------------------------------------------
    def test_wishlist_toggle_get_not_allowed(self):
        self.client.login(username="wishuser", password="StrongPass123@")
        response = self.client.get(reverse("products:wishlist_toggle", kwargs={"product_id": self.product.id}))
        self.assertEqual(response.status_code, 405)


    # --------------------------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): TEST_WISHLIST_LIST_SHOWS_ITEMS |
    # --------------------------------------------------------
    def test_wishlist_list_shows_items(self):
        WishlistItem.objects.create(user=self.user, product=self.product)
        self.client.login(username="wishuser", password="StrongPass123@")

        response = self.client.get(reverse("products:wishlist_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Áo wishlist")
