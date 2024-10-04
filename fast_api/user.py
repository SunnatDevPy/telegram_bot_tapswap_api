import asyncio
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from db import User, Statusie
from db.models.model import UserAndExperience
from fast_api.utils import get_detail_experience, top_players_from_statu, friends_detail, \
    top_players_from_statu_rank

user_router = APIRouter(prefix='/users', tags=['User'])


class UserAdd(BaseModel):
    first_name: str
    last_name: str
    username: Optional[str] = None
    phone: str
    is_admin: Optional[bool] = False
    status_id: int
    coins: Optional[int] = 0
    bonus: Optional[int] = 1
    energy: Optional[int] = 200
    max_energy: Optional[int] = 200
    hour_coin: Optional[int] = 0


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
    hour_coin: Optional[int] = None


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
    energy: Optional[int] = 0
    max_energy: Optional[int] = None


active_tasks = {}


async def update_status(user):
    status = await Statusie.get(user.status_id)
    status_by_level = await Statusie.get_from_level(status.level + 1)
    if status_by_level:
        if user.coins > status.limit_coin:
            await User.update(user.id, status_id=status_by_level.id, max_energy=user.max_energy + 400,
                              bonus=user.bonus + 1)
    else:
        return


@user_router.get("/{user_id}")
async def user_detail(user_id: int):
    user = await User.get(user_id)
    if user:
        status = await Statusie.get(user.status_id)
        return {"user_data": user, "status": status,
                'hour_coin': user.hour_coin, "rank": await top_players_from_statu_rank(user_id, status)}

    else:
        raise HTTPException(status_code=404, detail="Item not found")


@user_router.get("/top/")
async def users_top_rank():
    return {"top_10": await top_players_from_statu()}


@user_router.get("/experience/{user_id}")
async def user_get_friends(user_id: int):
    user = await User.get(user_id)
    if user:
        experience = await UserAndExperience.get_from_user_id_experience(user_id)
        return {"user_data": user, 'experience': await get_detail_experience(experience)}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@user_router.get("/friends/{user_id}")
async def user_get_friends(user_id: int):
    user = await User.get(user_id)
    if user:
        friend = await friends_detail(user_id)
        return {"user_data": user, "friends": friend[0], "friends_price": friend[-1]}
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
@user_router.patch("/detail/{user_id}")
async def user_patch_update(user_id: int, item: Annotated[UserPatch, Depends()]):
    user = await User.get(user_id)
    if user:
        update_data = {k: v for k, v in item.dict().items() if v is not None}
        if update_data:
            if update_data['coins'] > 0:
                await User.update(user_id, **update_data)
                if user_id in active_tasks:
                    active_tasks[user_id].cancel()
                await update_status(user)
                task = asyncio.create_task(increase_energy(user_id, item.energy, user.max_energy))
                active_tasks[user_id] = task
                return {"ok": True, "data": update_data}
            else:
                raise HTTPException(status_code=404, detail="0 dan kichik son kevotdi qara")
        else:
            return {"ok": False, "message": "Nothing to update"}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@user_router.patch("/{user_id}")
async def user_coin_energy_update(user_id: int, coin: int, energy: int):
    user = await User.get(user_id)
    if user:
        if coin > 0:
            await User.update(user_id, coins=coin, energy=energy)
            if user_id in active_tasks:
                active_tasks[user_id].cancel()
            await update_status(user)
            task = asyncio.create_task(increase_energy(user_id, energy, user.max_energy))
            active_tasks[user_id] = task
            return {"ok": True, "user": user}
        else:
            raise HTTPException(status_code=404, detail="0 dan kichik son kevotdi qara")
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@user_router.delete("/{user_id}")
async def user_delete(user_id: int):
    await User.delete(user_id)
    return {"ok": True, 'id': user_id}

# Instagram,
# https://www.instagram.com/
# Telegram,
# https://web.telegram.org/a/
# Youtube,
# https://www.youtube.com/
# Facebook,
# https://www.facebook.com/?locale=ru_RU
