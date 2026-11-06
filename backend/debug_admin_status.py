import sys
import requests
import re

sys.stdout.reconfigure(encoding="utf-8")

# Login as admin first
s = requests.Session()
BASE = "http://localhost:8000"

# Get CSRF
resp = s.get(f"{BASE}/dang-nhap/", headers={"X-Forwarded-For": "198.18.200.50"})
csrf_match = re.search(r'name="csrfmiddlewaretoken"\s+value="([^"]+)"', resp.text)
csrf_token = csrf_match.group(1) if csrf_match else s.cookies.get("csrftoken")

# Login as admin (admin/admin123 from prepare_e2e.py)
resp = s.post(
    f"{BASE}/dang-nhap/",
    data={
        "username": "admin",
        "password": "admin123",
        "csrfmiddlewaretoken": csrf_token,
    },
    headers={"X-Forwarded-For": "198.18.200.50"},
    allow_redirects=False,
)
print("Admin login status:", resp.status_code)
print("Location:", resp.headers.get("Location", "N/A"))

# Now go to admin dashboard and find an order to update
resp = s.get(f"{BASE}/admin-dashboard/", headers={"X-Forwarded-For": "198.18.200.50"})
print("\nAdmin dashboard status:", resp.status_code)

# Find order update form
form_match = re.search(r'action="([^"]*admin-dashboard[^"]*)"', resp.text)
if form_match:
    print("Admin form action:", form_match.group(1)[:100])

# Find order IDs
order_ids = re.findall(r'order_id["\s:=]+(\d+)', resp.text)
print("Order IDs found:", order_ids[:5])
