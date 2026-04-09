from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self._db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self._db.scalar(select(User).where(User.email == email.lower()))

    def create(
        self,
        *,
        full_name: str,
        email: str,
        password_hash: str,
        role: str,
        status: str,
    ) -> User:
        u = User(
            full_name=full_name,
            email=email.lower(),
            password_hash=password_hash,
            role=role,
            status=status,
        )
        self._db.add(u)
        self._db.commit()
        self._db.refresh(u)
        return u

    def list_users(self, skip: int = 0, limit: int = 50) -> list[User]:
        q = select(User).order_by(User.id.desc()).offset(skip).limit(limit)
        return list(self._db.scalars(q).all())

    def patch_user(
        self,
        user_id: int,
        *,
        full_name: str | None = None,
        set_full_name: bool = False,
        role: str | None = None,
        set_role: bool = False,
        status: str | None = None,
        set_status: bool = False,
    ) -> User | None:
        u = self.get_by_id(user_id)
        if not u:
            return None
        if set_full_name and full_name is not None:
            u.full_name = full_name
        if set_role and role is not None:
            u.role = role
        if set_status and status is not None:
            u.status = status
        self._db.commit()
        self._db.refresh(u)
        return u
