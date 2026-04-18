from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.pocket import SavingPocket, PocketMember, PocketContribution
from app.models.user import User
from app.schemas.pocket import (
    CreatePocketRequest, ContributeRequest,
    PocketStatusResponse, MemberStatusResponse
)
from uuid import UUID

router = APIRouter()


@router.post("/", status_code=201)
def create_pocket(
    data: CreatePocketRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    all_member_ids = list(set(data.member_user_ids))
    n_members = len(all_member_ids) + 1  # +1 por el creador
    target_per_member = data.goal_cents // n_members

    pocket = SavingPocket(
        creator_id=current_user.id,
        name=data.name,
        description=data.description,
        goal_cents=data.goal_cents,
        deadline=data.deadline,
    )
    db.add(pocket)
    db.flush()

    creator_member = PocketMember(
        pocket_id=pocket.id,
        user_id=current_user.id,
        target_cents=target_per_member,
    )
    db.add(creator_member)

    for uid in all_member_ids:
        user = db.query(User).filter(User.id == uid).first()
        if not user:
            db.rollback()
            raise HTTPException(404, f"Usuario {uid} no encontrado")
        db.add(PocketMember(
            pocket_id=pocket.id,
            user_id=uid,
            target_cents=target_per_member,
        ))

    db.commit()
    db.refresh(pocket)
    return {
        "pocket_id": pocket.id,
        "name": pocket.name,
        "goal_cents": pocket.goal_cents,
        "target_per_member_cents": target_per_member,
        "n_members": n_members,
    }


@router.post("/{pocket_id}/contribute", status_code=200)
def contribute(
    pocket_id: UUID,
    data: ContributeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if data.amount_cents <= 0:
        raise HTTPException(400, "El monto debe ser positivo")

    pocket = db.query(SavingPocket).filter(
        SavingPocket.id == pocket_id
    ).with_for_update().first()

    if not pocket:
        raise HTTPException(404, "Bolsillo no encontrado")
    if pocket.status != "open":
        raise HTTPException(400, f"El bolsillo está {pocket.status}")

    member = db.query(PocketMember).filter(
        PocketMember.pocket_id == pocket_id,
        PocketMember.user_id == current_user.id
    ).first()

    if not member:
        raise HTTPException(403, "No eres miembro de este bolsillo")

    account = db.query(Account).filter(
        Account.user_id == current_user.id
    ).with_for_update().first()

    if account.balance_cents < data.amount_cents:
        raise HTTPException(400, "Saldo insuficiente")

    account.balance_cents -= data.amount_cents
    pocket.collected_cents += data.amount_cents

    contribution = PocketContribution(
        pocket_id=pocket.id,
        account_id=account.id,
        member_id=member.id,
        amount_cents=data.amount_cents,
    )
    db.add(contribution)

    db.add(Transaction(
        account_id=account.id,
        amount_cents=-data.amount_cents,
        type="pocket_out",
        description=f"Aporte a bolsillo: {pocket.name}",
        reference_id=pocket.id,
    ))

    total_contributed = sum(
        c.amount_cents for c in db.query(PocketContribution).filter(
            PocketContribution.member_id == member.id,
            PocketContribution.pocket_id == pocket_id,
        ).all()
    ) + data.amount_cents

    member.status = "complete" if total_contributed >= member.target_cents else "partial"

    if pocket.collected_cents >= pocket.goal_cents:
        pocket.status = "completed"

    db.commit()
    return {
        "message": "Aporte registrado",
        "contributed_cents": data.amount_cents,
        "total_contributed_cents": total_contributed,
        "member_status": member.status,
        "pocket_status": pocket.status,
        "pocket_progress_pct": round(pocket.collected_cents / pocket.goal_cents * 100, 1),
    }


@router.get("/{pocket_id}/status", response_model=PocketStatusResponse)
def pocket_status(
    pocket_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pocket = db.query(SavingPocket).filter(SavingPocket.id == pocket_id).first()
    if not pocket:
        raise HTTPException(404, "Bolsillo no encontrado")

    is_member = db.query(PocketMember).filter(
        PocketMember.pocket_id == pocket_id,
        PocketMember.user_id == current_user.id
    ).first()
    if not is_member:
        raise HTTPException(403, "No tienes acceso a este bolsillo")

    members = db.query(PocketMember).filter(PocketMember.pocket_id == pocket_id).all()

    def to_response(m):
        return MemberStatusResponse(
            user_id=m.user_id,
            target_cents=m.target_cents,
            status=m.status,
        )

    return PocketStatusResponse(
        id=pocket.id,
        name=pocket.name,
        goal_cents=pocket.goal_cents,
        collected_cents=pocket.collected_cents,
        progress_pct=round(pocket.collected_cents / pocket.goal_cents * 100, 1),
        status=pocket.status,
        complete=[to_response(m) for m in members if m.status == "complete"],
        partial=[to_response(m) for m in members if m.status == "partial"],
        pending=[to_response(m) for m in members if m.status == "pending"],
    )


@router.post("/{pocket_id}/cancel", status_code=200)
def cancel_pocket(
    pocket_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pocket = db.query(SavingPocket).filter(
        SavingPocket.id == pocket_id,
        SavingPocket.creator_id == current_user.id
    ).with_for_update().first()

    if not pocket:
        raise HTTPException(404, "Bolsillo no encontrado o no eres el creador")
    if pocket.status == "cancelled":
        raise HTTPException(400, "El bolsillo ya está cancelado")

    contributions = db.query(PocketContribution).filter(
        PocketContribution.pocket_id == pocket_id
    ).all()

    refunded_users = {}
    for contrib in contributions:
        account = db.query(Account).filter(
            Account.id == contrib.account_id
        ).with_for_update().first()

        account.balance_cents += contrib.amount_cents

        db.add(Transaction(
            account_id=account.id,
            amount_cents=contrib.amount_cents,
            type="pocket_refund",
            description=f"Devolución bolsillo cancelado: {pocket.name}",
            reference_id=pocket.id,
        ))

        refunded_users[str(contrib.account_id)] = (
            refunded_users.get(str(contrib.account_id), 0) + contrib.amount_cents
        )

    pocket.status = "cancelled"
    pocket.collected_cents = 0

    members = db.query(PocketMember).filter(PocketMember.pocket_id == pocket_id).all()
    for m in members:
        m.status = "pending"

    db.commit()
    return {
        "message": "Bolsillo cancelado. Todas las contribuciones fueron devueltas.",
        "total_refunded_cents": sum(refunded_users.values()),
        "refunds_issued": len(refunded_users),
    }


@router.post("/{pocket_id}/disburse", status_code=200)
def disburse_pocket(
    pocket_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pocket = db.query(SavingPocket).filter(
        SavingPocket.id == pocket_id,
        SavingPocket.creator_id == current_user.id
    ).with_for_update().first()

    if not pocket:
        raise HTTPException(404, "Bolsillo no encontrado o no eres el creador")
    if pocket.status != "completed":
        raise HTTPException(400, f"El bolsillo debe estar completado para desembolsar (estado actual: {pocket.status})")

    creator_account = db.query(Account).filter(
        Account.user_id == current_user.id
    ).with_for_update().first()

    amount = pocket.collected_cents
    creator_account.balance_cents += amount

    db.add(Transaction(
        account_id=creator_account.id,
        amount_cents=amount,
        type="pocket_in",
        description=f"Desembolso bolsillo: {pocket.name}",
        reference_id=pocket.id,
    ))

    pocket.status = "cancelled"
    pocket.collected_cents = 0

    db.commit()
    return {
        "message": "Fondos desembolsados al creador",
        "disbursed_cents": amount,
    }