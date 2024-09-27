import asyncio
import time
from threading import Thread
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from db import User, Statusie
from db.models.model import Referral, UserAndExperience
from fast_api.utils import hour_coin_check, get_detail_experience, top_players_from_statu

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
    status_id: Optional[int] = None
    coins: Optional[int] = None
    bonus: Optional[int] = None
    energy: Optional[int] = None
    max_energy: Optional[int] = None


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
    status_id: Optional[int] = None
    coins: int
    bonus: Optional[int] = None
    energy: int
    max_energy: Optional[int] = None


active_tasks = {}


async def update_status(user):
    status = await Statusie.get(user.status_id)
    status_by_level = await Statusie.get_from_level(status.level + 1)
    if status_by_level:
        if user.coins > status.limit_coin:
            await User.update(user.id, status_id=status_by_level.id)
    else:
        return


@user_router.get("/{user_id}")
async def user_detail(user_id: int):
    user = await User.get(user_id)
    if user:
        status = await Statusie.get(user.status_id)
        # friends = await Referral.get_from_user_id(user_id)
        experience = await UserAndExperience.get_from_user_id_experience(user_id)
        return {"user_data": user, "status": status, 'experience': await get_detail_experience(experience),
                'hour_coin': await hour_coin_check(user_id), "top_10": await top_players_from_statu()}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


async def increase_energy(user_id, energy, max_energy):
    while max_energy != energy:
        energy += 4
        if energy > max_energy:
            await User.update(user_id, energy=max_energy)
            break
        await asyncio.sleep(3)
        await User.update(user_id, energy=energy)


# coin energy update
@user_router.patch("/{user_id}")
async def user_patch(user_id: int, item: Annotated[UserPatch, Depends()]):
    user = await User.get(user_id)
    if user:
        update_data = {k: v for k, v in item.dict().items() if v is not None}
        if update_data:
            await User.update(user_id, **update_data)
            if user_id in active_tasks:
                active_tasks[user_id].cancel()
            await update_status(user)
            task = asyncio.create_task(increase_energy(user_id, item.energy, user.max_energy))
            active_tasks[user_id] = task
            return {"ok": True, "data": update_data}
        else:
            return {"ok": False, "message": "Nothing to update"}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@user_router.delete("/{user_id}")
async def user_delete(user_id: int):
    await User.delete(user_id)
    return {"ok": True, 'id': user_id}
