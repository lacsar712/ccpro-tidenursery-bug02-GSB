from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.hatchery import Hatchery
from app.models.user import User
from app.schemas.hatchery import HatcheryCreate, HatcheryUpdate, HatcheryOut

router = APIRouter(prefix="/api/hatcheries", tags=["hatcheries"])


@router.get("", response_model=List[HatcheryOut])
def list_hatcheries(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return db.query(Hatchery).order_by(Hatchery.id).all()


@router.post("", response_model=HatcheryOut, status_code=status.HTTP_201_CREATED)
def create_hatchery(
    payload: HatcheryCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    item = Hatchery(
        name=payload.name,
        seawater_source=payload.seawater_source,
        notes=payload.notes,
    )
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="育苗场名称已存在")
    db.refresh(item)
    return item


@router.get("/{hatchery_id}", response_model=HatcheryOut)
def get_hatchery(
    hatchery_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    item = db.query(Hatchery).filter(Hatchery.id == hatchery_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="育苗场不存在")
    return item


@router.put("/{hatchery_id}", response_model=HatcheryOut)
def update_hatchery(
    hatchery_id: int,
    payload: HatcheryUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    item = db.query(Hatchery).filter(Hatchery.id == hatchery_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="育苗场不存在")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(item, k, v)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="育苗场名称已存在")
    db.refresh(item)
    return item


@router.delete("/{hatchery_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hatchery(
    hatchery_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    item = db.query(Hatchery).filter(Hatchery.id == hatchery_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="育苗场不存在")
    db.delete(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="该育苗场下仍有塘口，无法删除")
