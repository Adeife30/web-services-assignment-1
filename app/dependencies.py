from functools import lru_cache
from .config import settings
from .repository import MongoProductRepository, ProductRepository


@lru_cache(maxsize=1)
def get_repository() -> ProductRepository:
    return MongoProductRepository(
        mongo_uri=settings.mongo_uri,
        db_name=settings.mongo_db_name,
        collection_name=settings.mongo_collection_name,
    )
