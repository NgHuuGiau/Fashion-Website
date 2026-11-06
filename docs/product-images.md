# Quản lý ảnh sản phẩm

Catalog local có 90 sản phẩm thật từ bộ dữ liệu Fashion Product Images: 30 áo,
40 quần và 20 phụ kiện. Tên, thông số, mô tả và nhiều góc chụp được ghép theo cùng
mã sản phẩm. Xem [nguồn dữ liệu và cách nhập lại](sourced-catalog.md).

Đây là catalog lưu trữ dùng để xem mẫu. Kaggle ghi nhãn MIT cho bộ dữ liệu;
quyền ảnh của thương hiệu chưa được xác minh độc lập. Trước khi publish để bán,
xác nhận quyền ảnh, giá bán, size và tồn kho thực tế.

## Vị trí lưu ảnh

Thư mục gốc được cấu hình tại `MEDIA_ROOT`:

```text
frontend/static/images/
├── products/YYYY/MM/DD/          # Ảnh đại diện upload trực tiếp
├── products/gallery/YYYY/MM/DD/  # Ảnh phụ/góc chụp trong gallery
├── products/generated/<slug>/    # Asset sinh tự động, không sửa thủ công
├── reviews/YYYY/MM/DD/           # Ảnh khách gửi trong đánh giá
└── avatars/YYYY/MM/              # Ảnh đại diện khách đăng ký
```

Ảnh đại diện và gallery được lưu qua trường `Product.image` và
`ProductImage.image`; ảnh đại diện khách qua `UserProfile.avatar`. Nếu chưa upload
file, sản phẩm có thể dùng trường `Product.image_url` để trỏ tới CDN/object storage.

## Quy cách ảnh chuẩn (theo DirtyCoins / SWE / Levents)

Khảo sát trực tiếp 08/10/2026 (đo pixel + khung render):

| Web | Ảnh gốc upload | Lưới catalog | Trang chi tiết |
|---|---|---|---|
| DirtyCoins | 1638×2048 (4:5), JPG ~25KB | 275×344 (4:5), file 819×1024 | 620×775 (4:5), file gốc |
| SWE | 2048×2048 (1:1), JPG ~48KB | 263×263 (1:1), file `_large` 480px | File gốc vuông |
| Levents | ~4:5 (serve 685×856 webp) | 325×407 (4:5), webp | Khung 4:5 (`aspect-ratio: 4/5`) |

Chốt cho shop (theo số đông 2/3 web, khung dọc tôn dáng):

- **Khung hiển thị: 4:5 dọc** (card `aspect-ratio: 3/4` hiện tại gần đúng,
  placeholder SVG đã dùng viewBox 900×1125 = 4:5).
- **Ảnh gốc: 1600×2000px, JPG ~80%, <300KB.**
- Serve 2 bản: 480px (lưới, như SWE `_large`) + 1024px (detail, như DirtyCoins).
- Khi chưa có ảnh thật, site tự vẽ placeholder line-art theo loại
  (áo/quần/mũ/móc áo) — không cần sửa gì, chỉ cần upload ảnh là tự thay.

## Ảnh demo duyệt layout (DEV only, không phải ảnh thật)

Lệnh `python manage.py seed_demo_photos` tải ảnh thời trang Unsplash
(free license) crop sẵn 1200×2000 (4:5), gắn theo nhóm danh mục để duyệt
layout cho giống DirtyCoins/SWE/Levents. Lệnh từ chối chạy khi
`DEBUG=False`, bỏ qua sản phẩm đã có ảnh thật (chạy lại an toàn).

> Ảnh demo KHÔNG khớp từng sản phẩm (VD khẩu trang có thể hiện giày) —
> chỉ để kiểm bố cục. Trước khi bán phải upload ảnh chụp thật từng mẫu.

## Cách bổ sung sau này

1. Vào **Quản trị → Bảng điều khiển → Sản phẩm**.
2. Chọn sản phẩm, upload ảnh đại diện và tối đa 6 ảnh gallery.
3. Dùng JPG, PNG hoặc WebP; mỗi file tối đa 5MB.
4. Kiểm tra lại ảnh ở catalog và trang chi tiết trước khi publish.

Không nên đặt ảnh trực tiếp ở thư mục gốc `frontend/static/images`; hãy dùng
các thư mục `products` để Django quản lý URL và backup đúng cách.
