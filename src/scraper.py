import logging
import time

import requests
from bs4 import BeautifulSoup

from src.config import BASE_URL, REQUEST_DELAY, RATING_MAP

logger = logging.getLogger(__name__)


def parse_page(soup: BeautifulSoup) -> list[dict]:
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


def scrape(pages: int) -> list[dict]:
    all_books = []
    for page_num in range(1, pages + 1):
        if page_num == 1:
            url = BASE_URL
        else:
            url = f"{BASE_URL}catalogue/page-{page_num}.html"
        logger.info(f"Parsing: {url}")
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")
            books = parse_page(soup)
            all_books.extend(books)
            logger.info(f"Page {page_num}: {len(books)} books")
            time.sleep(REQUEST_DELAY)
        except Exception as e:
            logger.error(f"Error on page {page_num}: {e}")
            break
    return all_books
