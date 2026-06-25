from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user, require_admin
from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import TokenResponse, UserCreateByAdmin, UserLogin, UserRegister, UserResponse
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
def register(payload: UserRegister, db: Session = Depends(get_db)) -> UserResponse:
    user = AuthService(db).register(payload)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> TokenResponse:
    token = AuthService(db).login(payload)
    return TokenResponse(access_token=token)


@router.post("/token", response_model=TokenResponse)
def login_for_docs(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> TokenResponse:
    token = AuthService(db).login(UserLogin(email=form_data.username, password=form_data.password))
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user_as_admin(
    payload: UserCreateByAdmin,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> UserResponse:
    user = AuthService(db).create_user(
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
        role=payload.role,
    )
    return UserResponse.model_validate(user)
