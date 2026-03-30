from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class ProductRepository(ABC):
    @abstractmethod
    def get_single_product(self, product_id: int) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def get_all_products(self) -> List[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def add_product(self, product: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def delete_product(self, product_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    def starts_with(self, letter: str) -> List[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def paginate(self, start_id: int, end_id: int, batch_size: int = 10) -> List[Dict[str, Any]]:
        raise NotImplementedError


class InMemoryProductRepository(ProductRepository):
    def __init__(self, initial_products: Optional[List[Dict[str, Any]]] = None):
        self.products: List[Dict[str, Any]] = sorted(initial_products or [], key=lambda x: x["ProductID"])

    def get_single_product(self, product_id: int) -> Optional[Dict[str, Any]]:
        return next((p for p in self.products if p["ProductID"] == product_id), None)

    def get_all_products(self) -> List[Dict[str, Any]]:
        return sorted(self.products, key=lambda x: x["ProductID"])

    def add_product(self, product: Dict[str, Any]) -> Dict[str, Any]:
        if self.get_single_product(product["ProductID"]):
            raise ValueError("Product ID already exists")
        self.products.append(product)
        self.products.sort(key=lambda x: x["ProductID"])
        return product

    def delete_product(self, product_id: int) -> bool:
        product = self.get_single_product(product_id)
        if not product:
            return False
        self.products.remove(product)
        return True

    def starts_with(self, letter: str) -> List[Dict[str, Any]]:
        target = letter.lower()
        return [p for p in self.get_all_products() if p["Name"].lower().startswith(target)]

    def paginate(self, start_id: int, end_id: int, batch_size: int = 10) -> List[Dict[str, Any]]:
        filtered = [p for p in self.get_all_products() if start_id <= p["ProductID"] <= end_id]
        return filtered[:batch_size]


class MongoProductRepository(ProductRepository):
    def __init__(self, mongo_uri: str, db_name: str, collection_name: str):
        try:
            from pymongo import MongoClient
        except ImportError as exc:
            raise RuntimeError(
                "pymongo is required to use MongoProductRepository. Install dependencies from requirements.txt"
            ) from exc

        self.client = MongoClient(mongo_uri)
        self.collection = self.client[db_name][collection_name]
        self.collection.create_index("ProductID", unique=True)
        self.collection.create_index("Name")

    @staticmethod
    def _clean(document: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not document:
            return None
        document.pop("_id", None)
        return document

    def get_single_product(self, product_id: int) -> Optional[Dict[str, Any]]:
        return self._clean(self.collection.find_one({"ProductID": product_id}))

    def get_all_products(self) -> List[Dict[str, Any]]:
        return [self._clean(doc) for doc in self.collection.find({}, {"_id": 0}).sort("ProductID", 1)]

    def add_product(self, product: Dict[str, Any]) -> Dict[str, Any]:
        self.collection.insert_one(product)
        return product

    def delete_product(self, product_id: int) -> bool:
        result = self.collection.delete_one({"ProductID": product_id})
        return result.deleted_count > 0

    def starts_with(self, letter: str) -> List[Dict[str, Any]]:
        regex = f"^{letter}"
        return [self._clean(doc) for doc in self.collection.find({"Name": {"$regex": regex, "$options": "i"}}, {"_id": 0}).sort("ProductID", 1)]

    def paginate(self, start_id: int, end_id: int, batch_size: int = 10) -> List[Dict[str, Any]]:
        query = {"ProductID": {"$gte": start_id, "$lte": end_id}}
        return [self._clean(doc) for doc in self.collection.find(query, {"_id": 0}).sort("ProductID", 1).limit(batch_size)]
