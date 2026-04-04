"""
API эндпоинты авторизации: регистрация, вход, обновление токена.
"""
from fastapi import APIRouter, HTTPException, Depends, status

from db.connection import get_connection
from db.models import User
from server.schemas import UserCreate, UserLogin, UserResponse, Token, TokenRefresh, TokenRefreshResponse
from server.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate):
    """Зарегистрировать нового пользователя."""
    conn = get_connection()
    cursor = conn.cursor()

    # Проверяем, не занят ли email
    cursor.execute('SELECT id FROM "user" WHERE email = ?', (user_data.email,))
    if cursor.fetchone():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    # Создаём
    hashed_pw = get_password_hash(user_data.password)
    cursor.execute(
        'INSERT INTO "user" (email, hashed_password, full_name) VALUES (?, ?, ?)',
        (user_data.email, hashed_pw, user_data.full_name),
    )
    conn.commit()

    user_id = cursor.lastrowid

    return UserResponse(
        id=user_id,
        email=user_data.email,
        full_name=user_data.full_name,
        is_active=True,
    )


@router.post("/login", response_model=Token)
def login(credentials: UserLogin):
    """Войти в систему."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        'SELECT * FROM "user" WHERE email = ?',
        (credentials.email,),
    )
    row = cursor.fetchone()

    if not row or not verify_password(credentials.password, row["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    user = User.from_row(row)

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive",
        )

    # Создаём токены
    token_data = {"sub": user.email, "user_id": user.id}
    access = create_access_token(token_data)
    refresh = create_refresh_token(token_data)

    return Token(
        access_token=access,
        refresh_token=refresh,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
        ),
    )


@router.post("/refresh", response_model=TokenRefreshResponse)
def refresh_token(body: TokenRefresh):
    """Обновить access-токен через refresh."""
    payload = decode_token(body.refresh_token, "refresh")
    user_id = payload.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM "user" WHERE id = ?', (user_id,))
    row = cursor.fetchone()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    user = User.from_row(row)
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive",
        )

    token_data = {"sub": user.email, "user_id": user.id}
    return TokenRefreshResponse(
        access_token=create_access_token(token_data),
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Получить информацию о текущем пользователе."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
    )
