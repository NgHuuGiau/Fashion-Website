#!/usr/bin/env python
"""Dev server thay cho 'manage.py runserver'.

Lý do: trên máy này 'manage.py runserver' bị reset mọi kết nối HTTP (WinError 10054),
nhưng chạy qua server uvicorn thì ổn định. Uvicorn xử lý HTTPS/TLS sạch, không bị
lỗi cắt response lớn (ERR_RESPONSE_HEADERS_TRUNCATED) như wsgiref + ssl.

Server phục vụ HTTPS: các trình duyệt (Edge/Chrome) tự động chuyển sang https://.
Chứng chỉ tự ký được tạo tự động tại backend/certs/ khi chạy lần đầu.

Cách dùng:
    python run_local.py [host] [port]
    python run_local.py 127.0.0.1 8000
    python run_local.py 127.0.0.1 8000 --http   # chỉ HTTP, không dùng TLS
"""

import ipaddress
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

CERT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "certs")
CERT_PATH = os.path.join(CERT_DIR, "dev-cert.pem")
KEY_PATH = os.path.join(CERT_DIR, "dev-key.pem")


def _ensure_cert():
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import NameOID

    if os.path.exists(CERT_PATH) and os.path.exists(KEY_PATH):
        return CERT_PATH, KEY_PATH

    os.makedirs(CERT_DIR, exist_ok=True)
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "localhost")])
    san = x509.SubjectAlternativeName(
        [
            x509.DNSName("localhost"),
            x509.IPAddress(ipaddress.ip_address("127.0.0.1")),
            x509.IPAddress(ipaddress.ip_address("::1")),
        ]
    )
    now = datetime.now(timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=5))
        .not_valid_after(now + timedelta(days=365))
        .add_extension(san, critical=False)
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .sign(key, hashes.SHA256())
    )
    with open(KEY_PATH, "wb") as f:
        f.write(
            key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.TraditionalOpenSSL,
                serialization.NoEncryption(),
            )
        )
    with open(CERT_PATH, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    return CERT_PATH, KEY_PATH


def _main_uvicorn(host, port, use_tls):
    import django
    from django.core.asgi import get_asgi_application

    django.setup()
    application = get_asgi_application()

    import uvicorn

    kwargs = {}
    scheme = "http"
    if use_tls:
        cert, key = _ensure_cert()
        kwargs = {"ssl_certfile": cert, "ssl_keyfile": key}
        scheme = "https"
    display_host = "localhost" if host in ("0.0.0.0", "127.0.0.1") else host
    print(f"Dev server đang chạy: {scheme}://{display_host}:{port}/  (Ctrl+C để tắt)")
    if use_tls:
        print(
            "Trình duyệt báo động chứng chỉ tự ký -> bấm 'Tiếp tục'/'Advanced' là vào được."
        )
    try:
        uvicorn.run(application, host=host, port=port, log_level="warning", **kwargs)
    except KeyboardInterrupt:
        print("\nĐã dừng server.")


def _main_wsgiref(host, port, use_tls):

    import socketserver
    import ssl

    import django
    from django.core.servers.basehttp import (
        WSGIRequestHandler,
        WSGIServer,
        get_internal_wsgi_application,
    )

    class _Handler(WSGIRequestHandler):
        def log_message(self, format, *args):
            pass

        protocol_version = "HTTP/1.1"

    django.setup()
    httpd_cls = type("W", (socketserver.ThreadingMixIn, WSGIServer), {})
    httpd = httpd_cls((host, port), _Handler, ipv6=False)
    httpd.daemon_threads = True
    httpd.set_app(get_internal_wsgi_application())

    scheme = "http"
    if use_tls:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=_ensure_cert()[0], keyfile=_ensure_cert()[1])
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
        scheme = "https"

    display_host = "localhost" if host in ("0.0.0.0", "127.0.0.1") else host
    print(f"Dev server đang chạy: {scheme}://{display_host}:{port}/  (Ctrl+C để tắt)")
    if use_tls:
        print(
            "Trình duyệt báo động chứng chỉ tự ký -> bấm 'Tiếp tục'/'Advanced' là vào được."
        )
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nĐã dừng server.")


def main():
    use_tls = "--http" not in sys.argv
    args = [a for a in sys.argv[1:] if a != "--http"]
    host = args[0] if len(args) > 0 else "127.0.0.1"
    port = int(args[1]) if len(args) > 1 else 8000

    try:
        import uvicorn  # noqa: F401

        _main_uvicorn(host, port, use_tls)
    except ImportError:
        _main_wsgiref(host, port, use_tls)


if __name__ == "__main__":
    main()
