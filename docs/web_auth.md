# Đăng nhập, phân quyền người dùng

## Cách đăng nhập

- Username, email hoặc SĐT + mật khẩu tại `/dang-nhap/`.
- Đăng nhập mạng xã hội (Google/Facebook/Apple) chỉ hiện khi đã cấu hình
  `GOOGLE_OAUTH_URL` / `FACEBOOK_OAUTH_URL` / `APPLE_OAUTH_URL` — chưa có thì nút tự ẩn,
  không báo lỗi cho khách.
- Sai 10 lần trong 5 phút → khóa 5 phút (chống brute-force, chung với rate limit login).

## Vai trò

| Vai trò | Quyền |
|---|---|
| Khách (guest) | Mua hàng, tra cứu đơn bằng mã + SĐT |
| User | Đơn của tôi, wishlist, địa chỉ, điểm/hạng, referral |
| Staff (`is_staff`) | Dashboard vận hành theo quyền con (`users/permissions.py`) |
| Admin (`is_superuser`) | Toàn quyền: user/role, coupon, xóa SP |

Phân quyền 2 chiều với SQL Server: đổi role trên Django Admin ↔ cột `[Users].role`
trong SSMS (cài 1 lần: `python manage.py install_role_sync`, xem `docs/database-setup.md`).

## Tài khoản lần đầu

Không có tài khoản mặc định trên web. Tạo admin:

```powershell
cd backend
python manage.py createsuperuser
```

Tài khoản demo (`admin`/`admin123`, `staff1-3`/`staff123`, `user01-15`/`user123`)
chỉ do lệnh `seed_all` tạo ở `DEBUG=True`. Đổi hoặc xóa hết trước khi mở bán.
