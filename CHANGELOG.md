# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive CI/CD pipeline with GitHub Actions
- CodeQL security analysis
- Ruff linting and formatting
- MyPy type checking
- Bandit security scanning
- pip-audit and Safety vulnerability scanning
- Pre-commit hooks
- Issue and PR templates
- CODEOWNERS for review assignment
- Security policy
- Contributing guidelines
- So sánh sản phẩm (session-based, tối đa 4, bảng đối chiếu)
- Timeline trạng thái đơn hàng (4 bước: Xác nhận → Đóng gói → Đang giao → Đã giao)
- Nhắc giỏ hàng bỏ quên (model CartReminder, email template, management command)

### Changed
- Replaced flake8/isort/black with Ruff
- Migrated test workflow to PostgreSQL (from MSSQL)
- Updated Django to 4.2 LTS / 5.0 support
- Improved test coverage requirements (70% minimum)

### Fixed
- Various linting issues resolved by Ruff
- Type annotations added across codebase
- Security vulnerabilities in dependencies addressed

## [1.0.0] - 2026-08-26

### Added
- Website bán thời trang Django, giao diện editorial
- Danh mục sản phẩm: lọc theo danh mục/size/màu/giá, sắp xếp, phân trang (12/sp)
- Chi tiết sản phẩm: gallery 6 ảnh, biến thể (màu + size), đã xem gần đây, size chart
- Giỏ hàng session-based: cập nhật số lượng, coupon, phí ship theo vùng, ưu đãi thành viên
- Thanh toán: COD, chuyển khoản VietQR (polling, tự hết hạn 15 phút), VNPay (redirect + callback/IPN xác minh HMAC bằng hmac stdlib)
- Đăng nhập bằng email / SĐT / username, chặn spam (rate limit tự viết trong `core/ratelimit.py`)
- Tra cứu đơn hàng khách vãng lai (mã đơn + SĐT), hủy đơn + hoàn stock
- Đánh giá 2 chiều (khách + shop phản hồi), luồng đổi trả (ReturnRequest)
- Tích điểm & hạn điểm thưởng, ưu đãi sinh nhật, gift card (GiftCard/GiftCardUsage)
- Chương trình giới thiệu bạn bè (ReferralCode/ReferralReward)
- Admin dashboard: biểu đồ doanh thu 7 ngày, báo cáo doanh thu tháng + xuất CSV, bulk actions
- Blog/Lookbook, FAQ support chat, wishlist, newsletter
- Email thông báo SMTP Gmail App Password: đặt hàng, thanh toán, hủy đơn, giao xong, nhắc giỏ hàng bỏ quên
- So sánh sản phẩm (session-based, tối đa 4), timeline đơn hàng 4 bước
- Tối ưu ảnh sang WebP (`optimize_images`), server dev HTTPS cert tự sinh (`run_local.py`)

### Technical Stack
- Python 3.12+ / Django 5.2
- SQL Server (mssql-django + ODBC Driver 18); CI chạy PostgreSQL service container
- Cache/session Redis tùy chọn qua `REDIS_URL`
- Vanilla JavaScript ES5 + CSS thuần (~5.4K dòng), Font Awesome 6.5 local
- Nén asset django-compressor; test Django TestCase (400+ test)

---

## Release Process

1. Update version in `pyproject.toml` and `package.json`
2. Update this CHANGELOG.md
3. Create release commit: `git commit -m "chore: release vX.Y.Z"`
3. Tag release: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
4. Push: `git push origin main --tags`
5. GitHub Actions will build and deploy

---

## Release Types

| Type | Version Bump | When |
|------|--------------|------|
| Major | X.0.0 | Breaking API changes, major redesign |
| Minor | X.Y.0 | New features, backward compatible |
| Patch | X.Y.Z | Bug fixes, security patches |

---

## Links

- [GitHub Releases](https://github.com/your-org/fashion-website/releases)
- [Issues](https://github.com/your-org/fashion-website/issues)
- [Discussions](https://github.com/your-org/fashion-website/discussions)