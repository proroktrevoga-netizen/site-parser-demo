import csv
import json
import logging

logger = logging.getLogger(__name__)


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
