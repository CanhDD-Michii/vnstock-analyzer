from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.core.security import hash_password
from app.db.models import User, UserRole, UserStatus
from app.modules.users.repository import UserRepository


class UserService:
    def __init__(self, db: Session) -> None:
        self._repo = UserRepository(db)

    def register_user(self, full_name: str, email: str, password: str) -> User:
        if self._repo.get_by_email(email):
            raise AppError("Email đã được sử dụng", "EMAIL_TAKEN")
        return self._repo.create(
            full_name=full_name,
            email=email,
            password_hash=hash_password(password),
            role=UserRole.user.value,
            status=UserStatus.active.value,
        )
