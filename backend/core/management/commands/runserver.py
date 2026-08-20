import ssl
from pathlib import Path

from django.contrib.staticfiles.management.commands.runserver import (
    Command as StaticfilesRunserverCommand,
)
from django.core.servers.basehttp import WSGIServer

CERT_FILE = (
    Path(__file__).resolve().parent.parent.parent.parent / "certs" / "server.crt"
)
KEY_FILE = Path(__file__).resolve().parent.parent.parent.parent / "certs" / "server.key"

_SSL_CONTEXT = None
if CERT_FILE.exists():
    _ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    _ctx.load_cert_chain(CERT_FILE, KEY_FILE)
    _SSL_CONTEXT = _ctx


class SSLWSGIServer(WSGIServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if _SSL_CONTEXT is not None:
            self.socket = _SSL_CONTEXT.wrap_socket(self.socket, server_side=True)
            # The socket is wrapped with TLS below WSGI, so Django/wsgiref can
            # not tell that requests are HTTPS on their own. wsgiref.servers
            # derive wsgi.url_scheme from the legacy ``HTTPS`` environ entry
            # (and otherwise rewrite it to ``http``), so advertise both to keep
            # every generated absolute URL (e.g. the VietQR mobile link) HTTPS.
            self.base_environ["HTTPS"] = "on"
            self.base_environ["wsgi.url_scheme"] = "https"


class Command(StaticfilesRunserverCommand):
    server_cls = SSLWSGIServer
