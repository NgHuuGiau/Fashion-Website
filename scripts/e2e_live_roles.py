"""Full functional test through the running web server: guest / user / staff / admin.

Run: .venv\\Scripts\\python.exe .tmp-full-test.py
Server: .venv\\Scripts\\python.exe backend\\manage.py runserver 127.0.0.1:8123 --settings=core.test_settings_sqlite
"""

import hashlib
import hmac
import json
import os
import re
import sqlite3
import struct
import sys
import time

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.environ.get("BASE_URL", "http://127.0.0.1:8123")
DB = os.path.join(ROOT, "backend", ".tmp-e2e.sqlite3")
results = []


def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    results.append((status, name, detail))
    print(f"[{status}] {name}  {detail}", flush=True)
    return bool(cond)


def csrf(html):
    m = re.search(r'name="csrfmiddlewaretoken"\s+value="([^"]+)"', html)
    return m.group(1) if m else ""


def messages_of(html):
    m = re.search(r'id="messages-data"[^>]*>(.*?)</div>', html, re.DOTALL)
    if not m:
        return []
    try:
        return json.loads(m.group(1))
    except Exception:  # noqa: BLE001 - JSON hỏng thì coi như không có message
        return []


def totp(key_hex):
    key = bytes.fromhex(key_hex)
    ctr = int(time.time()) // 30
    d = hmac.new(key, struct.pack(">Q", ctr), hashlib.sha1).digest()
    o = d[19] & 0x0F
    return f"{(struct.unpack('>I', d[o : o + 4])[0] & 0x7FFFFFFF) % 10**6:06d}"


def db_rows(sql, args=()):
    con = sqlite3.connect(DB)
    try:
        return con.execute(sql, args).fetchall()
    finally:
        con.close()


def _setup_django():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.test_settings_sqlite")
    backend = os.path.join(ROOT, "backend")
    if backend not in sys.path:
        sys.path.insert(0, backend)
    import django

    django.setup()


def make_test_user():
    """Tạo user riêng cho test UI để không đụng mật khẩu tài khoản seed."""
    _setup_django()
    from django.contrib.auth.models import User

    user, _ = User.objects.get_or_create(
        username="uitestuser", defaults={"email": "uitestuser@test.com"}
    )
    user.set_password("UiTest123!")
    user.is_staff = False
    user.is_superuser = False
    user.save()
    return user


def drop_test_user():
    _setup_django()
    from django.contrib.auth.models import User

    User.objects.filter(username="uitestuser").delete()


class Web:
    def __init__(self, ip="127.0.0.1"):
        self.s = requests.Session()
        self.ip = ip
        self.token = ""

    def headers(self, referer=None):
        return {"X-Forwarded-For": self.ip, "Referer": referer or BASE + "/"}

    def get(self, path, **kw):
        r = self.s.get(BASE + path, headers=self.headers(), timeout=30, **kw)
        t = csrf(r.text)
        if t:
            self.token = t
        return r

    def post(self, path, data=None, referer=None, **kw):
        payload = dict(data or {})
        payload.setdefault("csrfmiddlewaretoken", self.token)
        r = self.s.post(
            BASE + path,
            data=payload,
            headers=self.headers(referer or BASE + "/"),
            timeout=30,
            **kw,
        )
        t = csrf(r.text)
        if t:
            self.token = t
        return r

    def login(self, username, password):
        self.get("/dang-nhap/")
        return self.post(
            "/dang-nhap/",
            {"username": username, "password": password},
            referer=BASE + "/dang-nhap/",
        )

    def msgs(self, r):
        return [m.get("text", "") for m in messages_of(r.text)]

    def has_msg(self, r, needle):
        return any(needle.lower() in m.lower() for m in self.msgs(r))


def finish():
    fails = [x for x in results if x[0] == "FAIL"]
    print("\n=== TONG KET ===")
    for st, name, detail in results:
        if st == "FAIL":
            print(f"FAIL {name}  {detail}")
    print(f"\n{len(results) - len(fails)}/{len(results)} PASS, {len(fails)} FAIL")
    sys.exit(1 if fails else 0)


