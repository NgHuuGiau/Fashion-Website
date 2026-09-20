# Runbook sao lưu và khôi phục

Các script trong repository chỉ thực hiện backup/restore khi được gọi thủ công. Chưa có lịch chạy, lưu trữ ngoài máy chủ, monitoring hay cảnh báo được cấu hình sẵn; cần thiết lập các phần đó trên hạ tầng triển khai.

## SQL Server trên Windows

Chạy PowerShell trên máy chủ SQL Server. Tài khoản dịch vụ SQL Server phải ghi được vào thư mục backup đã chọn. Script tạo file `.bak` native và chạy `RESTORE VERIFYONLY` để kiểm tra cấu trúc backup.

```powershell
.\scripts\backup-db.ps1 -Database HUUGIAU_Fashion -Server . -BackupDirectory D:\FashionBackups
```

Khôi phục sẽ thay thế database đích; cần có bản backup hiện tại và xác nhận bằng cách nhập `RESTORE`:

```powershell
.\scripts\restore-db.ps1 -BackupFile D:\FashionBackups\HUUGIAU_Fashion_20260918_020000.bak -Database HUUGIAU_Fashion -Server .
```

Hãy restore thử vào một database tạm trước khi dùng cho sự cố thật. File backup phải nằm trên đường dẫn mà dịch vụ SQL Server truy cập được.

## PostgreSQL trực tiếp

`scripts/backup.sh` tạo archive custom-format `.dump.gz`; script cần `DB_HOST`, `DB_NAME`, `DB_USER` và `DB_PASSWORD` được truyền qua environment. Script không tự đọc `.env` để tránh phân tích sai hoặc thực thi nội dụng môi trường như shell.

```bash
DB_ENGINE=postgres DB_HOST=db DB_PORT=5432 DB_NAME=huugiau_fashion DB_USER=huugiau \
  DB_PASSWORD="$DB_PASSWORD" ./scripts/backup.sh full
```

Khôi phục chỉ chấp nhận `.dump`/`.dump.gz`, yêu cầu gõ `RESTORE`, kiểm tra archive trước khi gọi `pg_restore` và ghi đè schema database đã chọn:

```bash
DB_ENGINE=postgres DB_HOST=db DB_PORT=5432 DB_NAME=huugiau_fashion DB_USER=huugiau \
  DB_PASSWORD="$DB_PASSWORD" ./scripts/restore.sh db ./backups/db/fashion-website_db_TIMESTAMP.dump.gz
```

Không dùng các script PostgreSQL cho SQL Server. SQL Server dùng riêng các script PowerShell ở trên.

## Docker Compose

Compose không công khai cổng PostgreSQL/PgBouncer ra host. Có thể tạo database backup trực tiếp từ service database; lệnh sau tạo file custom-format nén trên host:

```bash
mkdir -p backups/db
docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom --no-owner --no-acl' \
  | gzip -9 > "backups/db/fashion-website_db_$(date +%Y%m%d_%H%M%S).dump.gz"
gzip -t backups/db/*.dump.gz
```

Sao lưu vùng media hiện tại trong container (ảnh thật có thể được thêm sau):

```bash
mkdir -p backups/media
docker compose exec -T app tar -C /app/frontend/static -czf - images \
  > "backups/media/fashion-website_media_$(date +%Y%m%d_%H%M%S).tar.gz"
tar -tzf backups/media/FILE.tar.gz
```

Trước khi restore, dừng nhận đơn và tạo thêm một backup hiện tại. Restore database bằng `pg_restore --clean --if-exists` lên database đích; restore media giữ thư mục media cũ dưới tên `.backup.<timestamp>` trước khi thay. Không chạy restore trực tiếp trên production nếu chưa xác nhận chính xác database và file nguồn.

## Lịch, lưu trữ và xác minh

- Tạo lịch backup bằng Windows Task Scheduler hoặc cron sau khi kiểm thử lệnh thủ công.
- Giữ bản sao ngoài máy chủ; nếu dùng S3, bật versioning/lifecycle và mã hóa ở bucket. Script upload không tự xóa bản sao cũ trên S3.
- Bảo vệ file backup vì database/media có dữ liệu cá nhân và đơn hàng; giới hạn quyền truy cập và mã hóa ổ đĩa hoặc bucket.
- Sau mỗi lần backup, kiểm tra mã thoát và kích thước file. Định kỳ restore lên môi trường tạm, chạy `/api/health/ready/`, kiểm tra đăng nhập, sản phẩm, đơn hàng và media.
- Chưa có Prometheus alert, email cảnh báo hay lịch restore test trong Compose; cấu hình chúng ở nền tảng vận hành sau khi có server thật.
