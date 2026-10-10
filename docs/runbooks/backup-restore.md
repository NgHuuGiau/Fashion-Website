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

## Docker Compose + PostgreSQL

Compose không công khai cổng PostgreSQL ra host. Tạo `.env.compose.production` với thông số thật; script dùng biến trong file này qua Docker Compose và không thực thi file bằng shell. Chạy từ root repository:

```bash
./scripts/backup.sh
```

Script tạo `backups/db_TIMESTAMP.dump` (PostgreSQL custom format) và `backups/media_TIMESTAMP.tar.gz` từ volume `/app/media`, kiểm tra archive rồi giữ các bản trong 30 ngày. Media đã khôi phục trước đó được giữ dưới `.restore-backup.*` trong volume và không đưa vào bản backup mới.

Trước khi khôi phục, dừng nhận đơn, sao lưu trạng thái hiện tại và kiểm tra đúng file đích. Script yêu cầu gõ `RESTORE`, kiểm tra archive trước khi ghi đè. Media cũ vẫn nằm trong volume dưới `.restore-backup.<timestamp>`:

```bash
./scripts/restore.sh db ./backups/db_TIMESTAMP.dump
./scripts/restore.sh media ./backups/media_TIMESTAMP.tar.gz
```

Script cũng đọc được `.dump.gz` PostgreSQL cũ. Không dùng các script Bash này cho SQL Server; SQL Server dùng script PowerShell ở trên. Cần thử khôi phục trên một môi trường Compose tạm trước khi dùng trên production.

## Lịch, lưu trữ và xác minh

- Tạo lịch backup bằng Windows Task Scheduler hoặc cron sau khi kiểm thử lệnh thủ công.
- Giữ bản sao ngoài máy chủ; nếu dùng S3, bật versioning/lifecycle và mã hóa ở bucket. Script upload không tự xóa bản sao cũ trên S3.
- Bảo vệ file backup vì database/media có dữ liệu cá nhân và đơn hàng; giới hạn quyền truy cập và mã hóa ổ đĩa hoặc bucket.
- Sau mỗi lần backup, kiểm tra mã thoát và kích thước file. Định kỳ restore lên môi trường tạm, chạy `/api/health/ready/`, kiểm tra đăng nhập, sản phẩm, đơn hàng và media.
- Chưa có Prometheus alert, email cảnh báo hay lịch restore test trong Compose; cấu hình chúng ở nền tảng vận hành sau khi có server thật.
