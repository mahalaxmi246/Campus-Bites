from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models import User, UserRole
from app.schemas.menu import MenuItemCreateRequest, MenuItemResponse, MenuItemUpdateRequest
from app.services.menu_service import create_menu_item, delete_menu_item, update_menu_item

router = APIRouter()


@router.post("", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(
    data: MenuItemCreateRequest,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_role(UserRole.staff, UserRole.admin)),
) -> MenuItemResponse:
    return create_menu_item(db, data)


@router.put("/{item_id}", response_model=MenuItemResponse)
def update_item(
    item_id: int,
    data: MenuItemUpdateRequest,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_role(UserRole.staff, UserRole.admin)),
) -> MenuItemResponse:
    return update_menu_item(db, item_id, data)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_role(UserRole.staff, UserRole.admin)),
) -> None:
    delete_menu_item(db, item_id)