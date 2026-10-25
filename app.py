"""Local web server for the CLEARCUT Basic Data Cleaning Lab; uses Python's standard library."""
from __future__ import annotations

import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote

from cleaning import clean_csv_text

ROOT = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = 8000
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
ALLOWED_FILES = {
    "/": ROOT / "index.html",
    "/index.html": ROOT / "index.html",
    "/styles.css": ROOT / "styles.css",
    "/app.js": ROOT / "app.js",
    "/data/original_student_performance.csv": ROOT / "data" / "original_student_performance.csv",
}


class AppHandler(BaseHTTPRequestHandler):
    server_version = "ClearcutDataLab/1.0"

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        path = unquote(self.path.split("?", 1)[0])
        if path == "/api/health":
            body = json.dumps({"ok": True, "service": "CLEARCUT Data Cleaning Lab"}).encode("utf-8")
            self._send(200, body, "application/json; charset=utf-8")
            return
        file_path = ALLOWED_FILES.get(path)
        if not file_path or not file_path.is_file():
            self._send(404, b"Not found", "text/plain; charset=utf-8")
            return
        content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        if content_type.startswith("text/") or content_type in {"application/javascript", "application/json"}:
            content_type += "; charset=utf-8"
        self._send(200, file_path.read_bytes(), content_type)

    def do_POST(self) -> None:  # noqa: N802
        if self.path.split("?", 1)[0] != "/api/clean":
            self._send(404, b'{"error":"Not found"}', "application/json; charset=utf-8")
            return
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            content_length = 0
        if content_length <= 0:
            self._send(400, json.dumps({"error": "No CSV content received."}).encode(), "application/json; charset=utf-8")
            return
        if content_length > MAX_UPLOAD_BYTES:
            self._send(413, json.dumps({"error": "For this local demo, upload a CSV smaller than 5 MB."}).encode(), "application/json; charset=utf-8")
            return
        try:
            csv_text = self.rfile.read(content_length).decode("utf-8-sig")
            result = clean_csv_text(csv_text)
            result.pop("cleaned_dataframe", None)
            body = json.dumps(result, ensure_ascii=False, allow_nan=False).encode("utf-8")
            self._send(200, body, "application/json; charset=utf-8")
        except (UnicodeDecodeError, ValueError) as exc:
            body = json.dumps({"error": str(exc)}, ensure_ascii=False).encode("utf-8")
            self._send(400, body, "application/json; charset=utf-8")
        except Exception as exc:  # Return a readable error rather than dropping the request.
            body = json.dumps({"error": f"Cleaning failed safely: {exc}"}, ensure_ascii=False).encode("utf-8")
            self._send(500, body, "application/json; charset=utf-8")

    def log_message(self, format: str, *args: object) -> None:
        print(f"[CLEARCUT] {self.address_string()} - {format % args}")


def main() -> None:
    httpd = ThreadingHTTPServer((HOST, PORT), AppHandler)
    print("\nCLEARCUT — BASIC DATA CLEANING LAB")
    print("----------------------------------")
    print(f"Open this address in your browser: http://{HOST}:{PORT}")
    print("Press Ctrl+C in this terminal to stop the server.\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
