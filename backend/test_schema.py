import os
import django
from django.test import Client

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

client = Client()
response = client.get("/api/schema/")
print(f"Schema Status: {response.status_code}")
print(f"Content-Type: {response.get('Content-Type')}")
print(f"Content length: {len(response.content)}")
response = client.get("/api/docs/")
print(f"Swagger Status: {response.status_code}")
response = client.get("/api/redoc/")
print(f"Redoc Status: {response.status_code}")
