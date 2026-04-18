from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.account import Account
from app.models.transaction import Transaction
from app.schemas.account import DepositRequest, AccountResponse, TransactionResponse
from app.models.user import User

router = APIRouter()

@router.post("/deposit", response_model=AccountResponse)
def deposit(data: DepositRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if data.amount_cents <= 0:
        raise HTTPException(400, "El monto debe ser positivo")
    account = db.query(Account).filter(Account.user_id == current_user.id).first()
    account.balance_cents += data.amount_cents
    db.add(Transaction(account_id=account.id, amount_cents=data.amount_cents, type="deposit", description="Carga de saldo"))
    db.commit()
    db.refresh(account)
    return account

@router.get("/balance", response_model=AccountResponse)
def balance(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    account = db.query(Account).filter(Account.user_id == current_user.id).first()
    return account

@router.get("/history", response_model=list[TransactionResponse])
def history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    account = db.query(Account).filter(Account.user_id == current_user.id).first()
    return db.query(Transaction).filter(Transaction.account_id == account.id).order_by(Transaction.created_at.desc()).limit(50).all()