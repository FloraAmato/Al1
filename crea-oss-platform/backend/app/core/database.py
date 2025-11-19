"""
Database configuration and session management using SQLAlchemy.
"""
from typing import AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


# Convert sync postgres URL to async if needed
def get_async_database_url(url: str) -> str:
    """Convert PostgreSQL URL to async version."""
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql+psycopg2://"):
        return url.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
    return url


# Database URLs
SYNC_DATABASE_URL = settings.database_url
ASYNC_DATABASE_URL = get_async_database_url(settings.database_url)


# Sync engine (for Alembic migrations)
sync_engine = create_engine(
    SYNC_DATABASE_URL,
    echo=settings.database_echo,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

# Async engine (for FastAPI app)
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=settings.database_echo,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

# Session makers
SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# Base class for models
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


# Dependency for FastAPI routes (sync)
def get_db() -> Session:
    """Dependency to get a synchronous database session."""
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Dependency for FastAPI routes (async)
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get an asynchronous database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
