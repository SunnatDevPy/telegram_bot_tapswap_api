import asyncio
from datetime import timedelta, datetime
from typing import Annotated, Optional

import pytz
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from db import User, Statusie
from db.models.model import UserAndExperience
from fast_api.jwt_ import get_current_user
from fast_api.referrals import times_user
from fast_api.utils import get_detail_experience, top_players_from_statu, friends_detail, top_players_from_statu_rank, \
    update_status

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


# @user_router.post("/actives/{active}")
# async def all_users_default(active: bool):
#     if active:
#         users = await User.get_alls()
#         for i in users:
#             await User.update(i.id, coins=0, energy=200, status_id=1, max_energy=200)
#         return {'ok': True}
#     return {'ok': False}


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
    coins: Optional[int] = None
    bonus: Optional[int] = None
    energy: Optional[int] = 0
    max_energy: Optional[int] = None


active_tasks = {}


class UserId(BaseModel):
    id: Optional[int] = None


# Annotated[UserId, Depends(get_current_user)]

@user_router.get("/")
async def user_detail(user: Annotated[UserId, Depends(get_current_user)]):
    user = await User.get(user.id)
    if user:
        status = await Statusie.get(user.status_id)
        return {"status": status, "user": user, "rank": await top_players_from_statu_rank(user.id, status)}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@user_router.get("/top/")
async def users_top_rank(user: Annotated[UserId, Depends(get_current_user)]):
    return {"top_10": await top_players_from_statu()}


@user_router.get("/experience/")
async def user_get_friends(user: Annotated[UserId, Depends(get_current_user)]):
    experience = await UserAndExperience.get_from_user_id_experience(user.id)
    return {"user_data": user, 'experience': await get_detail_experience(experience)}


timezone = pytz.timezone('Asia/Tashkent')


@user_router.get("/friends/")
async def user_get_friends(user: Annotated[UserId, Depends(get_current_user)]):
    user = await User.get(user.id)
    if user:
        friend = await friends_detail(user.id)
        utc_now = datetime.utcnow()
        time = times_user.get(user.id)
        return {"user_data": user, "friends": friend[0], "friends_price": friend[-1], "date": time}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


class UserUsername(BaseModel):
    username: str


@user_router.get("/by/")
async def get_by_username(user_data: UserUsername):
    print(user_data)
    user = await User.get_user_by_username(user_data.username)
    if user:
        return {"user_data": user}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@user_router.get("/sum/")
async def user_sum_coin(user: Annotated[UserId, Depends(get_current_user)]):
    sum = await User.sum_coin()
    return {"sum coin": f"{int(sum):_}"}


async def increase_energy(user_id, energy, max_energy):
    while max_energy != energy:
        energy += 1
        await asyncio.sleep(3)
        await User.update(user_id, energy=energy)


# coin energy update
@user_router.patch("/detail/")
async def user_patch_update(user: Annotated[UserId, Depends(get_current_user)], item: Annotated[UserPatch, Depends()]):
    user = await User.get(user.id)
    if user:
        update_data = {k: v for k, v in item.dict().items() if v is not None}
        if update_data:
            if update_data['coins'] > 0:
                await User.update(user.id, **update_data)
                if user.id in active_tasks:
                    active_tasks[user.id].cancel()
                await update_status(user)
                task = asyncio.create_task(increase_energy(user.id, item.energy, user.max_energy))
                active_tasks[user.id] = task

                return {"ok": True, "data": update_data}
            else:
                raise HTTPException(status_code=404, detail="0 dan kichik son kevotdi qara")
        else:
            return {"ok": False, "message": "Nothing to update"}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@user_router.patch("/")
async def user_coin_energy_update(coin: int, energy: int, user: Annotated[UserId, Depends(get_current_user)]):
    user = await User.get(user.id)
    if user:
        if coin > 0:
            await User.update(user.id, coins=coin, energy=energy)
            if user.id in active_tasks:
                active_tasks[user.id].cancel()
            await update_status(user)
            task = asyncio.create_task(increase_energy(user.id, energy, user.max_energy))
            active_tasks[user.id] = task

            return {"ok": True, "user": user}
        else:
            raise HTTPException(status_code=404, detail="0 dan kichik son kevotdi qara")
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@user_router.delete("/")
async def user_delete(user: Annotated[UserId, Depends(get_current_user)]):
    await User.delete(user.id)
    return {"ok": True, 'id': user.id}
