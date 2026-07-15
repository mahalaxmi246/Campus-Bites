from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models import User, UserRole
from app.schemas.user import StaffCreateRequest, UserResponse
from app.services.user_service import create_staff_user

router = APIRouter()


@router.post("/staff", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_staff(
    data: StaffCreateRequest,
    db: Session = Depends(get_db),
    _current_admin: User = Depends(require_role(UserRole.admin)),
) -> UserResponse:
    """
    Admin-only. Only ever creates staff accounts — see create_staff_user's
    docstring for why this can't be abused to create an admin account.
    There is intentionally no equivalent endpoint for creating admins;
    that stays a developer-only, off-API action (scripts/seed.py or direct
    DB access), per an explicit product decision.
    """
    return create_staff_user(db, data)