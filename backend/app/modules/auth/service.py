from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.core.security import create_access_token, verify_password
from app.db.models import User, UserStatus
from app.modules.auth.schemas import TokenResponse, UserResponse
from app.modules.users.repository import UserRepository


class AuthService:
    def __init__(self, db: Session) -> None:
        self._repo = UserRepository(db)

    def issue_token_for_user(self, user: User) -> TokenResponse:
        if user.status != UserStatus.active.value:
            raise AppError("Tài khoản không hoạt động", "USER_INACTIVE", status_code=403)
        token = create_access_token(
            str(user.id),
            extra_claims={"email": user.email, "role": user.role},
        )
        return TokenResponse(access_token=token)

    def login(self, email: str, password: str) -> TokenResponse:
        user = self._repo.get_by_email(email)
        if not user or user.status != UserStatus.active.value:
            raise AppError(
                "Email hoặc mật khẩu không đúng",
                "INVALID_CREDENTIALS",
                status_code=401,
            )
        if not verify_password(password, user.password_hash):
            raise AppError(
                "Email hoặc mật khẩu không đúng",
                "INVALID_CREDENTIALS",
                status_code=401,
            )
        return self.issue_token_for_user(user)

    def me(self, user: User) -> UserResponse:
        return UserResponse(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            role=user.role,
            status=user.status,
        )
