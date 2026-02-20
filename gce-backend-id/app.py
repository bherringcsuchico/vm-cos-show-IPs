import html
import os
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.error import URLError, HTTPError

INTERNAL_IP_URL = "http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/ip"
EXTERNAL_IP_URL = "http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip"

def md_get(url: str) -> str:
    req = urllib.request.Request(url, headers={"Metadata-Flavor": "Google"})
    return urllib.request.urlopen(req, timeout=1).read().decode()

def get_internal_ip() -> str:
    try:
        return md_get(INTERNAL_IP_URL)
    except Exception:
        return "unknown"

def get_external_ip() -> str:
    try:
        return md_get(EXTERNAL_IP_URL)
    except HTTPError as e:
        # If no external IP is configured, metadata returns 404
        if e.code == 404:
            return "none"
        return "unknown"
    except (URLError, Exception):
        return "unknown"

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        hostname = html.escape(os.uname().nodename)
        internal_ip = html.escape(get_internal_ip())
        external_ip = html.escape(get_external_ip())

        body = f"""<html>
<head><title>Backend Identity</title></head>
<body style="font-family: Arial, sans-serif;">
  <h2>Served by backend VM</h2>
  <p><b>Hostname:</b> {hostname}</p>
  <p><b>Internal IP:</b> {internal_ip}</p>
  <p><b>External IP:</b> {external_ip}</p>
</body>
</html>"""

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def log_message(self, format, *args):
        return  # quiet

if __name__ == "__main__":
    HTTPServer(("", 80), Handler).serve_forever()
