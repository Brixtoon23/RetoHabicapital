from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from uuid import uuid4
from app.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False, index=True)
    amount_cents = Column(BigInteger, nullable=False)
    type = Column(String, nullable=False)  # deposit, transfer_in, transfer_out, pocket_in, pocket_out, pocket_refund
    description = Column(String, nullable=True)
    reference_id = Column(UUID(as_uuid=True), nullable=True)  # id de transferencia o bolsillo relacionado
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    account = relationship("Account", back_populates="transactions")