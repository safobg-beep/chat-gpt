from __future__ import annotations

import argparse

from olx_data_app.scraper import OlxShopScraper, save_as_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Collect OLX shop listings")
    parser.add_argument("--base-url", required=True, help="OLX shop URL, e.g. https://estestvenratan.olx.bg/home/")
    parser.add_argument("--max-pages", type=int, default=1, help="How many paginated pages to fetch")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between page requests in seconds")
    parser.add_argument("--output", default="data/listings.json", help="Output JSON path")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    scraper = OlxShopScraper(base_url=args.base_url, delay_seconds=args.delay)
    listings = scraper.collect(max_pages=args.max_pages)
    save_as_json(listings, args.output)
    print(f"Saved {len(listings)} listings to {args.output}")


if __name__ == "__main__":
    main()
