#!/usr/bin/env python3
"""Fetch HTML pages from Overclockers.ua forum for inspection."""

import argparse
import random
import sys
from pathlib import Path

import httpx
from bs4 import BeautifulSoup


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
]


def fetch_page(url: str, output_dir: Path) -> str:
    """Fetch a single page and save to file."""
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    with httpx.Client(timeout=30.0, follow_redirects=True) as client:
        response = client.get(url, headers=headers)
        response.raise_for_status()

    filename = url.split("/")[-1] or "index"
    if "?" in filename:
        filename = filename.replace("?", "_")
    if not filename.endswith(".html"):
        filename += ".html"

    output_path = output_dir / filename
    output_path.write_text(response.text, encoding="utf-8")
    print(f"Saved: {output_path}")

    return response.text


def fetch_forum_index(base_url: str, output_dir: Path, pages: int) -> list[str]:
    """Fetch forum index pages."""
    html_contents = []

    for page in range(1, pages + 1):
        if page == 1:
            url = base_url
        else:
            url = f"{base_url}&start={(page - 1) * 40}"

        print(f"Fetching page {page}: {url}")
        content = fetch_page(url, output_dir)
        html_contents.append(content)

        delay = random.uniform(1.0, 3.0)
        print(f"Waiting {delay:.1f}s...")
        import time
        time.sleep(delay)

    return html_contents


def fetch_topic(topic_url: str, output_dir: Path) -> str:
    """Fetch a single topic page."""
    print(f"Fetching topic: {topic_url}")
    content = fetch_page(topic_url, output_dir)
    return content


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch Overclockers.ua forum pages")
    parser.add_argument(
        "--base-url",
        default="https://forum.overclockers.ua/viewforum.php?f=26",
        help="Base forum URL",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("scraped_html"),
        help="Output directory for HTML files",
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=2,
        help="Number of index pages to fetch",
    )
    parser.add_argument(
        "--topic",
        help="Fetch a specific topic URL instead of index pages",
    )

    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    try:
        if args.topic:
            fetch_topic(args.topic, args.output_dir)
        else:
            fetch_forum_index(args.base_url, args.output_dir, args.pages)
    except httpx.HTTPError as e:
        print(f"HTTP error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
