from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.common import BaseResponse, success_response
from app.schemas.shopping_list import ShoppingListCreate, ShoppingListItemCreate, ShoppingListItemPatch
from app.services import shopping_list_service
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/shopping-lists", tags=["shopping-lists"])


@router.get("", response_model=BaseResponse)
def get_shopping_lists(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = shopping_list_service.get_shopping_lists(db, current_user.user_id)
    return success_response(data)


@router.post("", response_model=BaseResponse)
def create_shopping_list(
    req: ShoppingListCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = shopping_list_service.create_shopping_list(db, current_user.user_id, req.title)
    return success_response(data)


@router.post("/{shopping_list_id}/items", response_model=BaseResponse)
def add_item(
    shopping_list_id: str,
    req: ShoppingListItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = shopping_list_service.add_item(
        db, shopping_list_id, current_user.user_id,
        req.product_name_snapshot, req.qty, req.unit,
        req.product_id, req.estimated_price, req.store_id,
    )
    return success_response(data)


@router.patch("/{shopping_list_id}/items/{list_item_id}", response_model=BaseResponse)
def patch_item(
    shopping_list_id: str,
    list_item_id: str,
    req: ShoppingListItemPatch,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = shopping_list_service.patch_item(
        db, shopping_list_id, list_item_id, current_user.user_id,
        req.checked, req.qty,
    )
    return success_response(data)


@router.delete("/{shopping_list_id}/items/{list_item_id}", response_model=BaseResponse)
def delete_item(
    shopping_list_id: str,
    list_item_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = shopping_list_service.remove_item(
        db, shopping_list_id, list_item_id, current_user.user_id,
    )
    return success_response(data)
