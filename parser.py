import argparse
import logging

from src.config import DEFAULT_PAGES
from src.scraper import scrape
from src.exporters import save_csv, save_json

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Book catalog parser")
    parser.add_argument("--pages", type=int, default=DEFAULT_PAGES, help="Pages to parse")
    parser.add_argument("--output", type=str, default="output/books", help="Output path")
    parser.add_argument("--format", choices=["csv", "json", "both"], default="both", help="Output format")
    args = parser.parse_args()

    books = scrape(args.pages)
    logger.info(f"Total: {len(books)} books")

    if args.format in ("csv", "both"):
        save_csv(books, f"{args.output}.csv")
    if args.format in ("json", "both"):
        save_json(books, f"{args.output}.json")


if __name__ == "__main__":
    main()
