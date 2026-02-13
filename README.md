# OLX Shop Data Collector App

Това е примерна Python апликация, която събира обяви от OLX shop страница (напр. `https://estestvenratan.olx.bg/home/`) и ги предоставя:

1. през CLI;
2. през HTTP endpoint;
3. в JSON файл за последваща употреба.

> ⚠️ Важно: спазвай Terms of Service на OLX, robots.txt и приложимото законодателство (GDPR, авторско право, използване на публични данни).

## Инсталация

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## CLI ползване

```bash
python -m olx_data_app.cli \
  --base-url "https://estestvenratan.olx.bg/home/" \
  --max-pages 5 \
  --delay 1.0 \
  --output data/listings.json
```

## API ползване

```bash
python app.py
```

После:

```bash
curl -X POST http://127.0.0.1:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "base_url": "https://estestvenratan.olx.bg/home/",
    "max_pages": 3,
    "delay_seconds": 1.0,
    "output_file": "data/listings.json"
  }'
```

## Структура

- `olx_data_app/scraper.py` – логика за извличане и парсване на данните.
- `olx_data_app/cli.py` – command-line интерфейс.
- `app.py` – HTTP API приложение (stdlib server).
- `tests/test_parser.py` – тестове за HTML parser-а.
