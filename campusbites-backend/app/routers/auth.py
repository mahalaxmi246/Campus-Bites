from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import User
from app.schemas.auth import ChangePasswordRequest, LoginRequest, RefreshRequest, TokenResponse
from app.schemas.user import UserRegisterRequest, UserResponse
from app.services.auth_service import (
    authenticate_user,
    change_password,
    issue_tokens_for_user,
    refresh_access_token,
    revoke_all_refresh_tokens,
)
from app.services.user_service import create_user

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(data: UserRegisterRequest, db: Session = Depends(get_db)) -> UserResponse:
    user = create_user(db, data)
    return user


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = authenticate_user(db, data.username, data.password)
    access_token, refresh_token = issue_tokens_for_user(db, user)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    access_token, refresh_token = refresh_access_token(db, data.refresh_token)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> None:
    revoke_all_refresh_tokens(db, current_user.id)


@router.post("/change-password", response_model=TokenResponse)
def change_password_route(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TokenResponse:
    access_token, refresh_token = change_password(
        db, current_user, data.current_password, data.new_password
    )
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)