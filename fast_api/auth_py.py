from datetime import timedelta, timezone, datetime
from typing import Union

import jwt
from fastapi import HTTPException
from jwt import InvalidTokenError
from sqladmin.authentication import AuthenticationBackend
from starlette import status
from starlette.requests import Request

from db.models.model import User

ALGORITHM = "HS256"

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, "stockminiapp", algorithm=ALGORITHM)


async def get_current_user(token):
    try:
        payload = jwt.decode(token, "stockminiapp", algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    user = await User.get(int(user_id))
    if user is None:
        raise credentials_exception
    return user


class AuthBackend(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form['password']
        user = await User.get(5649321700)
        if user is not None and user:
            user_data = {
                "id": user.id,
                "username": user.username,
            }
            access_token = create_access_token(user_data)
            request.session.update({"token": access_token, "user_id": user.id})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request):
        token = request.session.get("token")
        try:
            user = await get_current_user(token)
        except Exception as e:
            return False
        return user, True
