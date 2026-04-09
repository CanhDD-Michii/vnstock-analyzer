from collections.abc import Generator

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.db.models import User, UserRole, UserStatus
from app.db.session import get_db as _get_db


def get_db() -> Generator[Session, None, None]:
    yield from _get_db()


def get_bearer_token(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise UnauthorizedError("Missing or invalid Authorization header")
    return authorization[7:].strip()


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(get_bearer_token),
) -> User:
    from app.core.security import decode_token_safe

    payload = decode_token_safe(token)
    if not payload or "sub" not in payload:
        raise UnauthorizedError("Invalid or expired token")
    try:
        user_id = int(payload["sub"])
    except (TypeError, ValueError) as exc:
        raise UnauthorizedError("Invalid token subject") from exc
    user = db.get(User, user_id)
    if not user or user.status != UserStatus.active.value:
        raise UnauthorizedError("User not found or inactive")
    return user


def get_current_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.admin.value:
        raise ForbiddenError("Admin access required")
    return user
