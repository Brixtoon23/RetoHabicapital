from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class DepositRequest(BaseModel):
    amount_cents: int

class TransferRequest(BaseModel):
    to_account_id: UUID
    amount_cents: int
    description: str | None = None

class AccountResponse(BaseModel):
    id: UUID
    balance_cents: int
    created_at: datetime
    model_config = {"from_attributes": True}

class TransactionResponse(BaseModel):
    id: UUID
    amount_cents: int
    type: str
    description: str | None
    created_at: datetime
    model_config = {"from_attributes": True}