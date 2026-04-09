from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.db.models import User
from app.modules.auth.schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.modules.auth.service import AuthService
from app.modules.users.service import UserService
from app.shared.schemas.common import ApiSuccessResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=ApiSuccessResponse[TokenResponse])
def register(
    body: RegisterRequest,
    db: Session = Depends(get_db),
) -> ApiSuccessResponse[TokenResponse]:
    user = UserService(db).register_user(body.full_name, str(body.email), body.password)
    token = AuthService(db).issue_token_for_user(user)
    return ApiSuccessResponse(data=token, message="Đăng ký thành công")


@router.post("/login", response_model=ApiSuccessResponse[TokenResponse])
def login(
    body: LoginRequest,
    db: Session = Depends(get_db),
) -> ApiSuccessResponse[TokenResponse]:
    token = AuthService(db).login(str(body.email), body.password)
    return ApiSuccessResponse(data=token, message="Đăng nhập thành công")


@router.get("/me", response_model=ApiSuccessResponse[UserResponse])
def me(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiSuccessResponse[UserResponse]:
    data = AuthService(db).me(user)
    return ApiSuccessResponse(data=data, message="Success")
