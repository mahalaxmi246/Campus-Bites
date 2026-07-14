from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.core.security import hash_password
from app.models import User
from app.schemas.user import UserRegisterRequest


def create_user(db: Session, data: UserRegisterRequest) -> User:
    existing = (
        db.query(User)
        .filter((User.username == data.username) | (User.email == data.email))
        .first()
    )
    if existing is not None:
        field = "username" if existing.username == data.username else "email"
        raise AppError(
            code="USER_ALREADY_EXISTS",
            message=f"A user with this {field} already exists",
            status_code=409,
        )

    user = User(
        full_name=data.full_name,
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        # Belt-and-braces: catches a race where two requests pass the
        # existence check above at the same instant.
        db.rollback()
        raise AppError(
            code="USER_ALREADY_EXISTS",
            message="A user with this username or email already exists",
            status_code=409,
        )
    db.refresh(user)
    return user
