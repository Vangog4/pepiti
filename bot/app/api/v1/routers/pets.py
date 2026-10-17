from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes import _validate_pet
from app.api.v1.dependencies import get_current_user, get_db_session
from app.api.v1.schemas.pet import PetCreateRequest, PetResponse, PetUpdateRequest
from app.infrastructure.db.models.pet import PetModel
from app.infrastructure.db.models.user import UserModel

router = APIRouter(prefix="/pets", tags=["Pets"])


def _to_pet_response(pet: PetModel) -> PetResponse:
    return PetResponse(
        id=pet.id,
        user_id=pet.user_id,
        name=pet.name,
        breed=pet.breed,
        sex=pet.sex,
        age_category=pet.age_category,
        age_months=pet.age_months,
        size_category=pet.size_category,
        weight_kg=pet.weight_kg,
        training_level=pet.training_level,
        temperament=pet.temperament,
        behavior_issues=pet.behavior_issues,
        goal=pet.goal,
        energy_level=pet.energy_level,
        health_notes=pet.health_notes,
        training_days=pet.training_days or 0,
        created_at=pet.created_at,
        updated_at=pet.updated_at,
    )


@router.get("", response_model=list[PetResponse], summary="List all pets of the current user")
async def list_pets(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[PetResponse]:
    stmt = select(PetModel).where(PetModel.user_id == current_user.id).order_id = (
        PetModel.id if hasattr(PetModel, "id") else None
    )
    stmt = select(PetModel).where(PetModel.user_id == current_user.id).order_by(PetModel.id)
    res = await session.execute(stmt)
    pets = res.scalars().all()
    return [_to_pet_response(p) for p in pets]


@router.post(
    "", response_model=PetResponse, status_code=status.HTTP_201_CREATED, summary="Create a new pet"
)
async def create_pet(
    body: PetCreateRequest,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> PetResponse:
    errors = _validate_pet(body.model_dump(), current_user.language_code or "ru")
    if errors:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=errors)

    pet = PetModel(
        user_id=current_user.id,
        name=body.name.strip(),
        breed=body.breed.strip() if body.breed else None,
        sex=body.sex.strip() if body.sex else None,
        age_category=body.age_category,
        age_months=body.age_months,
        size_category=body.size_category,
        weight_kg=body.weight_kg,
        training_level=body.training_level,
        temperament=body.temperament,
        behavior_issues=body.behavior_issues,
        goal=body.goal,
        energy_level=body.energy_level,
        health_notes=body.health_notes,
    )
    session.add(pet)
    await session.commit()
    await session.refresh(pet)
    return _to_pet_response(pet)


@router.get("/{pet_id}", response_model=PetResponse, summary="Get pet details by ID")
async def get_pet(
    pet_id: int,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> PetResponse:
    stmt = select(PetModel).where(PetModel.id == pet_id, PetModel.user_id == current_user.id)
    res = await session.execute(stmt)
    pet = res.scalar_one_or_none()
    if pet is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pet not found")
    return _to_pet_response(pet)


@router.patch("/{pet_id}", response_model=PetResponse, summary="Update pet profile")
async def update_pet(
    pet_id: int,
    body: PetUpdateRequest,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> PetResponse:
    stmt = select(PetModel).where(PetModel.id == pet_id, PetModel.user_id == current_user.id)
    res = await session.execute(stmt)
    pet = res.scalar_one_or_none()
    if pet is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pet not found")

    dump = body.model_dump(exclude_unset=True)
    if "name" in dump or "breed" in dump or "goal" in dump or "training_level" in dump:
        errors = _validate_pet(dump, current_user.language_code or "ru")
        if errors:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=errors)

    for field, val in dump.items():
        if isinstance(val, str):
            val = val.strip()
        setattr(pet, field, val)

    await session.commit()
    await session.refresh(pet)
    return _to_pet_response(pet)


@router.delete("/{pet_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete pet")
async def delete_pet(
    pet_id: int,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> None:
    stmt = select(PetModel).where(PetModel.id == pet_id, PetModel.user_id == current_user.id)
    res = await session.execute(stmt)
    pet = res.scalar_one_or_none()
    if pet is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pet not found")

    from sqlalchemy import delete

    from app.infrastructure.db.models.ai_conversation import AiConversationModel
    from app.infrastructure.db.models.training import TrainingPlanModel, TrainingTaskModel

    plan_ids_res = await session.execute(
        select(TrainingPlanModel.id).where(TrainingPlanModel.pet_id == pet.id)
    )
    plan_ids = list(plan_ids_res.scalars().all())
    if plan_ids:
        await session.execute(
            delete(TrainingTaskModel).where(TrainingTaskModel.plan_id.in_(plan_ids))
        )

    await session.execute(delete(TrainingPlanModel).where(TrainingPlanModel.pet_id == pet.id))
    await session.execute(delete(AiConversationModel).where(AiConversationModel.pet_id == pet.id))

    await session.delete(pet)
    await session.commit()
