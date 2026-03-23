# Site Parser Demo

Парсер каталога книг с сайта books.toscrape.com.

## Возможности

- Парсинг названия, цены, наличия и рейтинга
- Пагинация (несколько страниц)
- Выгрузка в CSV и JSON
- CLI-интерфейс с параметрами

## Запуск

```bash
pip install -r requirements.txt
python parser.py --pages 3 --format both --output books
```

## Параметры

- `--pages N` — количество страниц (по умолчанию 3)
- `--output name` — имя файла без расширения
- `--format csv|json|both` — формат выгрузки

## Docker

```bash
docker build -t parser .
docker run parser --pages 5 --format csv
```
