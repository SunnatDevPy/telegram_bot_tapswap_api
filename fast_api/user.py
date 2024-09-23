import asyncio
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from db import User

user_router = APIRouter(prefix='/users', tags=['User'])


class UserAdd(BaseModel):
    first_name: str
    last_name: str
    username: Optional[str] = None
    phone: str
    is_admin: Optional[bool] = False
    status_id: int
    coins: int
    bonus: int
    energy: int
    max_energy: int


class UserList(BaseModel):
    id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    phone: Optional[str] = None
    is_admin: Optional[bool] = False
    status_id: Optional[int] = None
    coins: Optional[int] = None
    bonus: Optional[int] = None
    energy: Optional[int] = None
    max_energy: Optional[int] = None


async def increase_energy(user_id, energy, max_energy):
    while True:
        if max_energy == energy:
            break
        energy += 1
        await User.update(user_id, energy=energy)
        await asyncio.sleep(1)


@user_router.post("")
async def user_add(user: Annotated[UserAdd, Depends()]):
    user = await User.create(**user.dict())
    return {'ok': True, "id": user.id}


@user_router.get('')
async def user_list() -> list[UserList]:
    users = await User.get_all()
    return users


class UserPatch(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    phone: Optional[str] = None
    is_admin: Optional[bool] = False
    status_id: Optional[int] = None
    coins: Optional[int] = None
    bonus: Optional[int] = None
    energy: Optional[int] = None
    max_energy: Optional[int] = None


class UserCoin(BaseModel):
    coins: int = None
    energy: int = None


@user_router.get("/{user_id}")
async def user_detail(user_id: int):
    user = await User.get(user_id)
    return {"detail": user}


# coin energy update
@user_router.patch("/coin/{user_id}", response_model=UserCoin)
async def user_patch(user_id: int, item: Annotated[UserPatch, Depends()]):
    user = await User.get(user_id)
    if user:
        update_data = {k: v for k, v in item.dict().items() if v is not None}
        if update_data:
            await User.update(user_id, **update_data)
            await increase_energy(user_id, item.energy, user.max_energy)
            return {"ok": True, "data": update_data}
        else:
            return {"ok": False, "message": "Nothing to update"}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@user_router.patch("/{user_id}")
async def user_patch(user_id: int, item: Annotated[UserPatch, Depends()]):
    user = await User.get(user_id)
    if user:
        update_data = {k: v for k, v in item.dict().items() if v is not None}
        if update_data:
            await User.update(user_id, **update_data)
            return {"ok": True, "data": update_data}
        else:
            return {"ok": False, "message": "Nothing to update"}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@user_router.delete("/{user_id}")
async def user_delete(user_id: int):
    await User.delete(user_id)
    return {"ok": True, 'id': user_id}
