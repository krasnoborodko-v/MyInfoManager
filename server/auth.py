"""
Авторизация: хеширование паролей, JWT токены, проверка пользователя.
"""
import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt

from db.connection import get_connection
from db.models import User


# ============================================================
# Настройки
# ============================================================

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    # Генерируем случайный при старте (для dev)
    SECRET_KEY = os.urandom(32).hex()

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ============================================================
# Утилиты паролей
# ============================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверить пароль against хеша."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Хешировать пароль через bcrypt."""
    return pwd_context.hash(password)


# ============================================================
# JWT
# ============================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Создать access-токен."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Создать refresh-токен."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str, token_type: str = "access") -> dict:
    """Расшифровать и проверить JWT токен."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ============================================================
# Зависимости для FastAPI
# ============================================================

def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Извлечь текущего пользователя из JWT токена.
    Используется как зависимость в защищённых эндпоинтах.
    """
    payload = decode_token(token, "access")
    user_id: Optional[int] = payload.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM "user" WHERE id = ?', (user_id,))
    row = cursor.fetchone()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    user = User.from_row(row)

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return user


def get_optional_user(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[User]:
    """
    Извлечь пользователя если токен есть, но не ошибиться если нет.
    Для эндпоинтов, которые работают и для анонимов тоже.
    """
    try:
        return get_current_user(token)
    except HTTPException:
        return None
