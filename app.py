from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from olx_data_app.scraper import OlxShopScraper, save_as_json


class AppHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload: dict, status: int = HTTPStatus.OK) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._send_json({"status": "ok"})
            return
        self._send_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/scrape":
            self._send_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length) if length else b"{}"

        try:
            payload = json.loads(raw_body.decode("utf-8"))
            base_url = payload["base_url"]
            max_pages = int(payload.get("max_pages", 1))
            delay_seconds = float(payload.get("delay_seconds", 1.0))
            output_file = payload.get("output_file", "data/listings.json")

            scraper = OlxShopScraper(base_url=base_url, delay_seconds=delay_seconds)
            listings = scraper.collect(max_pages=max_pages)
            save_as_json(listings, output_file)
        except Exception as exc:  # noqa: BLE001
            self._send_json({"error": f"Scrape failed: {exc}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        self._send_json(
            {
                "count": len(listings),
                "output_file": output_file,
                "items": [item.__dict__ for item in listings],
            }
        )


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), AppHandler)
    print(f"Server running on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
