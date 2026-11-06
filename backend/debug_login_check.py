import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests, re

s = requests.Session()
BASE = "http://localhost:8000"

resp = s.get(f"{BASE}/dang-nhap/")
csrf_match = re.search(r'name="csrfmiddlewaretoken"\s+value="([^"]+)"', resp.text)
csrf_token = csrf_match.group(1) if csrf_match else s.cookies.get("csrftoken")
print("CSRF token:", csrf_token[:20] + "..." if csrf_token else "None")

resp = s.post(f"{BASE}/dang-nhap/", data={
    "username": "nguyenvanA",
    "password": "user123",
    "csrfmiddlewaretoken": csrf_token,
}, allow_redirects=False, headers={"X-Forwarded-For": "198.18.100.1"})
print("POST status:", resp.status_code)
print("Location:", resp.headers.get("Location", "N/A"))
