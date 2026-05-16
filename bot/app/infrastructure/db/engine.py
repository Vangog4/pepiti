from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from app.core.config import settings

def create_db_engine() -> AsyncEngine:
    return create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )
