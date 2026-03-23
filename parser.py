#!/usr/bin/env python3
"""
Парсер каталога books.toscrape.com
Публичный тестовый сайт для скрапинга.
"""

import argparse
import csv
import json
import logging
import time
from dataclasses import dataclass, asdict
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

from config import (
    BASE_URL, START_URL, DEFAULT_PAGES, DEFAULT_OUTPUT, DEFAULT_FORMAT,
    RATING_MAP, HEADERS, REQUEST_DELAY, REQUEST_TIMEOUT,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


@dataclass
class Book:
    title: str
    price: float
    available: bool
    rating: int
    url: str


def fetch_page(url: str, session: requests.Session) -> Optional[BeautifulSoup]:
    try:
        resp = session.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "lxml")
    except requests.RequestException as e:
        logger.error("Ошибка при загрузке %s: %s", url, e)
        return None


def parse_books(soup: BeautifulSoup) -> List[Book]:
    books = []
    articles = soup.select("article.product_pod")

    for article in articles:
        title_tag = article.select_one("h3 > a")
        title = title_tag["title"] if title_tag else "N/A"
        rel_url = title_tag["href"].replace("../", "") if title_tag else ""
        full_url = BASE_URL + rel_url

        price_tag = article.select_one("p.price_color")
        try:
            price = float(price_tag.text.strip().replace("£", "").replace("Â", ""))
        except (AttributeError, ValueError):
            price = 0.0

        avail_tag = article.select_one("p.availability")
        available = avail_tag and "In stock" in avail_tag.text

        rating_tag = article.select_one("p.star-rating")
        rating_word = rating_tag["class"][1] if rating_tag else "Zero"
        rating = RATING_MAP.get(rating_word, 0)

        books.append(Book(
            title=title,
            price=price,
            available=bool(available),
            rating=rating,
            url=full_url,
        ))

    return books


def get_next_page_url(soup: BeautifulSoup) -> Optional[str]:
    next_btn = soup.select_one("li.next > a")
    if not next_btn:
        return None
    href = next_btn["href"]
    if href.startswith("catalogue/"):
        return "https://books.toscrape.com/" + href
    return BASE_URL + href


def scrape(pages: int) -> List[Book]:
    session = requests.Session()
    all_books: List[Book] = []
    url = START_URL

    for page_num in range(1, pages + 1):
        logger.info("Страница %d/%d — %s", page_num, pages, url)
        soup = fetch_page(url, session)
        if soup is None:
            break

        books = parse_books(soup)
        all_books.extend(books)
        logger.info("  Собрано книг: %d (всего: %d)", len(books), len(all_books))

        if page_num < pages:
            next_url = get_next_page_url(soup)
            if not next_url:
                logger.info("Следующей страницы нет, остановка.")
                break
            url = next_url
            time.sleep(REQUEST_DELAY)

    return all_books


def save_csv(books: List[Book], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "price", "available", "rating", "url"])
        writer.writeheader()
        writer.writerows(asdict(b) for b in books)
    logger.info("CSV сохранён: %s", path)


def save_json(books: List[Book], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump([asdict(b) for b in books], f, ensure_ascii=False, indent=2)
    logger.info("JSON сохранён: %s", path)


def build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Парсер каталога books.toscrape.com",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--pages", type=int, default=DEFAULT_PAGES,
        help="Количество страниц для парсинга"
    )
    parser.add_argument(
        "--output", default=DEFAULT_OUTPUT,
        help="Имя выходного файла (без расширения)"
    )
    parser.add_argument(
        "--format", choices=["csv", "json", "both"], default=DEFAULT_FORMAT,
        help="Формат выгрузки"
    )
    return parser


def main() -> None:
    args = build_cli().parse_args()

    logger.info("Старт: %d стр., формат=%s, файл=%s", args.pages, args.format, args.output)
    books = scrape(args.pages)
    logger.info("Итого собрано книг: %d", len(books))

    if args.format in ("csv", "both"):
        save_csv(books, f"{args.output}.csv")
    if args.format in ("json", "both"):
        save_json(books, f"{args.output}.json")


if __name__ == "__main__":
    main()
