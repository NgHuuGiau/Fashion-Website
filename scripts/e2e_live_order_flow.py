"""Live E2E: mua hang -> nhan vien xu ly don -> doi/tra, huy, hoan, mua lai."""

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
sys.path.insert(0, os.path.join(ROOT, "backend"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.test_settings_sqlite")

import django

django.setup()

from django.contrib.auth.models import User

results = []


def check(name, cond, detail=""):
    results.append(("PASS" if cond else "FAIL", name, detail))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}  {detail}", flush=True)
    return bool(cond)


def db(sql, args=()):
    con = sqlite3.connect(DB)
    try:
        return con.execute(sql, args).fetchall()
    finally:
        con.close()


def csrf(html):
    m = re.search(r'name="csrfmiddlewaretoken"\s+value="([^"]+)"', html)
    return m.group(1) if m else ""


def messages_of(html):
    m = re.search(r'id="messages-data"[^>]*>(.*?)</div>', html, re.DOTALL)
    if not m:
        return []
    try:
        return [x.get("text", "") for x in json.loads(m.group(1))]
    except Exception:  # noqa: BLE001 - JSON hỏng thì coi như không có message
        return []


def totp(key_hex):
    key = bytes.fromhex(key_hex)
    d = hmac.new(key, struct.pack(">Q", int(time.time()) // 30), hashlib.sha1).digest()
    o = d[19] & 0x0F
    return f"{(struct.unpack('>I', d[o:o + 4])[0] & 0x7FFFFFFF) % 1000000:06d}"


class Web:
    def __init__(self, ip):
        self.s = requests.Session()
        self.ip = ip
        self.token = ""
        self.page = BASE + "/"

    def _h(self):
        return {"X-Forwarded-For": self.ip, "Referer": self.page}

    def get(self, path, **kw):
        r = self.s.get(BASE + path, headers=self._h(), timeout=30, **kw)
        self.page = r.url
        self.token = csrf(r.text) or self.token
        return r

    def post(self, path, data):
        payload = dict(data)
        payload.setdefault("csrfmiddlewaretoken", self.token)
        r = self.s.post(
            BASE + path, data=payload, headers=self._h(), timeout=30
        )
        self.page = r.url
        self.token = csrf(r.text) or self.token
        return r

    def login(self, username, password):
        self.get("/dang-nhap/")
        return self.post("/dang-nhap/", {"username": username, "password": password})

    def msgs(self, r):
        return messages_of(r.text)

    def has(self, r, needle):
        return any(needle.lower() in m.lower() for m in self.msgs(r))


def staff_session():
    w = Web("203.0.113.240")
    w.login("codexstaff", "staff123")
    r = w.get("/admin/")
    if "/bao-mat-2-lop/ma/" in r.url:
        uid = db("select id from auth_user where username='codexstaff'")[0][0]
        key = db(
            "select key from otp_totp_totpdevice where user_id=? and confirmed=1 "
            "order by id desc limit 1",
            (uid,),
        )[0][0]
        w.get("/tai-khoan/bao-mat-2-lop/ma/")
        time.sleep(31 - time.time() % 30)  # mã TOTP không dùng lại được trong cùng cửa sổ 30s
        r = w.post("/tai-khoan/bao-mat-2-lop/ma/", {"code": totp(key)})
        w.get("/admin/")
    return w


def set_status(w, order_id, status, paid=False):
    data = {"action": "update_order_status", "order_id": str(order_id), "new_status": status}
    if paid:
        data["is_paid"] = "on"
    return w.post("/admin-dashboard/", data)


# ------------------------------------------------------------------ fixtures
User.objects.filter(username="flowuser").delete()
user = User.objects.create_user(
    username="flowuser", password="FlowTest123!", email="flowuser@test.com"
)
pid, price, vid = db(
    "select p.id, p.price, v.id from products_product p "
    "join products_productvariant v on v.product_id=p.id "
    "where p.available=1 and v.is_active=1 and v.stock>=10 limit 1"
)[0]

u = Web("203.0.113.230")
r = u.login("flowuser", "FlowTest123!")
check("F1 đăng nhập khách hàng", "/dang-nhap/" not in r.url, r.url)


def place_order(coupon="", qty=2, phone="0912345678"):
    u.post(f"/gio-hang/them/{pid}/", {"quantity": str(qty), "variant_id": str(vid)})
    u.get("/thanh-toan/")
    data = {
        "customer_name": "Flow Tester",
        "customer_email": "flowuser@test.com",
        "phone": phone,
        "shipping_address": "12 Lê Lợi, Quận 1, TP.HCM",
        "payment_method": "cod",
        "note": "Giao giờ hành chính",
        "delivery_time_slot": "morning",
        "gift_wrap": "on",
        "gift_note": "Chúc mừng sinh nhật",
    }
    if coupon:
        data["coupon_code"] = coupon
    return u.post("/thanh-toan/", data)


stock0 = db("select stock from products_productvariant where id=?", (vid,))[0][0]
r = place_order(coupon="GIAM50K")
m = re.search(r"/dat-hang-thanh-cong/(\d+)/", r.url)
check("F2 đặt hàng COD + mã giảm giá", bool(m), r.url)
oid = int(m.group(1))
row = db(
    "select status, is_paid, subtotal_amount, discount_amount, total_amount, coupon_code "
    "from orders_order where id=?",
    (oid,),
)[0]
check(
    "F3 đơn tạo đúng: pending, chưa thanh toán, có giảm giá",
    row[0] == "pending" and row[1] == 0 and float(row[3]) == 50000.0 and row[5] == "GIAM50K",
    str(row),
)
stock1 = db("select stock from products_productvariant where id=?", (vid,))[0][0]
check("F4 tồn kho trừ đúng 2", stock1 == stock0 - 2, f"{stock0} -> {stock1}")

r = u.post("/tra-cuu-don/", {"order_id": str(oid), "phone": "0912345678"})
check("F5 tra cứu đơn bằng mã + SĐT", f"#{oid}" in r.text and "Chờ xử lý" in r.text, r.url)

s = staff_session()
check("F6 nhân viên đăng nhập + 2FA", "/admin/" in s.page, s.page)

r = set_status(s, oid, "processing")
check("F7 NV: pending -> Đang xử lý", s.has(r, "chuyển sang trạng thái"), "|".join(s.msgs(r))[:80])

r = set_status(s, oid, "shipping")
check("F8 NV: -> Đang giao", s.has(r, "chuyển sang trạng thái"), "|".join(s.msgs(r))[:80])

r = set_status(s, oid, "delivered")
check(
    "F9 NV: không thể hoàn thành đơn chưa thanh toán",
    s.has(r, "phải được đánh dấu là đã thanh toán"),
    "|".join(s.msgs(r))[:90],
)

r = set_status(s, oid, "delivered", paid=True)
check("F10 NV: hoàn thành đơn + xác nhận đã thu tiền", s.has(r, "chuyển sang trạng thái"), "|".join(s.msgs(r))[:90])
row = db("select status, is_paid from orders_order where id=?", (oid,))[0]
check("F11 DB: đơn delivered + is_paid", row == ("delivered", 1), str(row))

r = s.post("/admin-dashboard/", {"action": "refund_order", "order_id": str(oid)})
check(
    "F12 NV: không hoàn tiền đơn đã thanh toán (đúng quy trình)",
    s.has(r, "đã thanh toán"),
    "|".join(s.msgs(r))[:90],
)

r = u.post(f"/don-hang/{oid}/doi-tra/", {
    "return_type": "refund",
    "reason": "wrong_size",
    "item_ids": [str(db("select id from orders_orderitem where order_id=? limit 1", (oid,))[0][0])],
})
rr = db("select status, return_type, reason, refund_amount from orders_returnrequest where order_id=?", (oid,))
check("F13 khách tạo yêu cầu đổi/trả", bool(rr), str(rr))

# ------------------------------------------------------------------ huy don
r = place_order()
oid2 = int(re.search(r"/dat-hang-thanh-cong/(\d+)/", r.url).group(1))
stock_before_cancel = db("select stock from products_productvariant where id=?", (vid,))[0][0]
r = u.post(f"/don-hang/{oid2}/huy/", {})
row = db("select status from orders_order where id=?", (oid2,))[0]
stock_after_cancel = db("select stock from products_productvariant where id=?", (vid,))[0][0]
check(
    "F14 khách tự huỷ đơn chưa thanh toán + hoàn kho",
    row[0] == "cancelled" and stock_after_cancel == stock_before_cancel + 2,
    f"{row[0]} {stock_before_cancel}->{stock_after_cancel}",
)

r = u.post(f"/don-hang/{oid2}/huy/", {})
check("F15 huỷ lần 2 bị từ chối", u.has(r, "Không thể huỷ"), "|".join(u.msgs(r))[:80])

# ------------------------------------------------------------------ NV hoan don chua thanh toan
r = place_order()
oid3 = int(re.search(r"/dat-hang-thanh-cong/(\d+)/", r.url).group(1))
stock_before_refund = db("select stock from products_productvariant where id=?", (vid,))[0][0]
r = s.post("/admin-dashboard/", {"action": "refund_order", "order_id": str(oid3)})
row = db("select status from orders_order where id=?", (oid3,))[0]
stock_after_refund = db("select stock from products_productvariant where id=?", (vid,))[0][0]
check(
    "F16 NV hoàn/huỷ đơn chưa thanh toán + trả kho",
    s.has(r, "trả hàng về kho") and row[0] == "cancelled"
    and stock_after_refund == stock_before_refund + 2,
    f"{row[0]} {stock_before_refund}->{stock_after_refund}",
)

# ------------------------------------------------------------------ mua lai
r = u.post(f"/don-hang/{oid}/mua-lai/", {})
cart = u.get("/gio-hang/")
pname = db("select name from products_product where id=?", (pid,))[0][0]
check("F17 mua lại đơn cũ -> có hàng trong giỏ", pname in cart.text, r.url)
u.post("/gio-hang/xoa-tat-ca/", {})

# ------------------------------------------------------------------ cleanup
from django.db.models import Sum
from orders.models import Order
from products.models import Product, ProductVariant

Order.objects.filter(customer_name="Flow Tester").delete()
User.objects.filter(username="flowuser").delete()
# Trả kho về như trước khi test để chạy lại nhiều lần không rút cạn tồn kho.
ProductVariant.objects.filter(id=vid).update(stock=stock0)
Product.objects.filter(id=pid).update(
    stock=ProductVariant.objects.filter(product_id=pid, is_active=True).aggregate(
        total=Sum("stock")
    )["total"]
    or 0
)

fails = [x for x in results if x[0] == "FAIL"]
print(f"\n{len(results) - len(fails)}/{len(results)} PASS, {len(fails)} FAIL")
sys.exit(1 if fails else 0)