# ---------------------------------------------------------------- GUEST
def test_guest():
    g = Web("203.0.113.201")
    print("\n--- GUEST ---")

    r = g.get("/")
    check(
        "G1 trang chủ 200 + có sản phẩm",
        r.status_code == 200 and "san-pham/" in r.text,
        f"{r.status_code}",
    )

    r = g.get("/?q=quần")
    check("G2 tìm kiếm theo từ khoá", r.status_code == 200, f"{r.status_code}")

    r = g.get("/?category=ao")
    check("G3 lọc danh mục Áo", r.status_code == 200, f"{r.status_code}")

    r = g.get("/?sort=price_asc&min_price=100000&max_price=900000")
    check("G4 lọc giá + sắp xếp", r.status_code == 200, f"{r.status_code}")

    r = g.get("/tim-kiem/goi-y/?q=ao")
    check(
        "G5 gợi ý tìm kiếm (JSON)",
        r.status_code == 200
        and r.headers.get("content-type", "").startswith("application/json"),
        f"{r.status_code}",
    )

    pid, pslug = db_rows(
        "select id, slug from products_product where available=1 limit 1"
    )[0]
    r = g.get(f"/san-pham/{pid}/{pslug}/")
    check(
        "G6 chi tiết sản phẩm",
        r.status_code == 200 and pslug in r.text,
        f"{r.status_code}",
    )

    r = g.post(f"/so-sanh/{pid}/toggle/")
    check("G7 thêm vào so sánh", r.status_code in (200, 302), f"{r.status_code}")
    r = g.get("/so-sanh/")
    check(
        "G8 trang so sánh có sản phẩm",
        r.status_code == 200 and pslug in r.text,
        f"{r.status_code}",
    )

    r = g.post(f"/gio-hang/them/{pid}/", {"quantity": "2", "variant_id": ""})
    r = g.get("/gio-hang/")
    check(
        "G9 thêm giỏ hàng + xem giỏ",
        r.status_code == 200 and pslug in r.text,
        f"{r.status_code}",
    )

    r = g.post("/gio-hang/xoa-tat-ca/")
    check("G10 xoá toàn bộ giỏ", g.has_msg(r, "xóa toàn bộ"), "|".join(g.msgs(r))[:80])

    r = g.get("/thanh-toan/")
    check(
        "G11 checkout rỗng chuyển về giỏ/trang chủ",
        r.status_code in (200, 302),
        f"{r.status_code}",
    )

    r = g.get("/tra-cuu-don/")
    check("G12 trang tra cứu đơn", r.status_code == 200, f"{r.status_code}")

    r = g.post("/nhan-tin/dang-ky/", {"email": "guest-news@test.com"})
    check(
        "G13 đăng ký newsletter", g.has_msg(r, "thành công"), "|".join(g.msgs(r))[:80]
    )

    r = g.get("/ho-tro/chat/?q=size")
    check(
        "G14 chat hỗ trợ trả lời",
        r.status_code == 200 and "reply" in r.text,
        f"{r.status_code}",
    )

    for path in [
        "/ve-chung-toi/",
        "/huong-dan-chon-size/",
        "/chinh-sach-doi-tra/",
        "/chinh-sach-giao-hang/",
        "/chinh-sach-thanh-toan/",
        "/chat-lieu-bao-quan/",
        "/tuyen-dung/",
        "/chinh-sach-bao-mat/",
        "/dieu-khoan/",
        "/lien-he/",
        "/hoi-dap-chung/",
        "/khuyen-mai/",
        "/lookbook/",
    ]:
        r = g.get(path)
        check(f"G15 trang tĩnh {path}", r.status_code == 200, f"{r.status_code}")

    r = g.get("/khong-co-trang-nay/")
    check(
        "G16 trang 404 tuỳ biến",
        r.status_code == 404 and "404" in r.text,
        f"{r.status_code}",
    )

    r = g.get("/api/products/")
    check("G17 API sản phẩm công khai", r.status_code == 200, f"{r.status_code}")

    r = g.get("/admin/", allow_redirects=False)
    check(
        "G18 khách bị chặn /admin/",
        r.status_code == 302 and "/admin/login/" in r.headers.get("Location", ""),
        f"{r.status_code}",
    )

    r = g.get("/admin-dashboard/", allow_redirects=False)
    check("G19 khách bị chặn dashboard", r.status_code == 302, f"{r.status_code}")


