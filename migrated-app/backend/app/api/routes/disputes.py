"""
Dispute API routes.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.dispute import Dispute, DisputeStatus
from app.models.agent import Agent, ValidatedSteps
from app.schemas.dispute import DisputeCreate, DisputeUpdate, Dispute as DisputeSchema, DisputeListItem
from app.schemas.solution import Solution
from app.services.optimizer import OptimizationService
from app.services.blockchain_service import BlockchainService

router = APIRouter()
blockchain_service = BlockchainService()


@router.post("/", response_model=DisputeSchema, status_code=status.HTTP_201_CREATED)
async def create_dispute(
    dispute_data: DisputeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new dispute."""
    dispute = Dispute(
        owner_id=current_user.id,
        name=dispute_data.name,
        resolution_method=dispute_data.resolution_method,
        bounds_percentage=dispute_data.bounds_percentage,
        rating_weight=dispute_data.rating_weight,
    )

    db.add(dispute)
    await db.commit()
    await db.refresh(dispute, ["agents", "goods"])

    return dispute


@router.get("/", response_model=List[DisputeListItem])
async def list_disputes(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List disputes (owned or participating)."""
    # Get disputes where user is owner or agent
    result = await db.execute(
        select(Dispute)
        .join(Agent, Agent.dispute_id == Dispute.id, isouter=True)
        .where(
            (Dispute.owner_id == current_user.id) | (Agent.user_id == current_user.id)
        )
        .distinct()
        .options(selectinload(Dispute.agents), selectinload(Dispute.goods))
        .offset(skip)
        .limit(limit)
    )
    disputes = result.scalars().unique().all()

    # Add counts
    dispute_list = []
    for dispute in disputes:
        dispute_dict = DisputeListItem.model_validate(dispute)
        dispute_dict.agents_count = len(dispute.agents)
        dispute_dict.goods_count = len(dispute.goods)
        dispute_list.append(dispute_dict)

    return dispute_list


@router.get("/{dispute_id}", response_model=DisputeSchema)
async def get_dispute(
    dispute_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get dispute details."""
    result = await db.execute(
        select(Dispute)
        .options(
            selectinload(Dispute.agents).selectinload(Agent.user),
            selectinload(Dispute.goods),
        )
        .where(Dispute.id == dispute_id)
    )
    dispute = result.scalar_one_or_none()

    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")

    # Check authorization: owner or agent
    is_owner = dispute.owner_id == current_user.id
    is_agent = any(agent.user_id == current_user.id for agent in dispute.agents)

    if not (is_owner or is_agent):
        raise HTTPException(status_code=403, detail="Not authorized")

    return dispute


@router.put("/{dispute_id}", response_model=DisputeSchema)
async def update_dispute(
    dispute_id: str,
    dispute_data: DisputeUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update dispute (owner only)."""
    result = await db.execute(select(Dispute).where(Dispute.id == dispute_id))
    dispute = result.scalar_one_or_none()

    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")

    if dispute.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Update fields
    for field, value in dispute_data.model_dump(exclude_unset=True).items():
        setattr(dispute, field, value)

    await db.commit()
    await db.refresh(dispute, ["agents", "goods"])

    return dispute


@router.delete("/{dispute_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dispute(
    dispute_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete dispute (owner only)."""
    result = await db.execute(select(Dispute).where(Dispute.id == dispute_id))
    dispute = result.scalar_one_or_none()

    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")

    if dispute.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    await db.delete(dispute)
    await db.commit()


@router.post("/{dispute_id}/validate")
async def validate_dispute_setup(
    dispute_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Validate dispute setup and move to bidding phase."""
    result = await db.execute(
        select(Dispute)
        .options(selectinload(Dispute.agents), selectinload(Dispute.goods))
        .where(Dispute.id == dispute_id)
    )
    dispute = result.scalar_one_or_none()

    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")

    # Check if user is an agent
    current_agent = next(
        (a for a in dispute.agents if a.user_id == current_user.id), None
    )

    if not current_agent:
        raise HTTPException(status_code=403, detail="Not an agent of this dispute")

    # Mark agent as validated
    current_agent.validated = ValidatedSteps.SETUP
    dispute.status = DisputeStatus.BIDDING

    await db.commit()

    return {"message": "Dispute setup validated"}


@router.post("/{dispute_id}/solve", response_model=Solution)
async def solve_dispute(
    dispute_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Solve dispute using optimization."""
    result = await db.execute(select(Dispute).where(Dispute.id == dispute_id))
    dispute = result.scalar_one_or_none()

    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")

    if dispute.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only owner can solve dispute")

    if dispute.status != DisputeStatus.BIDDING:
        raise HTTPException(
            status_code=400,
            detail="Dispute must be in bidding status to solve",
        )

    # Run optimization
    optimizer = OptimizationService(db)
    solution = await optimizer.solve_dispute(str(dispute_id))

    # Update dispute status
    dispute.status = DisputeStatus.FINALIZING
    await db.commit()

    return solution


@router.post("/{dispute_id}/finalize")
async def finalize_dispute(
    dispute_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Finalize dispute and anchor to blockchain."""
    result = await db.execute(
        select(Dispute)
        .options(selectinload(Dispute.agents))
        .where(Dispute.id == dispute_id)
    )
    dispute = result.scalar_one_or_none()

    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")

    # Check if user is an agent
    current_agent = next(
        (a for a in dispute.agents if a.user_id == current_user.id), None
    )

    if not current_agent:
        raise HTTPException(status_code=403, detail="Not an agent of this dispute")

    # Mark agent agreement
    current_agent.validated = ValidatedSteps.AGREEMENT

    # Check if all agents agreed
    all_agreed = all(
        a.validated in [ValidatedSteps.AGREEMENT, ValidatedSteps.DISAGREEMENT]
        for a in dispute.agents
    )

    if all_agreed:
        dispute.status = DisputeStatus.FINALIZED

        # Anchor to blockchain if enabled
        if not dispute.block_id:
            block_id = await blockchain_service.anchor_data(
                owner=current_user.email,
                data={"dispute_id": str(dispute.id), "name": dispute.name},
            )
            if block_id:
                dispute.block_id = block_id

    await db.commit()

    return {"message": "Dispute finalized"}


@router.post("/{dispute_id}/reject")
async def reject_dispute(
    dispute_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Reject dispute solution."""
    result = await db.execute(
        select(Dispute)
        .options(selectinload(Dispute.agents))
        .where(Dispute.id == dispute_id)
    )
    dispute = result.scalar_one_or_none()

    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")

    # Check if user is an agent
    current_agent = next(
        (a for a in dispute.agents if a.user_id == current_user.id), None
    )

    if not current_agent:
        raise HTTPException(status_code=403, detail="Not an agent of this dispute")

    # Mark disagreement
    current_agent.validated = ValidatedSteps.DISAGREEMENT
    dispute.status = DisputeStatus.REJECTED

    await db.commit()

    return {"message": "Dispute rejected"}
