from pydantic import BaseModel
import os


class Settings(BaseModel):
    app_name: str = "Inventory Management API"
    mongo_uri: str = os.getenv("MONGO_URI", "mongodb://mongo:27017")
    mongo_db_name: str = os.getenv("MONGO_DB_NAME", "inventory_db")
    mongo_collection_name: str = os.getenv("MONGO_COLLECTION_NAME", "products")
    exchange_rate_url: str = os.getenv("EXCHANGE_RATE_URL", "https://open.er-api.com/v6/latest/USD")
    docs_url: str = "/docs"


settings = Settings()
