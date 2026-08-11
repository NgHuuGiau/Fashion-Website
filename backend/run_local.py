#!/usr/bin/env python
"""Dev server thay cho 'manage.py runserver'.

Ly do: tren may nay 'manage.py runserver' bi reset moi ket noi HTTP (WinError 10054),
nhung server WSGI truc tiep van chay binh thuong. Script nay dung chinh
django.core.servers.basehttp de phuc vu ung dung.

Cach dung:
    python run_local.py [host] [port]
    python run_local.py 127.0.0.1 8000
"""
import os
import socketserver
import sys

import django
from django.core.servers.basehttp import (
    WSGIRequestHandler,
    WSGIServer,
    get_internal_wsgi_application,
)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

django.setup()


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000

    httpd_cls = type("W", (socketserver.ThreadingMixIn, WSGIServer), {})
    httpd = httpd_cls((host, port), WSGIRequestHandler, ipv6=False)
    httpd.daemon_threads = True
    httpd.set_app(get_internal_wsgi_application())

    print(f"Dev server dang chay: http://{host}:{port}/  (Ctrl+C de dung)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nDa dung server.")


if __name__ == "__main__":
    main()
