import os
import django
from drf_spectacular.views import SpectacularAPIView
from django.test import RequestFactory

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

factory = RequestFactory()
request = factory.get("/api/schema/")
request.META["HTTP_HOST"] = "testserver"
view = SpectacularAPIView.as_view()
response = view(request)
response.render()
print(f"Status: {response.status_code}")
print(f"Content-Type: {response.get('Content-Type')}")
print(f"Raw content: {response.content[:500]}")
