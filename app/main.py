from __future__ import annotations

from typing import Annotated, List

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import PositiveInt

from .config import settings
from .dependencies import get_repository
from .models import ApiMessage, ConvertResponse, DeleteResponse, ProductCreate, ProductResponse
from .repository import ProductRepository
from .services import fetch_usd_to_eur_rate

app = FastAPI(title=settings.app_name)


@app.get("/", response_model=ApiMessage)
def root() -> ApiMessage:
    return ApiMessage(message="Inventory Management API is running")


@app.get("/getSingleProduct", response_model=ProductResponse)
def get_single_product(
    product_id: Annotated[PositiveInt, Query(alias="productId")],
    repo: ProductRepository = Depends(get_repository),
) -> ProductResponse:
    product = repo.get_single_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductResponse.model_validate(product)


@app.get("/getAll", response_model=List[ProductResponse])
def get_all_products(repo: ProductRepository = Depends(get_repository)) -> List[ProductResponse]:
    return [ProductResponse.model_validate(product) for product in repo.get_all_products()]


@app.post("/addNew", response_model=ProductResponse, status_code=201)
def add_new_product(
    product: ProductCreate,
    repo: ProductRepository = Depends(get_repository),
) -> ProductResponse:
    try:
        inserted = repo.add_product(product.model_dump(by_alias=True))
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except Exception as exc:
        if "duplicate key" in str(exc).lower():
            raise HTTPException(status_code=409, detail="Product ID already exists") from exc
        raise
    return ProductResponse.model_validate(inserted)


@app.delete("/deleteOne", response_model=DeleteResponse)
def delete_one_product(
    product_id: Annotated[PositiveInt, Query(alias="productId")],
    repo: ProductRepository = Depends(get_repository),
) -> DeleteResponse:
    deleted = repo.delete_product(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    return DeleteResponse(message="Product deleted successfully", deleted_product_id=product_id)


@app.get("/startsWith", response_model=List[ProductResponse])
def starts_with(
    letter: Annotated[str, Query(min_length=1, max_length=1)],
    repo: ProductRepository = Depends(get_repository),
) -> List[ProductResponse]:
    return [ProductResponse.model_validate(product) for product in repo.starts_with(letter)]


@app.get("/paginate", response_model=List[ProductResponse])
def paginate_products(
    start_product_id: Annotated[PositiveInt, Query(alias="startProductId")],
    end_product_id: Annotated[PositiveInt, Query(alias="endProductId")],
    repo: ProductRepository = Depends(get_repository),
) -> List[ProductResponse]:
    if end_product_id < start_product_id:
        raise HTTPException(status_code=422, detail="endProductId must be greater than or equal to startProductId")

    products = repo.paginate(start_product_id, end_product_id, batch_size=10)
    return [ProductResponse.model_validate(product) for product in products]


@app.get("/convert", response_model=ConvertResponse)
def convert_price_to_eur(
    product_id: Annotated[PositiveInt, Query(alias="productId")],
    repo: ProductRepository = Depends(get_repository),
) -> ConvertResponse:
    product = repo.get_single_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    eur_rate, provider = fetch_usd_to_eur_rate(settings.exchange_rate_url)
    converted_price = round(float(product["UnitPrice"]) * eur_rate, 2)

    return ConvertResponse(
        product_id=product["ProductID"],
        name=product["Name"],
        unit_price_usd=round(float(product["UnitPrice"]), 2),
        exchange_rate_usd_to_eur=eur_rate,
        converted_price_eur=converted_price,
        rate_provider=provider,
    )
