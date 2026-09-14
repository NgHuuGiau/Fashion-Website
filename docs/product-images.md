# Quản lý ảnh sản phẩm

Hiện tại không cần thay ảnh sản phẩm. Khi có bộ ảnh 76 sản phẩm, có thể bổ sung
qua trang quản trị hoặc chép/upload theo đúng cấu trúc dưới đây.

## Vị trí lưu ảnh

Thư mục gốc được cấu hình tại `MEDIA_ROOT`:

```text
frontend/static/images/
├── products/YYYY/MM/DD/          # Ảnh đại diện upload trực tiếp
├── products/gallery/YYYY/MM/DD/  # Ảnh phụ/góc chụp trong gallery
├── products/generated/<slug>/    # Asset sinh tự động, không sửa thủ công
└── reviews/YYYY/MM/DD/           # Ảnh khách gửi trong đánh giá
```

Ảnh đại diện và gallery được lưu qua trường `Product.image` và
`ProductImage.image`. Nếu chưa upload file, sản phẩm có thể dùng trường
`Product.image_url` để trỏ tới CDN/object storage.

## Cách bổ sung sau này

1. Vào **Quản trị → Bảng điều khiển → Sản phẩm**.
2. Chọn sản phẩm, upload ảnh đại diện và tối đa 6 ảnh gallery.
3. Dùng JPG, PNG hoặc WebP; mỗi file tối đa 5MB.
4. Kiểm tra lại ảnh ở catalog và trang chi tiết trước khi publish.

Không nên đặt ảnh trực tiếp ở thư mục gốc `frontend/static/images`; hãy dùng
các thư mục `products` để Django quản lý URL và backup đúng cách.
