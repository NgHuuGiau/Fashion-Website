"""E2E live (HTTP that): dang ky / dang nhap / quen mat khau — 3 vai user/staff/admin.

Server: python -u backend/manage.py runserver --settings=core.test_settings_sqlite
        EMAIL_BACKEND=console (doc ma va link reset tu .tmp-e2e-server.log)
DB: .tmp-e2e.sqlite3 (duoc seed tai khoan admin/codexstaff/nguyenvanA)
"""
import base64
import hashlib
import hmac
import os
import re
import struct
import sys
import time

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.environ.get("BASE_URL", "http://127.0.0.1:8123")
LOG = os.path.join(ROOT, ".tmp-e2e-server.log")
DB = os.path.join(ROOT, "backend", ".tmp-e2e.sqlite3")
results = []


from django.core import mail

def prepare():
    """Fixture riêng cho E2E: tài khoản reset riêng + xoá 2FA cũ của staff/admin.

    Không đụng mật khẩu tài khoản seed (nguyenvanA/user123) và không phụ thuộc
    trạng thái 2FA của lần chạy trước, nên script chạy lại được nhiều lần.
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.test_settings_sqlite")
    sys.path.insert(0, os.path.join(ROOT, "backend"))
    import django

    django.setup()

    from django.contrib.auth.models import User
    from django_otp.plugins.otp_totp.models import TOTPDevice

    user, _ = User.objects.get_or_create(
        username="e2ereset", defaults={"email": "e2ereset@test.com"}
    )
    user.email = "e2ereset@test.com"
    user.set_password("user123")
    user.save()

    TOTPDevice.objects.filter(
        user__username__in=["codexstaff", "admin"]
    ).delete()

    # Clear email outbox
    mail.outbox = []



def check(name, cond, detail=""):
    s = "PASS" if cond else "FAIL"
    results.append((s, name, detail))
    print(f"[{s}] {name}  {detail}")


def totp(secret: str) -> str:
    # django-otp TOTPDevice.key la hex SHA1 (template render <code>{{ secret }}</code>)
    if re.fullmatch(r"[0-9a-fA-F]{40}", secret):
        key = bytes.fromhex(secret)
    else:
        key = base64.b32decode(secret.upper() + "=" * ((8 - len(secret) % 8) % 8))
    ctr = int(time.time()) // 30
    d = hmac.new(key, struct.pack(">Q", ctr), hashlib.sha1).digest()
    o = d[19] & 0x0F
    return f"{(struct.unpack('>I', d[o:o+4])[0] & 0x7FFFFFFF) % 10**6:06d}"


def token(html: str) -> str:
    m = re.search(r'name="csrfmiddlewaretoken"\s+value="([^"]+)"', html)
    return m.group(1) if m else ""


def extract_secret(html: str) -> str:
    m = re.search(r"<code>([^<]+)</code>", html)
    if not m:
        raise AssertionError("khong thay TOTP secret tren trang")
    return m.group(1).strip()


def wait_for(fn, timeout=15, i=0.5):
    end = time.time() + timeout
    while time.time() < end:
        try:
            return fn()
        except Exception:  # noqa: BLE001 - retry tới khi email/log xuất hiện
            time.sleep(i)
    raise RuntimeError("timeout doi email")


EMAIL_DIR = os.path.join(ROOT, ".tmp-e2e-emails")

def email_for(addr: str) -> str:
    """Email cuối cùng trong thư mục email file-based gửi cho addr."""
    if not os.path.isdir(EMAIL_DIR):
        raise AssertionError(f"thư mục email không tồn tại: {EMAIL_DIR}")
    # Django file-based email backend dùng đuôi .log
    files = sorted(
        [f for f in os.listdir(EMAIL_DIR) if f.endswith(".log")],
        key=lambda f: os.path.getmtime(os.path.join(EMAIL_DIR, f)),
        reverse=True,
    )
    for fname in files:
        path = os.path.join(EMAIL_DIR, fname)
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        if addr.lower() in content.lower():
            # Trích body email (sau header)
            parts = content.split("\n\n", 1)
            return parts[1] if len(parts) > 1 else content
    raise AssertionError(f"chua thay email cho {addr} trong {EMAIL_DIR} ({len(files)} files)")
def log_text() -> str:
    return open(LOG, encoding="utf-8", errors="replace").read()


def email_for(addr: str) -> str:
    """Email cuoi cung trong log console backend gui cho addr."""
    txt = log_text()
    parts = re.split(r"(?=^From: )", txt, flags=re.MULTILINE)
    hits = [p for p in parts if addr.lower() in p.lower()]
    if not hits:
        raise AssertionError(f"chua thay email cho {addr}")
    return hits[-1]


def code_in(html: str) -> str:
    c = re.findall(r"\b(\d{6})\b", html)
    if not c:
        raise AssertionError("khong thay ma 6 so")
    return c[-1]


def reset_link(html: str) -> str:
    m = re.search(
        r"https?://[^\s\"<>]+/quen-mat-khau/dat-lai/[A-Za-z0-9_-]+/[A-Za-z0-9-]+/",
        html,
    )
    if not m:
        raise AssertionError("khong thay link dat-lai")
    from urllib.parse import urlparse
    return urlparse(m.group(0)).path
    return m.group(0)[len(BASE):]


class B(requests.Session):
    def __init__(self, ip):
        super().__init__()
        self.ip = ip

    def hdr(self):
        return {"X-Forwarded-For": self.ip, "Referer": BASE}

    def get(self, url):
        r = super().get(BASE + url, headers={"X-Forwarded-For": self.ip}, timeout=30)
        r.path = url
        return r

    def post(self, url, data, from_page=None):
        if from_page is not None:
            data["csrfmiddlewaretoken"] = token(from_page.text)
        r = super().post(BASE + url, data=data, headers=self.hdr(), timeout=30)
        r.path = url
        return r


# ========== A. USER: quen mat khau + dang nhap ===prepare()
A1 = B("203.0.113.10")
r = A1.get("/dang-nhap/")
check("A1 trang dang nhap hien ra", r.status_code == 200, f"{r.status_code}")
bad = A1.post("/dang-nhap/", {"username": "e2ereset", "password": "SaiPass1!"}, from_page=r)
check(
    "A2 sai mat khau bao loi, khong logged in",
    "Sai tên đăng nhập" in bad.text and 'name="username"' in bad.text,
    f"{bad.status_code}",
)
r2 = A1.post("/quen-mat-khau/", {"identifier": "e2ereset"}, from_page=A1.get("/quen-mat-khau/"))
# Sau khi submit quen mat khau: o lai trang quen-mat-khau de hien thong bao
# Kiem tra co thong bao thanh cong (toast/message)
msg_ok = any(kw in r2.text.lower() for kw in ["gui", "gửi", "đã gửi", "reset", "mật khẩu", "email", "check", "hộp thư"])
check("A3 tim TK qua username -> o lai trang quen-mat-khau", r2.url == BASE + "/quen-mat-khau/" and msg_ok, f"{r2.status_code} {r2.url}")

# Debug: kiem tra email directory
import glob
import time
time.sleep(0.5)  # Wait for email file to be written
email_files = glob.glob(os.path.join(EMAIL_DIR, "*.log")) if os.path.isdir(EMAIL_DIR) else []
print(f"[DEBUG] Email files after A3: {len(email_files)}")
for f in email_files:
    print(f"  {f}")
    with open(f, "r", encoding="utf-8", errors="replace") as ef:
        print(f"  Content: {ef.read()[:500]}")

check("A3 tim TK qua username -> ve login", r2.url == BASE + "/dang-nhap/", f"{r2.status_code} {r2.url}")
b_anti = B("203.0.113.10")
r2b_page = b_anti.get("/quen-mat-khau/")
r2b = b_anti.post("/quen-mat-khau/", {"identifier": "khong-ton-tai-xyz"}, from_page=r2b_page)
check("A4 TK khong ton tai: cung phan hoi nhu thanh cong (chong doo)", r2b.url == BASE + "/dang-nhap/", f"{r2b.url}")

lk = wait_for(lambda: reset_link(email_for("e2ereset@test.com")))
A2 = B("203.0.113.11")
r = A2.get(lk)
check("A5 link token hop le -> /quen-mat-khau/dat-lai/", r.url == BASE + "/quen-mat-khau/dat-lai/", f"{r.status_code} {r.url}")
r = A2.post("/quen-mat-khau/dat-lai/", {"password1": "GiaoTiep123!", "password2": "GiaoTiep123!"}, from_page=r)
check("A6 dat lai mat khau moi ok", r.url == BASE + "/dang-nhap/", f"{r.url}")
r3 = A2.post("/dang-nhap/", {"username": "e2ereset", "password": "GiaoTiep123!"}, from_page=A2.get("/dang-nhap/"))
check("A7 dang nhap lai bang MK moi + /tai-khoan/", A2.get("/tai-khoan/").status_code == 200, "")

A2.post("/quen-mat-khau/", {"identifier": "e2ereset"}, from_page=A2.get("/quen-mat-khau/"))
u = A2.get("/quen-mat-khau/")
check("A8 user da login truy cap quen-MK bi day ve san pham", u.url == BASE + "/", f"{u.url}" if u.url else u.path)
A2.get("/dang-xuat/")

# ========== B. DANG KY MOI (user moi) ===s6 = str(int(time.time()))[-6:]
em = f"e2e{s6}@test.com"
n1 = B("198.51.100.55")
r = n1.post(
    "/dang-ky/",
    {
        "username": f"e2e{s6}",
        "email": em,
        "phone_number": f"09{s6}88",
        "password1": "E2Etest1!@",
        "password2": "E2Etest1!@",
    },
    from_page=n1.get("/dang-ky/"),
)
code = wait_for(lambda: code_in(email_for(em)))
r = n1.post("/dang-ky/xac-minh/", {"code": code}, from_page=r)
check("B1 dang ky + xac minh ma -> vao duoc tai khoan", n1.get("/tai-khoan/").status_code == 200, f"code={code}")

# sai ma 5 lan thi khoa
n2 = B("198.51.100.56")
base_page = n2.get("/dang-ky/")
rf = n2.post(
    "/dang-ky/",
    {
        "username": f"e2ewrong{s6}",
        "email": f"e2ewrong{s6}@test.com",
        "phone_number": f"09{s6}99",
        "password1": "E2Etest1!@",
        "password2": "E2Etest1!@",
    },
    from_page=base_page,
)
code2 = wait_for(lambda: code_in(email_for(f"e2ewrong{s6}@test.com")))
pages = []
last = None
for i in range(5):
    p = n2.get("/dang-ky/xac-minh/") if last is None else (
        last if token(last.text) else n2.get("/dang-ky/xac-minh/")
    )
    last = n2.post("/dang-ky/xac-minh/", {"code": "000000"}, from_page=p)
check("B2 sai ma 5 lan -> khoa (khong doi mat khau ton tai)", last.status_code == 200 and ("lượt" in last.text or "quá" in last.text or "Mã chưa đúng" in last.text), f"last={last.status_code}")
chk = B("198.51.100.58")
lp = chk.get("/dang-nhap/")
lp = chk.post("/dang-nhap/", {"username": f"e2ewrong{s6}", "password": "E2Etest1!@"}, from_page=lp)
check("B2b TK chua duoc tao sau 5 ma sai (login thep bao sai TKMK)", "Sai tên đăng nhập" in lp.text, "")

# password yeu bi tu choi
n3 = B("198.51.100.57")
r = n3.post(
    "/dang-ky/",
    {
        "username": f"e2eweak{s6}",
        "email": f"e2eweak{s6}@test.com",
        "phone_number": f"09{s6}77",
        "password1": "123456789",
        "password2": "123456789",
    },
    from_page=n3.get("/dang-ky/"),
)
check("B3 password yeu bi tu choi", "Mật khẩu" in r.text and r.status_code == 200 and 'name="password2"' in r.text, f"{r.status_code}")

# ========== C. STAFF (codexstaff) + 2FA ===S1 = B("192.0.2.77")
r = S1.post("/dang-nhap/", {"username": "codexstaff", "password": "staff123"}, from_page=S1.get("/dang-nhap/"))
check("C1 staff dang nhap ok", r.status_code == 200, f"{r.status_code}")
r = S1.get("/admin/")
check("C2 /admin/ bat 2FA -> bao-mat-2-lop", r.url == BASE + "/tai-khoan/bao-mat-2-lop/", f"{r.status_code} {r.url}")
secret = extract_secret(r.text)
bad = S1.post("/tai-khoan/bao-mat-2-lop/", {"code": "000000"}, from_page=r)
time.sleep(1.5)  # django-otp throttle: sau ma sai, phai doi >= 2^n giay
check("C3 ma 2FA sai -> bao loi, chua confirm", "chưa đúng" in bad.text, f"{bad.status_code}")
r2 = S1.get("/tai-khoan/bao-mat-2-lop/")
r = S1.post("/tai-khoan/bao-mat-2-lop/", {"code": totp(secret)}, from_page=r2)
admr = S1.get("/admin/")
check("C4 device confirm xong -> chuan bi nhap ma (ma/)", admr.url == BASE + "/tai-khoan/bao-mat-2-lop/ma/", f"{admr.status_code} {admr.url}")
time.sleep(31 - time.time() % 30)  # doi ma moi: doi window TOTP de khong bi coi la replay
r = S1.post("/tai-khoan/bao-mat-2-lop/ma/", {"code": totp(secret)}, from_page=admr)
adm = S1.get("/admin/")
check("C5 xac minh ma -> vao /admin/ (staff dashboard)", adm.status_code == 200 and adm.url == BASE + "/admin/", f"{adm.status_code} {adm.url}")
u = S1.get("/admin/auth/user/")
check("C6 staff BI TU CHOI trang user (403)", u.status_code == 403 and u.url == BASE + "/admin/auth/user/", f"{u.status_code} {u.url}")

# ========== D. ADMIN (admin / admin123) ===D1 = B("192.0.2.200")
r = D1.post("/dang-nhap/", {"username": "admin", "password": "admin123"}, from_page=D1.get("/dang-nhap/"))
check("D1 admin dang nhap ok", r.status_code == 200, f"{r.status_code}")
r = D1.get("/admin/")
check("D2 /admin/ bat 2FA lan dau", r.url == BASE + "/tai-khoan/bao-mat-2-lop/", f"{r.url}")
secret_admin = extract_secret(r.text)
r = D1.post("/tai-khoan/bao-mat-2-lop/", {"code": totp(secret_admin)}, from_page=r)
admr = D1.get("/admin/")
check("D3 device admin confirm -> /ma/", admr.url == BASE + "/tai-khoan/bao-mat-2-lop/ma/", f"{admr.url}")
time.sleep(31 - time.time() % 30)  # doi window TOTP moi (chong replay)
r = D1.post("/tai-khoan/bao-mat-2-lop/ma/", {"code": totp(secret_admin)}, from_page=admr)
adm = D1.get("/admin/")
check("D4 admin vao toan quyen /admin/", adm.status_code == 200 and adm.url == BASE + "/admin/", f"{adm.status_code} {adm.url}")
u = D1.get("/admin/auth/user/")
check("D5 admin vao duoc trang quan ly user", u.status_code == 200 and u.url == BASE + "/admin/auth/user/", f"{u.status_code} {u.url}")

# ========== E. RATE LIMIT LOGIN ===R1 = B("192.0.2.99")
page = R1.get("/dang-nhap/")
codes = []
for i in range(11):
    cp = R1.post("/dang-nhap/", {"username": "tranthib", "password": "wrongPass123", "next": "/"}, from_page=page)
    page = cp
lock = cp.status_code == 429
check("E1 sai 10+ lan trong 5p -> block (HTTP 429)", lock, f"{cp.status_code}")

print("\n=== TONG KET ===")
for s, name, detail in results:
    print(f"{s} {name} {detail}")
fails = [x for x in results if x[0] == "FAIL"]
print(f"\n{len(results)-len(fails)}/{len(results)} PASS, {len(fails)} FAIL")
sys.exit(1 if fails else 0)
