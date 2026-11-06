# Catalog 90 sản phẩm thật

Catalog local gồm đúng **30 áo, 40 quần, 20 phụ kiện**, không dùng ảnh AI,
ảnh Unsplash gắn ngẫu nhiên hoặc tên sản phẩm tự đặt. Tên gốc được giữ nguyên,
thông số có nhãn tiếng Việt, mô tả chi tiết gốc giữ nguyên ngôn ngữ nguồn.

## Nguồn và giới hạn

- [Fashion Product Images Dataset, Param Aggarwal](https://www.kaggle.com/datasets/paramaggarwal/fashion-product-images-dataset): dữ liệu sản phẩm Myntra lưu trữ, phiên bản cập nhật năm 2019. Đây không phải danh sách hàng đang bán năm 2026.
- [Bản CSV công khai của dcupl](https://github.com/dcupl-demos/fashion-products): dùng để chọn loại sản phẩm và đối chiếu ảnh chính. JSON từng sản phẩm tải trực tiếp từ Kaggle, đối chiếu `id`, `productDisplayName`, `articleType` và URL ảnh chính với CSV.
- Tất cả góc chụp lấy từ `styleImages` của **cùng ID**. Không đưa bảng size hoặc ảnh tìm kiếm vào gallery. Áo/quần có tối thiểu 4 ảnh khác nhau; phụ kiện tối thiểu 2 ảnh. Ảnh JPEG gốc có cạnh ngắn tối thiểu 600 px, tối đa 5 MB; lưu local, có SHA-256 và kích thước từng ảnh.
- Kaggle API ghi nhãn **MIT** cho bộ dữ liệu; điều này không tự xác nhận quyền ảnh hoặc nhãn hiệu của bên thứ ba. Chưa xác minh độc lập quyền dùng ảnh khi bán hàng.
- Giá INR lấy từ bản ghi gốc, quy đổi để tham khảo theo **272,0287 VND/INR**, số liệu ngày 13/10/2026 trên [Investing.com](https://www.investing.com/currencies/inr-vnd-historical-data). Đây không phải giá bán hiện hành, không tạo giảm giá, đánh giá, doanh số hoặc tồn kho giả.
- Sản phẩm mới để tồn kho bằng 0, không tự thêm size. Trên trang chi tiết, ghi rõ mẫu tham khảo và chưa xác nhận giá bán, size, tồn kho; không xuất giá tham khảo thành Offer trong dữ liệu SEO.

## Tạo và nhập lại

Từ thư mục gốc, dùng Python trong `.venv`:

```powershell
.\.venv\Scripts\python.exe scripts/build_sourced_catalog.py
.\.venv\Scripts\python.exe backend/manage.py seed_sourced_catalog
```

Lệnh tải cần kết nối mạng. Lệnh nhập chỉ chạy khi `DEBUG=True`. Nó kiểm tra đủ
90 mẫu, tên/mã khớp nguồn, đường dẫn và hash ảnh trước khi ghi DB; toàn bộ thao tác
ghi nằm trong một transaction. Những sản phẩm cũ được ẩn khỏi danh mục, không xóa
sản phẩm hoặc lịch sử đơn hàng. Nhập lại giữ giá, tồn kho và biến thể đã nhập trong shop.

## File local

- `database/seed/local_products_to_sync.json`: dữ liệu 90 sản phẩm, nguồn chi tiết, danh sách ảnh và hash.
- `.tmp-catalog/source/<id>.json`: bản ghi JSON gốc để đối chiếu.
- `frontend/static/images/products/sourced/myntra/<id>/`: ảnh chính và các góc chụp của cùng sản phẩm.

Các file dữ liệu nguồn và ảnh nằm trong `.gitignore`; khi chuyển máy hoặc deploy
phải tải/chép riêng catalog và kho ảnh. Cấu hình `MEDIA_ROOT` phải trỏ tới kho ảnh này
trước khi nhập. Không chạy `seed_demo_photos --overwrite` trên bộ ảnh đã đối chiếu.

## Kiểm tra

```powershell
.\.venv\Scripts\python.exe backend/manage.py test products.test_sourced_catalog --settings=core.test_settings_sqlite
```

Kiểm tra số lượng theo danh mục, nhập lại không nhân bản, giữ sản phẩm cũ và tồn kho,
từ chối tên sai/ảnh bị đổi/catalog thiếu, chặn production và trang chi tiết dùng ảnh
thật mà không thêm ô ảnh giả.
