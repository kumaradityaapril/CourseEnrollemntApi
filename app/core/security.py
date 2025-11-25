from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app import models
from app.db.database import get_db
from .config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    pwd_context.hash("test")  # Warm-up to ensure backend available
    USE_PASSLIB = True
except Exception:
    pwd_context = None
    USE_PASSLIB = False


def get_password_hash(password: str) -> str:
    password_bytes = password.encode("utf-8")[:72]
    password = password_bytes.decode("utf-8", errors="ignore")
    if not USE_PASSLIB:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
        return hashed.decode("utf-8")
    try:
        return pwd_context.hash(password)
    except Exception:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
        return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    pw = plain_password.encode("utf-8")[:72]
    pw = pw.decode("utf-8", errors="ignore")
    if not USE_PASSLIB:
        return bcrypt.checkpw(pw.encode(), hashed_password.encode())
    try:
        return pwd_context.verify(pw, hashed_password)
    except Exception:
        return bcrypt.checkpw(pw.encode(), hashed_password.encode())


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        role: str | None = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
        user = db.query(models.User).filter(models.User.username == username).first()
        if user is None or not user.is_active:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def admin_required(current_user: models.User = Depends(get_current_user)) -> models.User:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only")
    return current_user

