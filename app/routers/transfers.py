from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.account import Account
from app.models.user import User
from app.models.transaction import Transaction
from app.schemas.account import TransferRequest
from app.models.user import User

router = APIRouter()

@router.post("/", status_code=201)
def transfer(data: TransferRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if data.amount_cents <= 0:
        raise HTTPException(400, "El monto debe ser positivo")

    destination_user = db.query(User).filter(User.email == data.to_mail_id).first()
    if not destination_user:
        raise HTTPException(404, "No existe un usuario con ese correo")

    origin = db.query(Account).filter(Account.user_id == current_user.id).with_for_update().first()
    destination = db.query(Account).filter(Account.user_id == destination_user.id).with_for_update().first()

    if origin.id == destination.id:
        raise HTTPException(400, "No puedes transferirte a ti mismo")
    if origin.balance_cents < data.amount_cents:
        raise HTTPException(400, "Saldo insuficiente")

    origin.balance_cents -= data.amount_cents
    destination.balance_cents += data.amount_cents

    desc = data.description or "Transferencia"
    db.add(Transaction(account_id=origin.id, amount_cents=-data.amount_cents, type="transfer_out", description=desc, reference_id=destination.id))
    db.add(Transaction(account_id=destination.id, amount_cents=data.amount_cents, type="transfer_in", description=desc, reference_id=origin.id))

    db.commit()
    return {
        "message": "Transferencia exitosa",
        "to": destination_user.email,
        "amount_cents": data.amount_cents
    }