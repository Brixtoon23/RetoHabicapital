from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, accounts, transfers, pockets

app = FastAPI(
    title="HabiCapital Reto — Billetera P2P",
    description="Sistema de transferencias entre personas con bolsillos de ahorro colectivo",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
app.include_router(transfers.router, prefix="/transfers", tags=["transfers"])
app.include_router(pockets.router, prefix="/pockets", tags=["bolsillos"])

@app.get("/", tags=["health"])
def health():
    return {"status": "ok", "service": "habicapital-reto"}