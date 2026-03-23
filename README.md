# Site Parser Demo

Парсер каталога товаров на Python. Демо-проект для портфолио.

Парсит публичный тестовый сайт [books.toscrape.com](https://books.toscrape.com) — название, цена, наличие, рейтинг книг. Поддерживает пагинацию, выгрузку в CSV и JSON, CLI-интерфейс.

## Стек

- Python 3.11
- BeautifulSoup4 + lxml
- requests
- argparse, dataclasses, logging

## Установка

```bash
pip install -r requirements.txt
```

## Использование

```bash
# Парсить 5 страниц, выгрузить в CSV (по умолчанию)
python parser.py

# 10 страниц, JSON
python parser.py --pages 10 --format json

# Оба формата, произвольное имя файла
python parser.py --pages 3 --format both --output catalog

# Справка
python parser.py --help
```

## Docker

```bash
docker build -t site-parser .
docker run --rm -v $(pwd)/output:/app site-parser --pages 5 --format both --output /app/books
```

## Структура вывода

**CSV / JSON:**

| Поле | Тип | Описание |
|------|-----|----------|
| title | string | Название книги |
| price | float | Цена в фунтах |
| available | bool | Наличие на складе |
| rating | int | Рейтинг 1–5 |
| url | string | Ссылка на страницу |

## Конфигурация

Параметры в `config.py`: `BASE_URL`, `DEFAULT_PAGES`, `REQUEST_DELAY`, `REQUEST_TIMEOUT`.
