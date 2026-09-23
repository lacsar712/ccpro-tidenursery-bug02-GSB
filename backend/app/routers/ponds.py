from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.hatchery import Hatchery
from app.models.pond import Pond
from app.models.user import User
from app.pond_status import can_transit, transit_reason
from app.schemas.pond import PondCreate, PondUpdate, PondOut

router = APIRouter(prefix="/api/ponds", tags=["ponds"])


@router.get("", response_model=List[PondOut])
def list_ponds(
    hatchery_id: Optional[int] = Query(None, alias="hatcheryId"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
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
    item = db.query(Pond).filter(Pond.id == pond_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="塘口不存在")

    data = payload.model_dump(exclude_unset=True)
    if "hatchery_id" in data:
        hatchery = db.query(Hatchery).filter(Hatchery.id == data["hatchery_id"]).first()
        if not hatchery:
            raise HTTPException(status_code=400, detail="育苗场不存在")

    new_status = data.pop("status", None)
    status_changed = new_status is not None and new_status != item.status

    if status_changed:
        old_status = item.status
        # 合法路径只在 pond_status 一处判定
        if not can_transit(old_status, new_status):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=transit_reason(old_status, new_status),
            )
        # 原子条件更新（CAS）：WHERE 带上旧状态。
        # 并发改同一塘时，READ COMMITTED 下只有一个事务能匹配到旧行，
        # 其余事务 rowcount=0，保证并发改隔离至多成功一次。
        try:
            matched = (
                db.query(Pond)
                .filter(Pond.id == pond_id, Pond.status == old_status)
                .update({"status": new_status}, synchronize_session=False)
            )
            if matched == 0:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="塘口状态已被其他操作修改，请刷新后重试",
                )
            # CAS 已落库，丢弃会话内的过期快照，后续按新行继续
            db.expire(item)
        except HTTPException:
            raise
        except Exception:
            db.rollback()
            raise

    for k, v in data.items():
        setattr(item, k, v)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
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
