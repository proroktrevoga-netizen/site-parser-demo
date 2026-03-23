import argparse
import csv
import json
import logging
import time

import requests
from bs4 import BeautifulSoup

from config import BASE_URL, DEFAULT_PAGES

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

RATING_MAP = {
    "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5,
}


def parse_page(url: str) -> list[dict]:
    logger.info(f"Parsing: {url}")
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    books = []
    for article in soup.select("article.product_pod"):
        title = article.select_one("h3 a")["title"]
        price = article.select_one(".price_color").text.strip("£Â")
        in_stock = "In stock" in article.select_one(".availability").text
        rating_class = article.select_one("p.star-rating")["class"][1]
        rating = RATING_MAP.get(rating_class, 0)
        books.append({
            "title": title,
            "price": float(price),
            "in_stock": in_stock,
            "rating": rating,
        })
    return books


def parse_catalog(pages: int) -> list[dict]:
    all_books = []
    for page_num in range(1, pages + 1):
        if page_num == 1:
            url = BASE_URL
        else:
            url = f"{BASE_URL}catalogue/page-{page_num}.html"
        try:
            books = parse_page(url)
            all_books.extend(books)
            logger.info(f"Page {page_num}: {len(books)} books")
            time.sleep(0.5)
        except Exception as e:
            logger.error(f"Error on page {page_num}: {e}")
            break
    return all_books


def save_csv(data: list[dict], output: str):
    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "price", "in_stock", "rating"])
        writer.writeheader()
        writer.writerows(data)
    logger.info(f"Saved {len(data)} records to {output}")


def save_json(data: list[dict], output: str):
    with open(output, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved {len(data)} records to {output}")


def main():
    parser = argparse.ArgumentParser(description="Book catalog parser")
    parser.add_argument("--pages", type=int, default=DEFAULT_PAGES, help="Number of pages to parse")
    parser.add_argument("--output", type=str, default="books", help="Output filename (without extension)")
    parser.add_argument("--format", choices=["csv", "json", "both"], default="both", help="Output format")
    args = parser.parse_args()

    books = parse_catalog(args.pages)
    logger.info(f"Total: {len(books)} books")

    if args.format in ("csv", "both"):
        save_csv(books, f"{args.output}.csv")
    if args.format in ("json", "both"):
        save_json(books, f"{args.output}.json")


if __name__ == "__main__":
    main()
