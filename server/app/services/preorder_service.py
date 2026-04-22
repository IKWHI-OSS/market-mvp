"""
preorder_service — Preorder 비즈니스 로직

  create_preorder  → consumer/merchant 모두 가능
  list_preorders   → 내 사전 주문 목록 (consumer: 본인, merchant: 담당 점포)
  update_status    → merchant 전용, 상태 변경 시 Notification 자동 생성
"""
import uuid
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models.preorder import Preorder, PreorderStatusEnum
from app.db.repositories import preorder_repository as repo
from app.db.repositories.merchant_repository import get_store_ids_for_user
from app.db.models.notification import Notification

# 상태 전이 허용 규칙
_VALID_TRANSITIONS: dict[PreorderStatusEnum, list[PreorderStatusEnum]] = {
    PreorderStatusEnum.requested:  [PreorderStatusEnum.confirmed, PreorderStatusEnum.cancelled],
    PreorderStatusEnum.confirmed:  [PreorderStatusEnum.ready,     PreorderStatusEnum.cancelled],
    PreorderStatusEnum.ready:      [PreorderStatusEnum.cancelled],
    PreorderStatusEnum.cancelled:  [],
}

# Notification 메시지 템플릿
_NOTIF_MESSAGES: dict[PreorderStatusEnum, tuple[str, str]] = {
    PreorderStatusEnum.confirmed: ("사전 주문 확인됨", "'{product_name}' 주문이 상인에 의해 확인되었습니다."),
    PreorderStatusEnum.ready:     ("상품 준비 완료",   "'{product_name}' 주문 상품이 준비되었습니다. 방문해 주세요!"),
    PreorderStatusEnum.cancelled: ("주문 취소됨",      "'{product_name}' 주문이 취소되었습니다."),
}


def _fmt_preorder(p: Preorder) -> dict:
    return {
        "preorder_id":  p.preorder_id,
        "user_id":      p.user_id,
        "store_id":     p.store_id,
        "product_name": p.product_name,
        "qty":          p.qty,
        "status":       p.status.value,
        "created_at":   p.created_at.isoformat() if p.created_at else None,
    }


# ──────────────────────────────────────────────
# 사전 주문 생성
# ──────────────────────────────────────────────

def create_preorder(
    db: Session,
    user,
    store_id: str,
    product_name: str,
    qty: int,
) -> dict:
    if qty <= 0:
        raise HTTPException(status_code=422, detail="qty는 1 이상이어야 합니다.")

    p = repo.create_preorder(
        db,
        user_id=user.user_id,
        store_id=store_id,
        product_name=product_name,
        qty=qty,
    )
    return _fmt_preorder(p)


# ──────────────────────────────────────────────
# 내 사전 주문 목록
# ──────────────────────────────────────────────

def list_preorders(
    db: Session,
    user,
    page: int = 1,
    size: int = 20,
) -> dict:
    size = min(size, 100)

    if user.role.value == "merchant":
        store_ids = get_store_ids_for_user(db, user.user_id)
        items, total = repo.list_preorders_by_store(db, store_ids, page, size)
    else:
        items, total = repo.list_preorders_by_user(db, user.user_id, page, size)

    return {
        "items": [_fmt_preorder(p) for p in items],
        "pagination": {
            "page":     page,
            "size":     size,
            "total":    total,
            "has_next": (page * size) < total,
        },
    }


# ──────────────────────────────────────────────
# 상태 변경 (merchant 전용)
# ──────────────────────────────────────────────

def update_status(
    db: Session,
    user,
    preorder_id: str,
    new_status_str: str,
) -> dict:
    if user.role.value != "merchant":
        raise HTTPException(status_code=403, detail="상인 권한이 필요합니다.")

    # 상태값 검증
    try:
        new_status = PreorderStatusEnum(new_status_str)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"유효하지 않은 status: {new_status_str}. "
                   f"가능한 값: {[e.value for e in PreorderStatusEnum]}",
        )

    preorder: Optional[Preorder] = repo.get_preorder(db, preorder_id)
    if not preorder:
        raise HTTPException(status_code=404, detail="사전 주문을 찾을 수 없습니다.")

    # 상인이 담당 점포의 주문인지 확인
    store_ids = get_store_ids_for_user(db, user.user_id)
    if preorder.store_id not in store_ids:
        raise HTTPException(status_code=403, detail="해당 주문에 대한 권한이 없습니다.")

    # 상태 전이 검증
    allowed = _VALID_TRANSITIONS.get(preorder.status, [])
    if new_status not in allowed:
        raise HTTPException(
            status_code=409,
            detail=f"'{preorder.status.value}' → '{new_status.value}' 전이가 허용되지 않습니다.",
        )

    repo.update_preorder_status(db, preorder, new_status)
    _create_status_notification(db, preorder, new_status)

    return _fmt_preorder(preorder)


# ──────────────────────────────────────────────
# 알림 생성
# ──────────────────────────────────────────────

def _create_status_notification(
    db: Session, preorder: Preorder, new_status: PreorderStatusEnum
) -> None:
    tmpl = _NOTIF_MESSAGES.get(new_status)
    if not tmpl:
        return  # requested 자체에는 알림 없음

    title_tpl, body_tpl = tmpl
    title = title_tpl
    body  = body_tpl.format(product_name=preorder.product_name)

    notif = Notification(
        notification_id  = str(uuid.uuid4()),
        user_id          = preorder.user_id,
        type             = "preorder_status",
        title            = title,
        body             = body,
        target_type      = "preorder",
        target_id        = preorder.preorder_id,
        is_read          = False,
        send_status      = "sent",
    )
    db.add(notif)
    db.commit()
