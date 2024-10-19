from datetime import datetime, timedelta, timezone
from http.client import HTTPException
from typing import Annotated

import bcrypt
import jwt
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from icecream import icecream
from jose import JWTError
from jwt import InvalidTokenError
from pydantic import BaseModel
from starlette import status

from db import User

SECRET_KEY = "selectstalker"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3600
REFRESH_TOKEN_EXPIRE_DAYS = 100

jwt_router = APIRouter()

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"}, )


def create_refresh_token(user_id: int):
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"user_id": user_id, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        icecream.ic(payload)
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    user = await User.get(int(user_id))
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.status_id:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


class Token(BaseModel):
    access_token: str
    token_type: str


class UserId(BaseModel):
    user_id: int


class RefreshToken(BaseModel):
    refresh_token: int


@jwt_router.post("/me/")
async def protected_route(user_id: User = Depends(get_current_user)):
    return {"message": f"Ruxsat berildi {user_id}"}


@jwt_router.post("/token", response_model=Token)
async def login_for_access_token(user_id: Annotated[UserId, Depends()]) -> Token:
    user = await User.get(user_id.user_id)

    if user:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"user_id": str(user_id.user_id)},
            expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type='bearer')
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@jwt_router.post("/refresh")
def refresh_access_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token = create_access_token(
        data={"user_id": str(user_id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": new_access_token, "token_type": "bearer"}
