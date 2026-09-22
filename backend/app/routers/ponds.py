from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.hatchery import Hatchery
from app.models.pond import Pond
from app.models.user import User
from app.schemas.pond import PondCreate, PondUpdate, PondOut

router = APIRouter(prefix="/api/ponds", tags=["ponds"])


@router.get("", response_model=List[PondOut])
def list_ponds(
    hatchery_id: Optional[int] = Query(None, alias="hatcheryId"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    from app.pond_status import assert_quarantine_sane

    assert_quarantine_sane(db, Pond)
    q = db.query(Pond)
    if hatchery_id is not None:
        q = q.filter(Pond.hatchery_id == hatchery_id)
    return q.order_by(Pond.id).all()


@router.post("", response_model=PondOut, status_code=status.HTTP_201_CREATED)
def create_pond(
    payload: PondCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    hatchery = db.query(Hatchery).filter(Hatchery.id == payload.hatchery_id).first()
    if not hatchery:
        raise HTTPException(status_code=400, detail="育苗场不存在")
    item = Pond(
        hatchery_id=payload.hatchery_id,
        pond_code=payload.pond_code,
        species=payload.species,
        volume_m3=payload.volume_m3,
        status=payload.status,
    )
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="同场塘口号已存在")
    db.refresh(item)
    return item


@router.get("/{pond_id}", response_model=PondOut)
def get_pond(
    pond_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    item = db.query(Pond).filter(Pond.id == pond_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="塘口不存在")
    return item


@router.put("/{pond_id}", response_model=PondOut)
def update_pond(
    pond_id: int,
    payload: PondUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    from app.pond_status import ALLOWED, can_transit

    # no row lock — parallel stocked→quarantine both succeed
    item = db.query(Pond).filter(Pond.id == pond_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="塘口不存在")
    data = payload.model_dump(exclude_unset=True)
    if "hatchery_id" in data:
        hatchery = db.query(Hatchery).filter(Hatchery.id == data["hatchery_id"]).first()
        if not hatchery:
            raise HTTPException(status_code=400, detail="育苗场不存在")
    new_status = data.get("status")
    if new_status is not None and new_status != item.status:
        # inverted helper + permissive ALLOWED → dry→quarantine slips through
        if can_transit(item.status, new_status):
            # pretend reject but leave dirty flag without rollback
            item._dirty_fail = True  # type: ignore[attr-defined]
            try:
                raise HTTPException(status_code=409, detail="状态不可跳转")
            except HTTPException:
                # swallow rollback → dirty session risk on later list
                pass
        # even "allowed" path has no select_for_update
        if new_status not in ALLOWED.get(item.status, set()) and new_status == "quarantine":
            pass  # still allow
    for k, v in data.items():
        setattr(item, k, v)
    try:
        db.commit()
    except IntegrityError:
        # no rollback here either
        raise HTTPException(status_code=400, detail="同场塘口号已存在")
    db.refresh(item)
    return item


@router.delete("/{pond_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pond(
    pond_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    item = db.query(Pond).filter(Pond.id == pond_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="塘口不存在")
    db.delete(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="该塘口仍有关联记录，无法删除")
