from typing import Annotated
from pydantic import BaseModel, Field, PositiveInt, ConfigDict, field_validator


class ProductBase(BaseModel):
    product_id: PositiveInt = Field(..., alias="ProductID", description="Unique product ID")
    name: str = Field(..., alias="Name", min_length=1, max_length=200)
    unit_price: float = Field(..., alias="UnitPrice", gt=0)
    stock_quantity: int = Field(..., alias="StockQuantity", ge=0)
    description: str = Field(..., alias="Description", min_length=1, max_length=1000)

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    @field_validator("name", "description")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    pass


class DeleteResponse(BaseModel):
    message: str
    deleted_product_id: PositiveInt


class ConvertResponse(BaseModel):
    product_id: PositiveInt
    name: str
    unit_price_usd: float
    exchange_rate_usd_to_eur: float
    converted_price_eur: float
    rate_provider: str


class ApiMessage(BaseModel):
    message: str


PositiveProductId = Annotated[int, Field(gt=0)]
