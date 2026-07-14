from passlib.context import CryptContext

# CryptContext wraps bcrypt with sane defaults (auto-handles salting,
# work factor). "deprecated=auto" lets you add a stronger scheme later
# (e.g. argon2) and it'll auto-upgrade old hashes on next login.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)