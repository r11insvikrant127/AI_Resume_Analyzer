# auth.py

from passlib.context import CryptContext
from db_operations import create_user, get_user_by_email

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return pwd_ctx.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return pwd_ctx.verify(plain, hashed)
    except Exception:
        return False


def register_user(email, password, full_name=None):
    if get_user_by_email(email):
        return None, "An account with that email already exists."

    if len(password) < 8:
        return None, "Password must be at least 8 characters."

    user_id = create_user(
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
        is_admin=False,
    )
    return user_id, None


def authenticate(email, password):
    user = get_user_by_email(email)

    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user