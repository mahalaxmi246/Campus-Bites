import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def create_access_token(subject: str, extra_claims: dict | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode: dict = {"sub": subject, "exp": expire, "type": "access"}
    if extra_claims:
        to_encode.update(extra_claims)
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])


def generate_refresh_token() -> str:
    """
    Refresh tokens are NOT JWTs — just a high-entropy random string. Real
    rotation/revocation needs a server-side record per token anyway (see
    RefreshToken model), so there's no benefit to a signed/decodable
    token here, only extra complexity.
    """
    return secrets.token_urlsafe(64)


def hash_refresh_token(token: str) -> str:
    """
    SHA-256, not bcrypt. Refresh tokens are already high-entropy random
    strings (unlike passwords), so we only need a fast, deterministic
    hash for exact-match DB lookup — not a slow adaptive one. The DB
    still never stores the raw token.
    """
    return hashlib.sha256(token.encode()).hexdigest()