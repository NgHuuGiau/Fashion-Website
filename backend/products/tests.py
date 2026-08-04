import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Category, Product, ProductVariant, SupportFAQ, WishlistItem



class ProductViewsTest(TestCase):

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


    def test_product_list_page_ok(self):
        response = self.client.get(reverse("products:product_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Áo test")
        self.assertNotContains(response, "Quần test")


    def test_product_list_excludes_unavailable(self):
        response = self.client.get(reverse("products:product_list"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Ẩn test")


    def test_product_list_filter_by_category(self):
        response = self.client.get(reverse("products:product_list"), {"category": "ao"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Áo test")
        self.assertNotContains(response, "Quần test")


    def test_product_list_filter_by_invalid_category_returns_404(self):
        response = self.client.get(reverse("products:product_list"), {"category": "khong-ton-tai"})
        self.assertEqual(response.status_code, 404)


    def test_product_list_keyword_search(self):
        response = self.client.get(reverse("products:product_list"), {"q": "quần"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Quần test")
        self.assertNotContains(response, "Áo test")


    def test_product_list_keyword_search_without_accent_and_case(self):
        response = self.client.get(reverse("products:product_list"), {"q": "AO"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Áo test")
        self.assertNotContains(response, "Quần test")


    def test_product_list_filter_by_price_range(self):
        response = self.client.get(reverse("products:product_list"), {"min_price": "300000", "max_price": "399000"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Áo test")
        self.assertNotContains(response, "Quần test")


    def test_product_list_filter_by_dotted_price_range(self):
        response = self.client.get(reverse("products:product_list"), {"min_price": "300.000", "max_price": "399.000"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Áo test")
        self.assertNotContains(response, "Quần test")


    def test_product_list_sort_price_desc(self):
        response = self.client.get(reverse("products:product_list"), {"sort": "price_desc", "min_price": "1"})
        self.assertEqual(response.status_code, 200)
        products = response.context["products"]
        self.assertGreaterEqual(len(products), 2)
        self.assertEqual(products[0].id, self.product_quan.id)


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


    def test_product_detail_page_ok(self):
        response = self.client.get(
            reverse("products:product_detail", kwargs={"pk": self.product_ao.id, "slug": self.product_ao.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Áo test")


    def test_product_detail_404_when_wrong_slug(self):
        response = self.client.get(
            reverse("products:product_detail", kwargs={"pk": self.product_ao.id, "slug": "sai-slug"})
        )
        self.assertEqual(response.status_code, 404)


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



class WishlistFeatureTest(TestCase):

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


    def test_wishlist_requires_login(self):
        response = self.client.get(reverse("products:wishlist_list"))
        self.assertEqual(response.status_code, 302)


    def test_toggle_wishlist_add_and_remove(self):
        self.client.login(username="wishuser", password="StrongPass123@")

        add_response = self.client.post(reverse("products:wishlist_toggle", kwargs={"product_id": self.product.id}))
        self.assertEqual(add_response.status_code, 302)
        self.assertTrue(WishlistItem.objects.filter(user=self.user, product=self.product).exists())

        remove_response = self.client.post(reverse("products:wishlist_toggle", kwargs={"product_id": self.product.id}))
        self.assertEqual(remove_response.status_code, 302)
        self.assertFalse(WishlistItem.objects.filter(user=self.user, product=self.product).exists())


    def test_wishlist_toggle_get_not_allowed(self):
        self.client.login(username="wishuser", password="StrongPass123@")
        response = self.client.get(reverse("products:wishlist_toggle", kwargs={"product_id": self.product.id}))
        self.assertEqual(response.status_code, 405)


    def test_wishlist_list_shows_items(self):
        WishlistItem.objects.create(user=self.user, product=self.product)
        self.client.login(username="wishuser", password="StrongPass123@")

        response = self.client.get(reverse("products:wishlist_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Áo wishlist")



class SupportChatApiTest(TestCase):

    def setUp(self):
        SupportFAQ.objects.create(
            question="Bao hanh ra sao?",
            keywords="bao hanh,loi ky thuat",
            answer="Shop ho tro bao hanh loi ky thuat.",
            priority=1,
            is_active=True,
        )


    def test_support_chat_reply_matches_database(self):
        response = self.client.get(reverse("products:support_chat_reply"), {"q": "San pham co bao hanh loi ky thuat khong"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["reply"], "Shop ho tro bao hanh loi ky thuat.")


    def test_support_chat_reply_empty_question_rejected(self):
        response = self.client.get(reverse("products:support_chat_reply"), {"q": ""})
        self.assertEqual(response.status_code, 400)


    def test_support_chat_reply_can_recommend_size(self):
        response = self.client.get(reverse("products:support_chat_reply"), {"q": "Mình cao 1m72 nặng 68kg mặc size gì?"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("size", response.json()["reply"].lower())
        self.assertIn("68kg", response.json()["reply"])


    def test_support_chat_reply_asks_for_missing_weight(self):
        response = self.client.get(reverse("products:support_chat_reply"), {"q": "Mình cao 1m68 mặc size gì?"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("cân nặng", response.json()["reply"].lower())


class SearchSuggestTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(name="Áo", slug="ao")
        Product.objects.create(
            category=self.category,
            name="Áo thun trơn",
            slug="ao-thun-tron",
            price=250000,
            stock=10,
            available=True,
        )
        Product.objects.create(
            category=self.category,
            name="Áo hoodie",
            slug="ao-hoodie",
            price=500000,
            stock=5,
            available=True,
        )
        Product.objects.create(
            category=self.category,
            name="Áo khoác",
            slug="ao-khoac",
            price=800000,
            stock=3,
            available=True,
        )
        Product.objects.create(
            category=self.category,
            name="Quần jeans",
            slug="quan-jeans",
            price=600000,
            stock=0,
            available=False,
        )

    def test_search_suggest_returns_json(self):
        response = self.client.get(reverse("products:search_suggest"), {"q": "hoodie"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        data = response.json()
        self.assertGreaterEqual(len(data), 1)

    def test_search_suggest_excludes_unavailable(self):
        response = self.client.get(reverse("products:search_suggest"), {"q": "jeans"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 0)

    def test_search_suggest_empty_query_returns_empty(self):
        response = self.client.get(reverse("products:search_suggest"), {"q": ""})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_search_suggest_min_length_one_works(self):
        response = self.client.get(reverse("products:search_suggest"), {"q": "h"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(len(data), 1)

    def test_search_suggest_contains_product_details(self):
        response = self.client.get(reverse("products:search_suggest"), {"q": "hoodie"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(len(data), 1)
        self.assertIn("name", data[0])
        self.assertIn("price", data[0])
        self.assertIn("slug", data[0])
        self.assertIn("id", data[0])

    def test_search_suggest_long_query_truncated(self):
        long_q = "a" * 51
        response = self.client.get(reverse("products:search_suggest"), {"q": long_q})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])


class ChatServiceUnitTest(TestCase):

    def test_has_any_keyword_match(self):
        from .services.chat_service import has_any_keyword
        self.assertTrue(has_any_keyword("chao ban", ("chao", "hello")))

    def test_has_any_keyword_no_match(self):
        from .services.chat_service import has_any_keyword
        self.assertFalse(has_any_keyword("goodbye", ("chao", "hello")))

    def test_has_any_keyword_empty_message(self):
        from .services.chat_service import has_any_keyword
        self.assertFalse(has_any_keyword("", ("chao", "hello")))

    def test_extract_height_cm_172cm(self):
        from .services.chat_service import extract_height_cm
        self.assertEqual(extract_height_cm("Tôi cao 172cm"), 172)

    def test_extract_height_cm_1m72(self):
        from .services.chat_service import extract_height_cm
        self.assertEqual(extract_height_cm("Tôi cao 1m72"), 172)

    def test_extract_height_cm_no_match(self):
        from .services.chat_service import extract_height_cm
        self.assertIsNone(extract_height_cm("Tôi cao"))

    def test_extract_weight_kg_68kg(self):
        from .services.chat_service import extract_weight_kg
        self.assertEqual(extract_weight_kg("Tôi nặng 68kg"), 68)

    def test_extract_weight_kg_no_match(self):
        from .services.chat_service import extract_weight_kg
        self.assertIsNone(extract_weight_kg("Tôi nặng"))

    def test_build_size_recommendation_s(self):
        from .services.chat_service import build_size_recommendation
        result = build_size_recommendation(158, 48)
        self.assertIn("S", result)

    def test_build_size_recommendation_m(self):
        from .services.chat_service import build_size_recommendation
        result = build_size_recommendation(165, 58)
        self.assertIn("M", result)

    def test_build_size_recommendation_l(self):
        from .services.chat_service import build_size_recommendation
        result = build_size_recommendation(172, 68)
        self.assertIn("L", result)

    def test_build_size_recommendation_xl(self):
        from .services.chat_service import build_size_recommendation
        result = build_size_recommendation(178, 76)
        self.assertIn("XL", result)

    def test_build_size_recommendation_xxl(self):
        from .services.chat_service import build_size_recommendation
        result = build_size_recommendation(185, 85)
        self.assertIn("XXL", result)

    def test_detect_topic_size(self):
        from .services.chat_service import detect_topic
        self.assertEqual(detect_topic("toi cao 1m72 mac size gi"), "size")

    def test_detect_topic_shipping(self):
        from .services.chat_service import detect_topic
        self.assertEqual(detect_topic("phi ship bao nhieu"), "shipping")

    def test_detect_topic_payment(self):
        from .services.chat_service import detect_topic
        self.assertEqual(detect_topic("thanh toan chuyen khoan duoc khong"), "payment")

    def test_detect_topic_empty(self):
        from .services.chat_service import detect_topic
        self.assertEqual(detect_topic("troi dep qua"), "")

    def test_greeting_reply(self):
        from .services.chat_service import build_greeting_reply
        self.assertIn("Chào bạn", build_greeting_reply())

    def test_thanks_reply(self):
        from .services.chat_service import build_thanks_reply
        self.assertIn("cần chốt size", build_thanks_reply())

    def test_human_support_reply(self):
        from .services.chat_service import build_human_support_reply
        self.assertIn("câu hỏi cụ thể", build_human_support_reply())

    def test_size_support_reply_not_size_topic(self):
        from .services.chat_service import build_size_support_reply
        result = build_size_support_reply("troi dep qua", state={"topic": "style"})
        self.assertIsNone(result)

    def test_size_support_reply_needs_both(self):
        from .services.chat_service import build_size_support_reply
        result = build_size_support_reply("size")
        self.assertIn("gửi theo mẫu", result)

    def test_size_support_reply_only_height(self):
        from .services.chat_service import build_size_support_reply
        result = build_size_support_reply("cao 1m72")
        self.assertIn("cân nặng", result)

    def test_find_support_reply_greeting(self):
        from .services.chat_service import find_support_reply
        result = find_support_reply("Chào shop")
        self.assertIn("Chào bạn", result)

    def test_find_support_reply_thanks(self):
        from .services.chat_service import find_support_reply
        result = find_support_reply("Cảm ơn shop")
        self.assertIn("cần chốt size", result)

    def test_find_support_reply_fallback(self):
        from .services.chat_service import find_support_reply
        result = find_support_reply("abcxyz")
        self.assertIn("hỗ trợ về size", result)


class ProductModelTest(TestCase):

    def setUp(self):
        self.ao_category = Category.objects.create(name="Áo", slug="ao")
        self.pk_category = Category.objects.create(name="Phụ kiện", slug="phu-kien")

        self.product_ao = Product.objects.create(
            category=self.ao_category,
            name="Áo hoodie test",
            slug="ao-hoodie-test",
            price=500000,
            stock=10,
            available=True,
        )
        self.product_pk = Product.objects.create(
            category=self.pk_category,
            name="Mũ test",
            slug="mu-test",
            price=200000,
            stock=5,
            available=True,
        )

    def test_product_requires_variants_true_for_apparel(self):
        self.assertTrue(self.product_ao.requires_variants)

    def test_product_requires_variants_false_for_accessories(self):
        self.assertFalse(self.product_pk.requires_variants)

    def test_product_str_representation(self):
        self.assertEqual(str(self.product_ao), "Áo hoodie test")

    def test_product_requires_variants_for_quan(self):
        quan_category = Category.objects.create(name="Quần", slug="quan")
        product_quan = Product.objects.create(
            category=quan_category,
            name="Quần test",
            slug="quan-test",
            price=300000,
            stock=10,
            available=True,
        )
        self.assertTrue(product_quan.requires_variants)
