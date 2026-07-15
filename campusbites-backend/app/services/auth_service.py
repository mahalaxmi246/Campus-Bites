from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AppError
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.models import RefreshToken, User


def authenticate_user(db: Session, username: str, password: str) -> User:
    user = db.query(User).filter(User.username == username).first()
    if user is None or not verify_password(password, user.password_hash):
        raise AppError(
            code="INVALID_CREDENTIALS",
            message="Username or password is incorrect",
            status_code=401,
        )
    return user


def _create_refresh_token_row(db: Session, user_id: int) -> str:
    raw_token = generate_refresh_token()
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    db.add(
        RefreshToken(
            user_id=user_id,
            token_hash=hash_refresh_token(raw_token),
            expires_at=expires_at,
        )
    )
    return raw_token


def issue_tokens_for_user(db: Session, user: User) -> tuple[str, str]:
    access_token = create_access_token(
        subject=str(user.id),
        extra_claims={"role": user.role.value, "username": user.username},
    )
    refresh_token = _create_refresh_token_row(db, user.id)
    db.commit()
    return access_token, refresh_token


def refresh_access_token(db: Session, raw_refresh_token: str) -> tuple[str, str]:
    stored = (
        db.query(RefreshToken)
        .filter(RefreshToken.token_hash == hash_refresh_token(raw_refresh_token))
        .first()
    )

    now = datetime.now(timezone.utc)
    is_invalid = (
        stored is None
        or stored.revoked
        or stored.expires_at.replace(tzinfo=timezone.utc) < now
    )
    if is_invalid:
        raise AppError(
            code="INVALID_REFRESH_TOKEN",
            message="Refresh token is invalid or expired",
            status_code=401,
        )

    user = db.query(User).filter(User.id == stored.user_id).first()
    if user is None:
        raise AppError(
            code="INVALID_REFRESH_TOKEN",
            message="Refresh token is invalid or expired",
            status_code=401,
        )

    stored.revoked = True
    access_token = create_access_token(
        subject=str(user.id),
        extra_claims={"role": user.role.value, "username": user.username},
    )
    new_refresh_token = _create_refresh_token_row(db, user.id)
    db.commit()
    return access_token, new_refresh_token

def revoke_all_refresh_tokens(db: Session, user_id: int) -> None:
    """
    "Logout." Note this only revokes refresh tokens — the current access
    token stays technically valid until it naturally expires (it's a
    stateless JWT, minutes-lived by design). This is the standard, accepted
    tradeoff of the access+refresh pattern: true instant-everywhere
    revocation of access tokens would require checking a blacklist on every
    single request, which defeats the point of using stateless JWTs at all.
    Keeping ACCESS_TOKEN_EXPIRE_MINUTES short (15 min, per .env) is what
    bounds the actual exposure window.
    """
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id, RefreshToken.revoked.is_(False)
    ).update({"revoked": True})
    db.commit()

def change_password(
    db: Session, user: User, current_password: str, new_password: str
) -> tuple[str, str]:
    """
    Requires the CURRENT password (not admin-bypassable) — this is
    self-service, not account recovery. Full forgot-password (for someone
    who's genuinely lost access) needs an email service and is deferred;
    see conversation notes. This alone already solves the "admin assigned
    everyone the same initial password" risk, since staff can immediately
    set something only they know.

    Revokes every other active session on success — if the old password
    had leaked or been shared, this is the point that exposure ends. The
    CURRENT session gets a fresh token pair below so this device doesn't
    get logged out too.
    """
    if not verify_password(current_password, user.password_hash):
        raise AppError(
            code="INVALID_CREDENTIALS",
            message="Current password is incorrect",
            status_code=401,
        )

    user.password_hash = hash_password(new_password)
    db.add(user)

    db.query(RefreshToken).filter(
        RefreshToken.user_id == user.id, RefreshToken.revoked.is_(False)
    ).update({"revoked": True})

    access_token = create_access_token(
        subject=str(user.id),
        extra_claims={"role": user.role.value, "username": user.username},
    )
    new_refresh_token = _create_refresh_token_row(db, user.id)
    db.commit()
    return access_token, new_refresh_token