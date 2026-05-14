from django.test import TestCase
from django.urls import reverse


class SupportChatContextTest(TestCase):
    def test_support_chat_keeps_size_context_between_messages(self):
        first_response = self.client.get(reverse("products:support_chat_reply"), {"q": "Mình cao 1m68 mặc size gì?"})
        self.assertEqual(first_response.status_code, 200)
        self.assertIn("cân nặng", first_response.json()["reply"].lower())

        second_response = self.client.get(reverse("products:support_chat_reply"), {"q": "58kg"})
        self.assertEqual(second_response.status_code, 200)
        self.assertIn("size", second_response.json()["reply"].lower())
        self.assertIn("58kg", second_response.json()["reply"])

    def test_support_chat_handles_greeting_and_follow_up(self):
        greeting_response = self.client.get(reverse("products:support_chat_reply"), {"q": "Chào shop"})
        self.assertEqual(greeting_response.status_code, 200)
        self.assertIn("hỗ trợ", greeting_response.json()["reply"].lower())

        follow_up_response = self.client.get(reverse("products:support_chat_reply"), {"q": "còn hàng không"})
        self.assertEqual(follow_up_response.status_code, 200)
        self.assertIn("tồn kho", follow_up_response.json()["reply"].lower())
