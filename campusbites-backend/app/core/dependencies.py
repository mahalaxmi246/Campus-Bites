from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import AppError
from app.core.security import decode_token
from app.models import User

# auto_error=False so a missing header doesn't trigger FastAPI's default
# HTTPException shape — we want every auth failure to go through our own
# AppError, so the response body is always {"error": {"code", "message"}}.
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

    # Guards against a refresh token (or any other future token "type")
    # being passed here by mistake — only access tokens authenticate requests.
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