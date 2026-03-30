from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path
from typing import List, Dict, Any


def convert_csv_rows(csv_path: Path) -> List[Dict[str, Any]]:
    products: List[Dict[str, Any]] = []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            products.append(
                {
                    "ProductID": int(row["ProductID"]),
                    "Name": row["Name"].strip(),
                    "UnitPrice": float(row["UnitPrice"]),
                    "StockQuantity": int(row["StockQuantity"]),
                    "Description": row["Description"].strip(),
                }
            )
    return products


def write_json(products: List[Dict[str, Any]], json_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with json_path.open("w", encoding="utf-8") as json_file:
        json.dump(products, json_file, indent=2)


def store_in_mongodb(products: List[Dict[str, Any]], mongo_uri: str, db_name: str, collection_name: str) -> None:
    try:
        from pymongo import MongoClient, UpdateOne
    except ImportError as exc:
        raise RuntimeError("pymongo is required to import data into MongoDB") from exc

    client = MongoClient(mongo_uri)
    collection = client[db_name][collection_name]
    collection.create_index("ProductID", unique=True)

    operations = [
        UpdateOne({"ProductID": product["ProductID"]}, {"$set": product}, upsert=True)
        for product in products
    ]
    if operations:
        collection.bulk_write(operations)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert products.csv to JSON and load it into MongoDB.")
    parser.add_argument("--csv", dest="csv_path", required=True, help="Path to the source CSV file")
    parser.add_argument("--json", dest="json_path", default="data/products.json", help="Path to the output JSON file")
    parser.add_argument("--mongo-uri", dest="mongo_uri", default=os.getenv("MONGO_URI", "mongodb://localhost:27017"))
    parser.add_argument("--db", dest="db_name", default=os.getenv("MONGO_DB_NAME", "inventory_db"))
    parser.add_argument("--collection", dest="collection_name", default=os.getenv("MONGO_COLLECTION_NAME", "products"))
    args = parser.parse_args()

    csv_path = Path(args.csv_path)
    json_path = Path(args.json_path)

    products = convert_csv_rows(csv_path)
    write_json(products, json_path)
    store_in_mongodb(products, args.mongo_uri, args.db_name, args.collection_name)

    print(f"Imported {len(products)} products into MongoDB and wrote JSON to {json_path}")