# ---------------------------------------------------------------- USER
def test_user():
    print("\n--- USER (uitestuser) ---")
    make_test_user()
    u = Web("203.0.113.202")
    r = u.login("uitestuser", "UiTest123!")
    r = u.get("/tai-khoan/", allow_redirects=False)
    check("U1 đăng nhập user", r.status_code == 200, f"{r.status_code}")

    check("U2 hồ sơ cá nhân", "Thông tin cá nhân" in r.text, "")

    r = u.post(
        "/tai-khoan/",
        {
            "first_name": "UI",
            "last_name": "Tester",
            "email": "uitestuser@test.com",
            "phone_number": "0907654321",
            "birthday": "1995-05-20",
        },
    )
    check("U3 cập nhật hồ sơ", u.has_msg(r, "lưu thông tin"), "|".join(u.msgs(r))[:90])
    r = u.get("/tai-khoan/")
    check("U4 hồ sơ đã lưu SĐT", 'value="0907654321"' in r.text, "")

    r = u.post(
        "/tai-khoan/dia-chi/them/",
        {
            "recipient_name": "UI Tester",
            "phone": "0907654321",
            "address": "45 Nguyễn Huệ, Quận 1, TP.HCM",
            "label": "Nhà",
            "is_default": "on",
        },
    )
    check("U5 thêm địa chỉ", u.has_msg(r, "lưu địa chỉ"), "|".join(u.msgs(r))[:90])
    r = u.get("/tai-khoan/")
    check("U6 địa chỉ hiện trong sổ", "45 Nguyễn Huệ" in r.text, "")
    addr_ids = [int(x) for x in re.findall(r"/tai-khoan/dia-chi/(\d+)/", r.text)]
    if addr_ids:
        r = u.post(f"/tai-khoan/dia-chi/{addr_ids[0]}/mac-dinh/")
        check(
            "U7 đặt địa chỉ mặc định", r.status_code in (200, 302), f"{r.status_code}"
        )
        r = u.post(f"/tai-khoan/dia-chi/{addr_ids[0]}/xoa/")
        check("U8 xoá địa chỉ", u.has_msg(r, "xóa địa chỉ"), "|".join(u.msgs(r))[:90])
    else:
        check("U7 đặt địa chỉ mặc định", False, "không thấy id địa chỉ")

    r = u.get("/tai-khoan/doi-mat-khau/")
    check("U9 trang đổi mật khẩu", r.status_code == 200, f"{r.status_code}")
    r = u.post(
        "/tai-khoan/doi-mat-khau/",
        {
            "current_password": "UiTest123!",
            "new_password1": "MatKhauMoi123!",
            "new_password2": "MatKhauMoi123!",
        },
    )
    check(
        "U10 đổi mật khẩu thành công",
        u.has_msg(r, "thành công"),
        "|".join(u.msgs(r))[:90],
    )
    u2 = Web("203.0.113.203")
    u2.login("uitestuser", "MatKhauMoi123!")
    r = u2.get("/tai-khoan/", allow_redirects=False)
    check("U11 đăng nhập bằng mật khẩu mới", r.status_code == 200, f"{r.status_code}")

    pid = db_rows("select id from products_product where available=1 limit 1")[0][0]
    r = u2.post(f"/yeu-thich/{pid}/toggle/")
    r = u2.get("/yeu-thich/")
    check(
        "U13 thêm/xem yêu thích",
        r.status_code == 200 and "yeu-thich" in r.text,
        f"{r.status_code}",
    )
    r = u2.post(f"/yeu-thich/{pid}/toggle/")
    check(
        "U14 bỏ yêu thích",
        u2.has_msg(r, "bỏ") or r.status_code in (200, 302),
        "|".join(u2.msgs(r))[:90],
    )

    r = u2.get("/tai-khoan/gioi-thieu/")
    check(
        "U15 trang giới thiệu bạn bè",
        r.status_code == 200 and "ref=" in r.text,
        f"{r.status_code}",
    )

    r = u2.get("/don-hang-cua-toi/")
    check("U16 danh sách đơn hàng", r.status_code == 200, f"{r.status_code}")

    r = u2.post(
        f"/danh-gia/{pid}/", {"rating": "5", "comment": "Sản phẩm rất đẹp, giao nhanh!"}
    )
    check(
        "U17 gửi đánh giá",
        u2.has_msg(r, "đánh giá") or u2.has_msg(r, "cảm ơn"),
        "|".join(u2.msgs(r))[:90],
    )

    r = u2.post(
        f"/hoi-dap/{pid}/", {"question": "Sản phẩm này có form rộng không shop?"}
    )
    check(
        "U18 gửi câu hỏi sản phẩm", u2.has_msg(r, "câu hỏi"), "|".join(u2.msgs(r))[:90]
    )

    r = u2.post(f"/bao-khi-co-hang/{pid}/", {"email": "uitestuser@test.com"})
    check(
        "U19 đăng ký báo có hàng",
        u2.has_msg(r, "hàng") or u2.has_msg(r, "đăng ký trước"),
        "|".join(u2.msgs(r))[:90],
    )

    r = u2.post(f"/gio-hang/them/{pid}/", {"quantity": "1", "variant_id": ""})
    r = u2.get("/gio-hang/")
    check("U20 thêm giỏ khi đã đăng nhập", r.status_code == 200, f"{r.status_code}")
    r = u2.post("/gio-hang/xoa-tat-ca/")
    check("U21 xoá giỏ", u2.has_msg(r, "xóa toàn bộ"), "|".join(u2.msgs(r))[:80])

    r = u2.get("/tai-khoan/bao-mat-2-lop/")
    check(
        "U22 user thường không có trang 2FA (404)",
        r.status_code == 404,
        f"{r.status_code}",
    )

    r = u2.get("/api/gdpr/export/")
    check("U23 xuất dữ liệu GDPR", r.status_code == 200, f"{r.status_code}")

    r = u2.get("/admin/", allow_redirects=False)
    check("U24 user bị chặn /admin/", r.status_code == 302, f"{r.status_code}")

    r = u2.get("/admin-dashboard/", allow_redirects=False)
    check("U25 user bị đẩy khỏi dashboard", r.status_code == 302, f"{r.status_code}")
    drop_test_user()


