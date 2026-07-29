# HUUGIAU Atelier — Website thời trang

![Python](https://img.shields.io/badge/Python_3.10%2B-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django_6.x-092E20?logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-A30000?logo=django&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-ES5-F7DF1E?logo=javascript&logoColor=black)
![Pillow](https://img.shields.io/badge/Pillow-3776AB?logo=python&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?logo=numpy&logoColor=white)
![Requests](https://img.shields.io/badge/Requests-3776AB?logo=python&logoColor=white)
![YAML](https://img.shields.io/badge/YAML-CB171E?logo=yaml&logoColor=white)
![Font Awesome](https://img.shields.io/badge/Font_Awesome_6.5-528DD7?logo=fontawesome&logoColor=white)
![Windows](https://img.shields.io/badge/Windows_11%2B-0078D4?logo=windows&logoColor=white)
![PowerShell](https://img.shields.io/badge/PowerShell_7%2B-5391FE?logo=powershell&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

Website bán thời trang xây dựng bằng Django, giao diện editorial, quản trị đơn giản.

## Yêu cầu hệ thống

- **Python** 3.10+ | **Windows** 11+ | **PowerShell** 7+
- **Django** 6.x | **SQLite** | **DRF**
- **Pillow** | **NumPy** | **Requests** | **YAML**

## Công nghệ

| Layer | Công nghệ |
|-------|-----------|
| Backend | Python 3.10+, Django 6.0, DRF |
| Database | SQLite (dev), sẵn sàng nâng cấp PostgreSQL |
| Frontend | HTML5, CSS3 (3.8K dòng), JavaScript ES5 |
| UI Icons | Font Awesome 6.5 (local + CDN dự phòng) |
| Thanh toán | VietQR (23 ngân hàng) |
| Testing | Django TestCase (70 tests) |
| CI/CD | GitHub Actions (CodeQL + Tests) |
| Export | CSV, JSON |

## Tính năng chính

- **Trang chủ editorial** — hero + sản phẩm nổi bật
- **Danh mục** — lọc theo danh mục, size, màu, giá, sắp xếp, phân trang (12/sp)
- **Chi tiết sản phẩm** — gallery (6 ảnh), biến thể (màu + size), đã xem gần đây, size chart, wishlist
- **Giỏ hàng** — session-based, cập nhật số lượng, coupon, phí ship
- **Thanh toán** — COD hoặc chuyển khoản VietQR, polling trạng thái, tự động hết hạn (15 phút)
- **Tra cứu đơn hàng** — khách vãng lai tra bằng mã đơn + SĐT, hủy đơn + hoàn stock
- **Tìm kiếm** — gợi ý tự động (debounce 250ms, 6 kết quả), không phân biệt dấu
- **Đăng nhập** — bằng email / SĐT / username
- **Support chat** — FAQ, gợi ý size, ngữ cảnh
- **Admin dashboard** — biểu đồ doanh thu 7 ngày, CRUD sản phẩm, gallery, variants, quản lý đơn hàng + coupon, bulk actions, xuất CSV

## Cài đặt nhanh

```powershell
git clone <repo-url> Fashion-Website
cd Fashion-Website
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
cd backend
python manage.py migrate
python manage.py seed_products --sync
python manage.py runserver localhost:8000
```

Hoặc dùng script: `.\scripts\run_local.ps1`

## Cấu trúc thư mục

```
Fashion-Website/
├── backend/           # Django apps
│   ├── core/          # Settings, URL config, utilities
│   ├── orders/        # Cart, checkout, payment, admin
│   ├── products/      # Catalog, product detail, search
│   └── users/         # Auth, profiles, activity
├── frontend/
│   ├── static/        # CSS, JS, fonts, images
│   └── templates/     # 19 templates
├── database/          # SQLite DB + seed data
├── scripts/           # PowerShell helpers
├── docs/              # Hướng dẫn cài đặt & chạy
└── .github/workflows/ # CI/CD pipelines
```

## Testing

```powershell
cd backend
python manage.py test
```

70 tests — tất cả đều pass.

## Ghi chú

- Mặc định dùng SQLite — đặt `DB_PATH` trong `.env` để chuyển database
- SSL/Security tắt ở dev — bật qua `.env` khi production
- Nếu CSS/JS cũ, hard refresh (Ctrl+F5)

## License

MIT — Bản quyền © 2026 HuuGiau
