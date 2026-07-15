from collections.abc import Callable

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import AppError
from app.core.security import decode_token
from app.models import User, UserRole

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise AppError(
            code="NOT_AUTHENTICATED", message="Missing bearer token", status_code=401
        )

    try:
        payload = decode_token(credentials.credentials)
    except JWTError:
        raise AppError(
            code="INVALID_TOKEN", message="Access token is invalid or expired", status_code=401
        )

    if payload.get("type") != "access":
        raise AppError(
            code="INVALID_TOKEN", message="Access token is invalid or expired", status_code=401
        )

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first() if user_id else None
    if user is None:
        raise AppError(
            code="INVALID_TOKEN", message="Access token is invalid or expired", status_code=401
        )

    return user


def require_role(*allowed_roles: UserRole) -> Callable[[User], User]:
    """
    Usage: Depends(require_role(UserRole.staff, UserRole.admin))

    Layered on top of get_current_user, so the 401-vs-403 distinction stays
    correct automatically: no/bad token -> 401 (not authenticated) happens
    inside get_current_user before this even runs; valid token but wrong
    role -> 403 (authenticated, but not permitted) happens here.
    """

    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise AppError(
                code="FORBIDDEN",
                message="You do not have permission to perform this action",
                status_code=403,
            )
        return current_user

    return dependency