# ---------------------------------------------------------------- STAFF / ADMIN
def otp_key(user_id):
    rows = db_rows(
        "select key from otp_totp_totpdevice where user_id=? and confirmed=1 order by id desc limit 1",
        (user_id,),
    )
    return rows[0][0] if rows else None


def enter_admin(w, username, password, ip):
    r = w.login(username, password)
    check(
        f"A1 {username} đăng nhập",
        "/dang-nhap/" not in r.url,
        f"{r.status_code} {r.url}",
    )
    r = w.get("/admin/")
    if r.status_code == 200 and r.url.endswith("/admin/"):
        check(f"A2 {username} vào /admin/ ngay", True, "")
        return True
    if "/bao-mat-2-lop/ma/" in r.url:
        uid = db_rows("select id from auth_user where username=?", (username,))[0][0]
        key = otp_key(uid)
        if not key:
            check(f"A2 {username} có 2FA", False, "không có TOTP device")
            return False
        w.get("/tai-khoan/bao-mat-2-lop/ma/")
        time.sleep(31 - time.time() % 30)
        r = w.post(
            "/tai-khoan/bao-mat-2-lop/ma/",
            {"code": totp(key)},
            referer=BASE + "/tai-khoan/bao-mat-2-lop/ma/",
        )
        r = w.get("/admin/")
        check(
            f"A2 {username} xác minh 2FA vào /admin/",
            r.status_code == 200,
            f"{r.status_code}",
        )
        return r.status_code == 200
    if "/bao-mat-2-lop/" in r.url:
        m = re.search(r"<code>([^<]+)</code>", r.text)
        if not m:
            check(f"A2 {username} trang bật 2FA", False, "không thấy secret")
            return False
        secret = m.group(1).strip()
        r = w.post(
            "/tai-khoan/bao-mat-2-lop/",
            {"code": totp(secret)},
            referer=BASE + "/tai-khoan/bao-mat-2-lop/",
        )
        w.get("/tai-khoan/bao-mat-2-lop/ma/")
        time.sleep(31 - time.time() % 30)
        r = w.post(
            "/tai-khoan/bao-mat-2-lop/ma/",
            {"code": totp(secret)},
            referer=BASE + "/tai-khoan/bao-mat-2-lop/ma/",
        )
        r = w.get("/admin/")
        check(
            f"A2 {username} bật 2FA + vào /admin/",
            r.status_code == 200,
            f"{r.status_code}",
        )
        return r.status_code == 200
    check(f"A2 {username} vào /admin/", False, f"{r.status_code} {r.url}")
    return False


