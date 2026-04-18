from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from uuid import uuid4
from app.database import Base

class SavingPocket(Base):
    __tablename__ = "saving_pockets"
    __table_args__ = (
        CheckConstraint("collected_cents >= 0", name="collected_never_negative"),
        CheckConstraint("goal_cents > 0", name="goal_must_be_positive"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    goal_cents = Column(BigInteger, nullable=False)
    collected_cents = Column(BigInteger, nullable=False, default=0)
    status = Column(String, nullable=False, default="open")  # open, completed, cancelled, expired
    deadline = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    members = relationship("PocketMember", back_populates="pocket")
    contributions = relationship("PocketContribution", back_populates="pocket")


class PocketMember(Base):
    __tablename__ = "pocket_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    pocket_id = Column(UUID(as_uuid=True), ForeignKey("saving_pockets.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    target_cents = Column(BigInteger, nullable=False)  # goal_cents / n_members
    status = Column(String, nullable=False, default="pending")  # pending, partial, complete
    joined_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    pocket = relationship("SavingPocket", back_populates="members")
    contributions = relationship("PocketContribution", back_populates="member")


class PocketContribution(Base):
    __tablename__ = "pocket_contributions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    pocket_id = Column(UUID(as_uuid=True), ForeignKey("saving_pockets.id"), nullable=False, index=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    member_id = Column(UUID(as_uuid=True), ForeignKey("pocket_members.id"), nullable=False)
    amount_cents = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    pocket = relationship("SavingPocket", back_populates="contributions")
    member = relationship("PocketMember", back_populates="contributions")