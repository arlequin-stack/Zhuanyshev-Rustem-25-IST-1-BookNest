from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
Db = Annotated[Session, Depends(get_db)]

def get_current_user(db: Db, token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    credentials_error = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недействительные учётные данные", headers={"WWW-Authenticate": "Bearer"})
    try:
        user_id = int(decode_access_token(token)["sub"])
    except (JWTError, KeyError, ValueError):
        raise credentials_error
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise credentials_error
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]

def require_librarian(user: CurrentUser) -> User:
    if user.role != "librarian":
        raise HTTPException(status_code=403, detail="Требуется роль библиотекаря")
    return user

Librarian = Annotated[User, Depends(require_librarian)]

