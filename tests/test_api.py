from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.dependencies import get_repository
from app.repository import InMemoryProductRepository
import app.main as main_module


def make_repo() -> InMemoryProductRepository:
    return InMemoryProductRepository(
        [
            {"ProductID": 1001, "Name": "RTX 4090", "UnitPrice": 1599.99, "StockQuantity": 5, "Description": "GPU"},
            {"ProductID": 1002, "Name": "Ryzen 9 7950X", "UnitPrice": 699.99, "StockQuantity": 8, "Description": "CPU"},
            {"ProductID": 1003, "Name": "Samsung SSD", "UnitPrice": 149.99, "StockQuantity": 22, "Description": "SSD"},
            {"ProductID": 1004, "Name": "Seasonic PSU", "UnitPrice": 179.99, "StockQuantity": 9, "Description": "Power supply"},
        ]
    )


def setup_function() -> None:
    app.dependency_overrides[get_repository] = make_repo


def teardown_function() -> None:
    app.dependency_overrides.clear()


def test_get_single_product_success() -> None:
    client = TestClient(app)
    response = client.get("/getSingleProduct", params={"productId": 1001})
    assert response.status_code == 200
    assert response.json()["ProductID"] == 1001


def test_get_single_product_not_found() -> None:
    client = TestClient(app)
    response = client.get("/getSingleProduct", params={"productId": 9999})
    assert response.status_code == 404


def test_get_all_returns_all_products() -> None:
    client = TestClient(app)
    response = client.get("/getAll")
    assert response.status_code == 200
    assert len(response.json()) == 4


def test_add_new_success() -> None:
    client = TestClient(app)
    payload = {
        "ProductID": 2001,
        "Name": "Logitech Mouse",
        "UnitPrice": 59.99,
        "StockQuantity": 30,
        "Description": "Gaming mouse",
    }
    response = client.post("/addNew", json=payload)
    assert response.status_code == 201
    assert response.json()["ProductID"] == 2001


def test_add_new_duplicate_product_id() -> None:
    client = TestClient(app)
    payload = {
        "ProductID": 1001,
        "Name": "Duplicate GPU",
        "UnitPrice": 10.00,
        "StockQuantity": 1,
        "Description": "Duplicate",
    }
    response = client.post("/addNew", json=payload)
    assert response.status_code == 409


def test_delete_one_success() -> None:
    client = TestClient(app)
    response = client.delete("/deleteOne", params={"productId": 1002})
    assert response.status_code == 200
    assert response.json()["deleted_product_id"] == 1002


def test_starts_with() -> None:
    client = TestClient(app)
    response = client.get("/startsWith", params={"letter": "S"})
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_paginate_returns_batch_of_matching_products() -> None:
    client = TestClient(app)
    response = client.get("/paginate", params={"startProductId": 1001, "endProductId": 1004})
    assert response.status_code == 200
    assert len(response.json()) == 4


def test_paginate_rejects_invalid_range() -> None:
    client = TestClient(app)
    response = client.get("/paginate", params={"startProductId": 1005, "endProductId": 1001})
    assert response.status_code == 422


def test_convert_uses_online_rate(monkeypatch) -> None:
    def fake_fetch(_: str) -> tuple[float, str]:
        return 0.92, "mock-provider"

    monkeypatch.setattr(main_module, "fetch_usd_to_eur_rate", fake_fetch)
    client = TestClient(app)
    response = client.get("/convert", params={"productId": 1001})
    assert response.status_code == 200
    body = response.json()
    assert body["product_id"] == 1001
    assert body["converted_price_eur"] == round(1599.99 * 0.92, 2)
