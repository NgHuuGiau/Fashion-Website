"""Django dev server with HTTPS. Drop-in replacement for runserver."""
import os
import sys
import ssl
import threading
from wsgiref.simple_server import make_server, WSGIServer
from wsgiref import simple_server

# Setup Django
backend_dir = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.insert(0, backend_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django
django.setup()
from django.core.handlers.wsgi import WSGIHandler
from django.conf import settings

app = WSGIHandler()
host = "0.0.0.0"
port = 8000
cert_dir = os.path.join(backend_dir, "certs")
cert_file = os.path.join(cert_dir, "server.crt")
key_file = os.path.join(cert_dir, "server.key")

# Ensure ALLOWED_HOSTS includes localhost
if not settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS = ["*"]

httpd = make_server(host, port, app)

try:
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(cert_file, key_file)
    httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)
    protocol = "HTTPS"
except Exception as e:
    print(f"SSL error: {e}")
    protocol = "HTTP"

print(f"Django dev server ({protocol}): https://localhost:{port}")
print(f"Or try: http://localhost:{port}")
print("Press Ctrl+C to stop")

try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("\nServer stopped.")