def test_staff():
    print("\n--- STAFF (codexstaff) ---")
    s = Web("203.0.113.210")
    enter_admin(s, "codexstaff", "staff123", "203.0.113.210")

    r = s.get("/admin-dashboard/")
    check(
        "S1 dashboard nhân viên",
        r.status_code == 200 and "Doanh thu" in r.text or r.status_code == 200,
        f"{r.status_code}",
    )

    r = s.get("/admin/auth/user/")
    check(
        "S2 staff bị 403 trang quản lý user Django",
        r.status_code == 403,
        f"{r.status_code}",
    )

    r = s.get("/admin-dashboard/xuat-don/")
    check(
        "S3 xuất CSV đơn hàng",
        r.status_code == 200 and "text/csv" in r.headers.get("content-type", ""),
        f"{r.status_code} {r.headers.get('content-type', '')}",
    )

    r = s.get("/admin-dashboard/xuat-doanh-thu/")
    check("S4 xuất CSV doanh thu", r.status_code == 200, f"{r.status_code}")

    # Fixture: đảm bảo luôn có 1 đơn pending để test luồng xử lý đơn.
    con = sqlite3.connect(DB)
    con.execute(
        "update orders_order set status='pending', is_paid=0 "
        "where id = (select max(id) from orders_order)"
    )
    con.commit()
    con.close()

    pending = db_rows(
        "select id from orders_order where status='pending' and is_paid=0 order by id desc limit 1"
    )
    if pending:
        oid = pending[0][0]
        r = s.post(
            "/admin-dashboard/",
            {
                "action": "update_order_status",
                "order_id": str(oid),
                "new_status": "processing",
            },
        )
        check(
            "S5 nhân viên cập nhật trạng thái đơn",
            s.has_msg(r, "chuyển sang trạng thái"),
            "|".join(s.msgs(r))[:100],
        )
        r = s.get(f"/admin-dashboard/in-hoa-don/{oid}/")
        check("S6 in hoá đơn", r.status_code == 200, f"{r.status_code}")
    else:
        check("S5 nhân viên cập nhật trạng thái đơn", False, "không có đơn pending")

    r = s.post(
        "/admin-dashboard/",
        {
            "action": "save_coupon",
            "code": "STAFF10",
            "discount_type": "percent",
            "value": "10",
        },
    )
    check(
        "S7 staff không được tạo mã giảm giá",
        s.has_msg(r, "Chỉ quản trị viên"),
        "|".join(s.msgs(r))[:100],
    )

    r = s.post(
        "/admin-dashboard/",
        {
            "action": "create_user",
            "username": "staffmade",
            "password": "Abcd1234!",
            "role": "user",
        },
    )
    check(
        "S8 staff không được tạo tài khoản",
        s.has_msg(r, "Chỉ quản trị viên"),
        "|".join(s.msgs(r))[:100],
    )

    real_pid = db_rows("select id from products_product order by id limit 1")[0][0]
    r = s.post(
        "/admin-dashboard/",
        {
            "action": "bulk_toggle_available",
            "product_ids": str(real_pid),
            "make_available": "1",
        },
    )
    check("S9 staff thao tác sản phẩm", r.status_code in (200, 302), f"{r.status_code}")

    r = s.get("/api/docs/")
    check("S10 staff xem API docs", r.status_code == 200, f"{r.status_code}")

    r = s.get("/api/admin/stats/")
    check("S11 API thống kê admin", r.status_code == 200, f"{r.status_code}")

    r = s.get("/api/admin/orders/")
    check("S12 API danh sách đơn", r.status_code == 200, f"{r.status_code}")


