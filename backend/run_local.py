#!/usr/bin/env python
"""Dev server thay cho 'manage.py runserver'.

Ly do: tren may nay 'manage.py runserver' bi reset moi ket noi HTTP (WinError 10054),
nhung server WSGI truc tiep van chay binh thuong.

Server nay phuc vu HTTPS: cac trinh duyet (Edge/Chrome) co cai dat tu dong chuyen
sang https:// nen truoc day web khong hien thi (400, "only supports HTTP").
Chung chi tu ky duoc tao tu dong tai backend/certs/ khi chay lan dau.

Cach dung:
    python run_local.py [host] [port]
    python run_local.py 127.0.0.1 8000
    python run_local.py 127.0.0.1 8000 --http   # chi HTTP, khong dung TLS
"""
import ipaddress
import os
import socketserver
import ssl
import sys
from datetime import datetime, timedelta, timezone

import django
from django.core.servers.basehttp import (
    WSGIRequestHandler,
    WSGIServer,
    get_internal_wsgi_application,
)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

django.setup()

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


def main():
    use_tls = "--http" not in sys.argv
    args = [a for a in sys.argv[1:] if a != "--http"]
    host = args[0] if len(args) > 0 else "127.0.0.1"
    port = int(args[1]) if len(args) > 1 else 8000

    httpd_cls = type("W", (socketserver.ThreadingMixIn, WSGIServer), {})
    httpd = httpd_cls((host, port), WSGIRequestHandler, ipv6=False)
    httpd.daemon_threads = True
    httpd.set_app(get_internal_wsgi_application())

    scheme = "http"
    if use_tls:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=_ensure_cert()[0], keyfile=_ensure_cert()[1])
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
        scheme = "https"

    display_host = "localhost" if host in ("0.0.0.0", "127.0.0.1") else host
    print(f"Dev server dang chay: {scheme}://{display_host}:{port}/  (Ctrl+C de tat)")
    if use_tls:
        print("Trinh duyet bao dong chung chi tu ky -> bam 'Tiep tuc'/'Advanced' la vao duoc.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nDa dung server.")


if __name__ == "__main__":
    main()
