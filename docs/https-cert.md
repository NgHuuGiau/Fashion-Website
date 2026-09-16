# HTTPS cho Server Dev

Server local hiện chạy **HTTP** bằng `manage.py runserver` tại `http://localhost:8000/`.
HTTPS chỉ bật ở reverse proxy production bằng certificate thật; không dùng cert dev
cho website mở bán.

Cert trong `backend/certs/`: `server.crt` + `server.key` (cho `localhost`, `127.0.0.1`, `::1`); `ca.crt` là CA `HUUGIAU Fashion Dev CA` đã cài vào Windows Trusted Root Store.

## Lưu ý về chạy HTTP

Nếu cần HTTPS production, cấu hình SSL ở nginx/IIS hoặc load balancer rồi chuyển request
vào Django qua HTTP nội bộ. Không mở trực tiếp `manage.py runserver` ra Internet.

## Trạng thái hiện tại

- Certificate production phải được cấp cho domain thật và quản lý tại reverse proxy.

## Cài CA tin cậy (máy khác)

Nếu mở vẫn báo "Not secure" (máy chưa cài CA), cài `backend/certs/ca.crt` vào Trust Store:

```powershell
certutil -user -addstore Root backend\certs\ca.crt
```

> `-user` cài cho user hiện tại (không cần admin). Cài toàn máy: chạy PowerShell với quyền admin rồi dùng
> `Import-Certificate -FilePath .\backend\certs\ca.crt -CertStoreLocation Cert:\LocalMachine\Root`.

Firefox sẽ mở `http://localhost:8000/` khi chạy local. Với production, cài certificate
domain thật trên reverse proxy và kiểm tra bằng cả Chrome lẫn Firefox.

## Tạo lại cert

Cert hiện tại hết hạn 398 ngày (giới hạn của Chrome). Muốn tạo bộ mới:

```powershell
cd backend\certs
python -c "from scripts.gen_cert import gen_cert; gen_cert()"  # chưa tồn tại → dùng script bên dưới
```

Thay thế bằng cách tạo thủ công bằng Python (thư viện `cryptography` đã có trong requirements):

```powershell
cd backend
python - <<'PY'
import datetime, ipaddress
from pathlib import Path
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

d = Path("certs"); now = datetime.datetime.now(datetime.timezone.utc)
ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
ca_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "HUUGIAU Fashion Dev CA")])
ca = (x509.CertificateBuilder().subject_name(ca_name).issuer_name(ca_name)
      .public_key(ca_key.public_key()).serial_number(x509.random_serial_number())
      .not_valid_before(now - datetime.timedelta(days=1))
      .not_valid_after(now + datetime.timedelta(days=3650))
      .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
      .sign(ca_key, hashes.SHA256()))
srv_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
srv_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "localhost")])
srv = (x509.CertificateBuilder().subject_name(srv_name).issuer_name(ca_name)
       .public_key(srv_key.public_key()).serial_number(x509.random_serial_number())
       .not_valid_before(now - datetime.timedelta(days=1))
       .not_valid_after(now + datetime.timedelta(days=398))
       .add_extension(x509.SubjectAlternativeName([x509.DNSName("localhost"),
                      x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                      x509.IPAddress(ipaddress.IPv6Address("::1"))]), critical=False)
       .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
       .add_extension(x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
       .sign(ca_key, hashes.SHA256()))
(d/"ca.crt").write_bytes(ca.public_bytes(serialization.Encoding.PEM))
(d/"server.crt").write_bytes(srv.public_bytes(serialization.Encoding.PEM))
(d/"server.key").write_bytes(srv_key.private_bytes(serialization.Encoding.PEM,
    serialization.PrivateFormat.TraditionalOpenSSL, serialization.NoEncryption()))
print("done")
PY
```

Tạo xong: **xóa CA cũ** khỏi Trust Store nếu bạn tạo CA mới (Certificate Manager → Trusted Root Certificates), cài CA mới, rồi restart server.

## Lỗi thường gặp

- **`403 Forbidden — CSRF verification failed — Origin checking failed`**: trình duyệt gửi header `Origin` khi POST; origin phải nằm trong `CSRF_TRUSTED_ORIGINS` (`core/settings.py` đã cấu hình `localhost` + `127.0.0.1`). Không liên quan đến HTTPS.
- **"Not secure" trên `127.0.0.1`**: cert có SAN chứa IP, nhưng nếu CA chưa cài thì vẫn cảnh báo → cài CA như trên.
- **`KeyError: WERKZEUG_SERVER_FD`**: đừng dùng `runserver_plus`; dùng `python manage.py runserver`. HTTP là mặc định để chạy local và Playwright; đặt `DEV_HTTPS=true` nếu cần bật HTTPS bằng cert trong `backend/certs/`.
