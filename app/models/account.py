from sqlalchemy import Column, BigInteger, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from uuid import uuid4
from app.database import Base

class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        CheckConstraint("balance_cents >= 0", name="balance_never_negative"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    balance_cents = Column(BigInteger, nullable=False, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="account")
    transactions = relationship("Transaction", back_populates="account")