from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from jose import JWTError
from app import models, schemas
from app.deps import CurrentUser, Db
from app.security import create_access_token, create_refresh_token, decode_refresh_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def register(data: schemas.UserCreate, db: Db):
    if db.scalar(select(models.User).where(models.User.email == data.email.lower())):
        raise HTTPException(status_code=409, detail="E-mail уже зарегистрирован")
    user = models.User(email=data.email.lower(), password_hash=hash_password(data.password), profile=models.Profile(full_name=data.full_name))
    db.add(user); db.commit(); db.refresh(user)
    return user

@router.post("/token", response_model=schemas.TokenPair)
def token(db: Db, form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = db.scalar(select(models.User).options(selectinload(models.User.profile)).where(models.User.email == form.username.lower()))
    if not user or not user.is_active or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверный e-mail или пароль", headers={"WWW-Authenticate": "Bearer"})
    return schemas.TokenPair(access_token=create_access_token(user.id, user.role), refresh_token=create_refresh_token(user.id, user.role))

@router.get("/me", response_model=schemas.UserRead)
def me(user: CurrentUser):
    return user

@router.post("/refresh", response_model=schemas.TokenPair)
def refresh(data: schemas.RefreshRequest, db: Db):
    try:
        user_id = int(decode_refresh_token(data.refresh_token)["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Недействительный refresh-токен")
    user = db.get(models.User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Пользователь недоступен")
    return schemas.TokenPair(access_token=create_access_token(user.id, user.role), refresh_token=create_refresh_token(user.id, user.role))

