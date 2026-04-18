from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class CreatePocketRequest(BaseModel):
    name: str
    description: str | None = None
    goal_cents: int
    member_user_ids: list[UUID]  # usuarios invitados (sin incluir al creador)
    deadline: datetime | None = None

class ContributeRequest(BaseModel):
    amount_cents: int

class MemberStatusResponse(BaseModel):
    user_id: UUID
    target_cents: int
    status: str  # pending, partial, complete
    model_config = {"from_attributes": True}

class PocketStatusResponse(BaseModel):
    id: UUID
    name: str
    goal_cents: int
    collected_cents: int
    progress_pct: float
    status: str
    complete: list[MemberStatusResponse]
    partial: list[MemberStatusResponse]
    pending: list[MemberStatusResponse]