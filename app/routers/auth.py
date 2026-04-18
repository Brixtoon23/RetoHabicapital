from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, EmailStr
from app.database import get_db
from app.models.user import User
from app.models.account import Account
from app.dependencies import SECRET_KEY, ALGORITHM

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

@router.post("/register", status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(400, "Email ya registrado")
    user = User(name=data.name, email=data.email, password_hash=pwd_context.hash(data.password))
    db.add(user)
    db.flush()  # genera el user.id sin hacer commit aún
    account = Account(user_id=user.id, balance_cents=0)
    db.add(account)
    db.commit()
    return {"user_id": user.id, "message": "Usuario creado"}

@router.post("/token")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not pwd_context.verify(form.password, user.password_hash):
        raise HTTPException(401, "Credenciales inválidas")
    token = jwt.encode(
        {"sub": str(user.id), "exp": datetime.now(timezone.utc) + timedelta(hours=24)},
        SECRET_KEY, algorithm=ALGORITHM
    )
    return {"access_token": token, "token_type": "bearer"}