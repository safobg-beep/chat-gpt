from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.parse import parse_qs, urlencode, urljoin, urlparse, urlunparse
from urllib.request import Request, urlopen


@dataclass
class Listing:
    title: str
    url: str
    price: str | None
    location: str | None


class _OlxLinkParser(HTMLParser):
    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url
        self.current_href: str | None = None
        self.current_text: list[str] = []
        self.candidates: list[Listing] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        attr_map = dict(attrs)
        href = attr_map.get("href")
        if href and "/d/ad/" in href:
            self.current_href = href
            self.current_text = []

    def handle_data(self, data: str) -> None:
        if self.current_href is not None:
            self.current_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag != "a" or self.current_href is None:
            return
        title = " ".join(part.strip() for part in self.current_text).strip()
        if title:
            self.candidates.append(
                Listing(
                    title=title,
                    url=urljoin(self.base_url, self.current_href),
                    price=None,
                    location=None,
                )
            )
        self.current_href = None
        self.current_text = []


class OlxShopScraper:
    def __init__(self, base_url: str, delay_seconds: float = 1.0, timeout_seconds: float = 20.0):
        self.base_url = base_url
        self.delay_seconds = delay_seconds
        self.timeout_seconds = timeout_seconds

    def _page_url(self, page: int) -> str:
        if page <= 1:
            return self.base_url

        parsed = urlparse(self.base_url)
        query = parse_qs(parsed.query)
        query["page"] = [str(page)]
        encoded_query = urlencode(query, doseq=True)
        return urlunparse(parsed._replace(query=encoded_query))

    def fetch_page(self, page: int) -> str:
        url = self._page_url(page)
        request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(request, timeout=self.timeout_seconds) as response:
            return response.read().decode("utf-8", errors="replace")

    @staticmethod
    def parse_listings(html: str, base_url: str) -> list[Listing]:
        parser = _OlxLinkParser(base_url)
        parser.feed(html)
        unique = {(l.title, l.url): l for l in parser.candidates}
        return list(unique.values())

    def collect(self, max_pages: int = 1) -> list[Listing]:
        all_items: list[Listing] = []
        for page in range(1, max_pages + 1):
            html = self.fetch_page(page)
            all_items.extend(self.parse_listings(html, self.base_url))
            if page < max_pages:
                time.sleep(self.delay_seconds)

        unique = {(l.title, l.url): l for l in all_items}
        return list(unique.values())


def save_as_json(listings: Iterable[Listing], output_file: str | Path) -> None:
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = [asdict(item) for item in listings]
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
