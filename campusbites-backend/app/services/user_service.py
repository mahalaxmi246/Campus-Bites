from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.core.security import hash_password
from app.models import User, UserRole
from app.schemas.user import StaffCreateRequest, UserRegisterRequest


def _ensure_username_and_email_available(db: Session, username: str, email: str) -> None:
    existing = (
        db.query(User).filter((User.username == username) | (User.email == email)).first()
    )
    if existing is not None:
        field = "username" if existing.username == username else "email"
        raise AppError(
            code="USER_ALREADY_EXISTS",
            message=f"A user with this {field} already exists",
            status_code=409,
        )


def _insert_user(db: Session, user: User) -> User:
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise AppError(
            code="USER_ALREADY_EXISTS",
            message="A user with this username or email already exists",
            status_code=409,
        )
    db.refresh(user)
    return user


def create_user(db: Session, data: UserRegisterRequest) -> User:
    """Public self-registration. ALWAYS creates a student — there is no
    role field on UserRegisterRequest, so there is no code path here that
    could ever produce a staff or admin account."""
    _ensure_username_and_email_available(db, data.username, data.email)
    user = User(
        full_name=data.full_name,
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        # role omitted -> falls back to the model default: UserRole.student
    )
    return _insert_user(db, user)


def create_staff_user(db: Session, data: StaffCreateRequest) -> User:
    """
    Admin-only staff provisioning (route enforces require_role(UserRole.admin)).
    Deliberately hardcodes role=staff — this function can NEVER create an
    admin account, no matter what a caller puts in the request body, because
    StaffCreateRequest has no role field to manipulate in the first place.
    Admin accounts are created ONLY via scripts/seed.py / direct DB access
    by whoever operates the server — never through the API, by design.
    """
    _ensure_username_and_email_available(db, data.username, data.email)
    user = User(
        full_name=data.full_name,
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        role=UserRole.staff,
    )
    return _insert_user(db, user)