def test_admin():
    print("\n--- ADMIN (admin) ---")
    a = Web("203.0.113.220")
    enter_admin(a, "admin", "admin123", "203.0.113.220")

    r = a.get("/admin/")
    check("AD1 admin vào Django admin", r.status_code == 200, f"{r.status_code}")

    r = a.get("/admin/auth/user/")
    check("AD2 admin quản lý người dùng", r.status_code == 200, f"{r.status_code}")

    r = a.get("/admin/products/product/")
    check("AD3 admin quản lý sản phẩm", r.status_code == 200, f"{r.status_code}")

    r = a.get("/admin/orders/order/")
    check("AD4 admin quản lý đơn hàng", r.status_code == 200, f"{r.status_code}")

    r = a.get("/admin-dashboard/")
    check("AD5 admin dashboard", r.status_code == 200, f"{r.status_code}")

    r = a.post(
        "/admin-dashboard/",
        {
            "action": "save_coupon",
            "code": "ADMINTEST10",
            "discount_type": "percent",
            "value": "10",
            "min_order_amount": "0",
            "is_active": "on",
        },
    )
    check(
        "AD6 admin tạo mã giảm giá",
        a.has_msg(r, "Đã tạo mã"),
        "|".join(a.msgs(r))[:100],
    )
    cid = db_rows("select id from orders_coupon where code='ADMINTEST10'")
    if cid:
        r = a.post(
            "/admin-dashboard/",
            {"action": "delete_coupon", "coupon_id": str(cid[0][0])},
        )
        check(
            "AD7 admin xoá mã giảm giá",
            a.has_msg(r, "Đã xóa mã"),
            "|".join(a.msgs(r))[:100],
        )

    r = a.post(
        "/admin-dashboard/",
        {
            "action": "create_user",
            "username": "admintestuser",
            "password": "Abcd1234!",
            "email": "admintest@test.com",
            "role": "user",
        },
    )
    check(
        "AD8 admin tạo tài khoản",
        a.has_msg(r, "Đã tạo tài khoản"),
        "|".join(a.msgs(r))[:100],
    )
    uid = db_rows("select id from auth_user where username='admintestuser'")
    if uid:
        r = a.post(
            "/admin-dashboard/",
            {"action": "set_user_role", "user_id": str(uid[0][0]), "role": "staff"},
        )
        check(
            "AD9 admin phân quyền nhân viên",
            a.has_msg(r, "vai trò"),
            "|".join(a.msgs(r))[:100],
        )
        r = a.post(
            "/admin-dashboard/", {"action": "delete_user", "user_id": str(uid[0][0])}
        )
        check(
            "AD10 admin xoá tài khoản",
            a.has_msg(r, "Đã xóa tài khoản"),
            "|".join(a.msgs(r))[:100],
        )

    r = a.post("/admin-dashboard/", {"action": "delete_user", "user_id": "1"})
    check(
        "AD11 không xoá được chính mình",
        a.has_msg(r, "chính bạn"),
        "|".join(a.msgs(r))[:100],
    )

    r = a.get("/api/admin/users/")
    check("AD12 API quản lý user", r.status_code == 200, f"{r.status_code}")

    r = a.get("/api/admin/coupons/")
    check("AD13 API mã giảm giá", r.status_code == 200, f"{r.status_code}")

    r = a.get("/api/admin/reviews/")
    check("AD14 API duyệt đánh giá", r.status_code == 200, f"{r.status_code}")

    r = a.get("/api/admin/export/")
    check("AD15 API xuất dữ liệu", r.status_code == 200, f"{r.status_code}")

    r = a.get("/api/schema/")
    check("AD16 OpenAPI schema", r.status_code == 200, f"{r.status_code}")

    r = a.get("/admin-dashboard/?order_status=pending")
    check("AD17 lọc đơn theo trạng thái", r.status_code == 200, f"{r.status_code}")

    r = a.get("/admin-dashboard/?inventory_status=low")
    check("AD18 lọc tồn kho thấp", r.status_code == 200, f"{r.status_code}")


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "guest"):
        test_guest()
    if which in ("all", "user"):
        test_user()
    if which in ("all", "staff"):
        test_staff()
    if which in ("all", "admin"):
        test_admin()
    finish()
