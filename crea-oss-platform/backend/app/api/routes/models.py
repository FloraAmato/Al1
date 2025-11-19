"""Model configuration API routes."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_async_db
from app.models import ModelConfig
from app.schemas.model_config import ModelConfigCreate, ModelConfigRead, ModelConfigUpdate

router = APIRouter(prefix="/models", tags=["models"])


@router.post("/", response_model=ModelConfigRead)
async def create_model_config(
    config_data: ModelConfigCreate,
    db: AsyncSession = Depends(get_async_db),
):
    """Register a new model configuration."""
    try:
        # If set as default, unset other defaults
        if config_data.is_default:
            await db.execute(
                select(ModelConfig).where(ModelConfig.is_default == True)
            )
            # (In production, update these to is_default=False)

        config = ModelConfig(**config_data.dict())
        db.add(config)
        await db.commit()
        await db.refresh(config)

        return config

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[ModelConfigRead])
async def list_models(
    db: AsyncSession = Depends(get_async_db),
):
    """List all available model configurations."""
    result = await db.execute(
        select(ModelConfig).where(ModelConfig.is_active == True)
    )
    configs = result.scalars().all()
    return list(configs)


@router.get("/{config_id}", response_model=ModelConfigRead)
async def get_model_config(
    config_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    """Get a model configuration by ID."""
    result = await db.execute(
        select(ModelConfig).where(ModelConfig.id == config_id)
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(status_code=404, detail="Model config not found")

    return config
