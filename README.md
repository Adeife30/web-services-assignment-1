# Inventory Management API

This project was built from scratch to match the Web Services Assignment 1 brief.

## Features
- CSV to JSON conversion and MongoDB import using Python
- FastAPI inventory API
- Pydantic validation
- Python unit tests
- Postman + Newman test collection
- Docker Ubuntu container
- Jenkins pipeline
- Uptime Kuma monitoring guide

## Required endpoints
- `/getSingleProduct`
- `/getAll`
- `/addNew`
- `/deleteOne`
- `/startsWith`
- `/paginate`
- `/convert`

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt
python scripts/import_csv_to_mongo.py --csv data/products.csv --json data/products.json
python -m uvicorn app.main:app --reload --port 8000
```

FastAPI docs:
- `http://localhost:8000/docs`
