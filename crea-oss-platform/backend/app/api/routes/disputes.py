"""Dispute management API routes."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_async_db
from app.models import Dispute, Agent, Good
from app.schemas.dispute import DisputeCreate, DisputeRead, DisputeUpdate
from app.schemas.solution import SolveRequest, SolutionRead
from app.services import OptimizerService

router = APIRouter(prefix="/disputes", tags=["disputes"])


@router.post("/", response_model=DisputeRead)
async def create_dispute(
    dispute_data: DisputeCreate,
    db: AsyncSession = Depends(get_async_db),
):
    """Create a new dispute."""
    # For demo, use fixed owner_id=1
    owner_id = 1

    try:
        # Create dispute
        dispute = Dispute(
            owner_id=owner_id,
            name=dispute_data.name,
            resolution_method=dispute_data.resolution_method,
            bounds_percentage=dispute_data.bounds_percentage,
            rating_weight=dispute_data.rating_weight,
        )
        db.add(dispute)
        await db.flush()

        # Create agents
        for agent_data in dispute_data.agents:
            agent = Agent(
                dispute_id=dispute.id,
                email=agent_data.email,
                name=agent_data.name,
                share_of_entitlement=agent_data.share_of_entitlement,
            )
            db.add(agent)

        # Create goods
        for good_data in dispute_data.goods:
            good = Good(
                dispute_id=dispute.id,
                name=good_data.name,
                estimated_value=good_data.estimated_value,
                indivisible=good_data.indivisible,
            )
            db.add(good)

        await db.commit()
        await db.refresh(dispute)

        return dispute

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{dispute_id}", response_model=DisputeRead)
async def get_dispute(
    dispute_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    """Get a dispute by ID."""
    result = await db.execute(
        select(Dispute).where(Dispute.id == dispute_id)
    )
    dispute = result.scalar_one_or_none()

    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")

    return dispute


@router.post("/{dispute_id}/solve", response_model=SolutionRead)
async def solve_dispute(
    dispute_id: int,
    request: SolveRequest,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Solve a dispute using the specified algorithm.

    Methods: "maxmin" or "nash"
    """
    try:
        service = OptimizerService(db)

        if request.method == "maxmin":
            solution = await service.run_maxmin(dispute_id)
        elif request.method == "nash":
            solution = await service.run_nash(dispute_id)
        else:
            raise HTTPException(status_code=400, detail="Invalid method")

        return solution

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
