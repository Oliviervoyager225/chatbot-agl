import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
from collections import deque
from pathlib import Path
import argparse
import json
import time
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

START_URL = "https://www.aglgroup.com/"
BASE_DOMAIN = ".".join(urlparse(START_URL).netloc.rsplit(".", 2)[-2:])

OUTPUT_DIR = (
    Path(__file__).resolve().parent.parent.parent.parent / "data" / "website_scrape"
)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SESSION = requests.Session()
SESSION.headers["User-Agent"] = (
    "Mozilla/5.0 (compatible; AGLChatBot/0.1; +https://github.com/korokoa)"
)


def normalize_url(url):
    parsed = urlparse(url)
    return urlunparse(parsed._replace(fragment="", query=""))


def is_internal_link(url):
    netloc = urlparse(url).netloc
    is_internal = (
        netloc == "" or netloc == BASE_DOMAIN or netloc.endswith("." + BASE_DOMAIN)
    )
    logger.debug("Link check: %s -> internal=%s", url, is_internal)
    return is_internal


def clean_text(text):
    cleaned = " ".join(text.split())
    logger.debug("Cleaned text length: %d chars", len(cleaned))
    return cleaned


def save_results(pages):
    filepath = OUTPUT_DIR / "pages.json"
    filepath.write_text(
        json.dumps(pages, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    logger.info("Saved %d pages to %s", len(pages), filepath)


def fetch_page(url):
    logger.info("Fetching: %s", url)
    response = SESSION.get(url, timeout=10)
    response.raise_for_status()
    logger.debug(
        "Response %d from %s (%d bytes)",
        response.status_code,
        url,
        len(response.content),
    )

    content_type = response.headers.get("Content-Type", "")
    if "text/html" not in content_type:
        logger.warning("Non-HTML content (%s): %s", content_type, url)
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    hrefs = [link["href"] for link in soup.find_all("a", href=True)]

    title_tag = soup.find("title")
    title = clean_text(title_tag.get_text()) if title_tag else ""

    for tag in soup.find_all(["nav", "header", "footer", "aside", "script", "style"]):
        tag.decompose()

    main = soup.find("main")
    body = main if main else soup.body
    text = clean_text(body.get_text(separator=" ")) if body else ""

    page = {"title": title, "text": text, "link": url}
    logger.info("Extracted page: %s (%d chars)", title, len(text))
    return page, hrefs


def fetch_single(url):
    url = normalize_url(url)
    result = fetch_page(url)
    if result is None:
        return None
    page, _ = result
    return page


def crawl(start_url):
    visited = set()
    pages = []
    queue = deque([normalize_url(start_url)])

    while queue:
        url = queue.popleft()

        if url in visited:
            logger.debug("Skipping already visited: %s", url)
            continue

        visited.add(url)
        logger.info("Crawling: %s (visited %d pages so far)", url, len(visited))

        try:
            result = fetch_page(url)
        except Exception as e:
            logger.error("Failed to fetch %s: %s", url, e)
            continue

        if result is None:
            continue

        page, hrefs = result
        pages.append(page)

        for href in hrefs:
            full_url = normalize_url(urljoin(url, href))
            if full_url not in visited and is_internal_link(full_url):
                queue.append(full_url)

        time.sleep(0.5)

    save_results(pages)
    return pages


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AGL website crawler")
    parser.add_argument(
        "--single", metavar="URL", help="Extract a single page without following links"
    )
    args = parser.parse_args()

    if args.single:
        page = fetch_single(args.single)
        if page:
            print(json.dumps(page, ensure_ascii=False, indent=2))
            filepath = OUTPUT_DIR / f"{page['title']}.json"
            existing = json.loads(filepath.read_text(encoding="utf-8")) if filepath.exists() else []
            existing.append(page)
            filepath.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
            logger.info("Saved to %s (%d pages total)", filepath, len(existing))
    else:
        logger.info("Starting crawl from %s", START_URL)
        result = crawl(START_URL)
        logger.info("Crawl complete. Extracted %d pages.", len(result))
