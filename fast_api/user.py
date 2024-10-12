import asyncio
from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette.responses import JSONResponse

from db import User, Statusie
from db.models.model import UserAndExperience
from fast_api.jwt_ import get_current_user
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
async def user_list(user_token=Depends(get_current_user)) -> list[UserList]:
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


class UserData(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    is_admin: Optional[bool] = None
    hour_coin: Optional[int] = None
    updated_at: Optional[str] = None
    id: Optional[int] = None
    username: Optional[str] = None
    coins: Optional[int] = None
    status_id: Optional[int] = None
    bonus: Optional[int] = None
    energy: Optional[int] = None
    max_energy: Optional[int] = None
    created_at: Optional[str] = None


class Status(BaseModel):
    name: str
    id: int
    created_at: str
    limit_coin: int
    level: int
    updated_at: str


class UserId(BaseModel):
    id: int


class Rank(BaseModel):
    status: str
    rank: int


class ResponseModel(BaseModel):
    user_data: UserData
    status: Status
    hour_coin: int
    rank: Rank


@user_router.get("/")
async def user_detail(user: Annotated[UserData, Depends(get_current_user)]):
    status = await Statusie.get(user.status_id)
    response_data = ResponseModel(
    user_data=UserData(first_name=user.first_name, last_name=user.last_name, phone=user.phone,
                           is_admin=user.is_admin,
                           hour_coin=user.hour_coin,
                           updated_at=str(user.updated_at),
                           id=user.id,
                           username=user.username,
                           coins=user.coins,
                           status_id=user.status_id,
                           bonus=user.bonus,
                           energy=user.energy,
                           max_energy=user.max_energy,
                           created_at=str(user.created_at)),
        status=Status(id=status.id, name=status.name, limit_coin=status.limit_coin, level=status.level,
                      created_at=str(status.created_at), updated_at=str(status.updated_at)),
        hour_coin=user.hour_coin,
        rank=await top_players_from_statu_rank(user.id, status)
    )
    return JSONResponse(content=response_data.dict())
    # return {"status": status, "user": user, "rank": await top_players_from_statu_rank(user.id, status)}


@user_router.get("/top/")
async def users_top_rank():
    return {"top_10": await top_players_from_statu()}


@user_router.get("/experience/")
async def user_get_friends(user=Depends(get_current_user)):
    experience = await UserAndExperience.get_from_user_id_experience(user.id)
    return {"user_data": user, 'experience': await get_detail_experience(experience)}


@user_router.get("/friends/")
async def user_get_friends(user=Depends(get_current_user)):
    friend = await friends_detail(user.id)
    return {"user_data": user, "friends": friend[0], "friends_price": friend[-1]}


async def increase_energy(user_id, energy, max_energy):
    while max_energy != energy:
        energy += 4
        if energy > max_energy:
            await User.update(user_id, energy=max_energy)
            break
        await asyncio.sleep(3)
        await User.update(user_id, energy=energy)


# coin energy update
@user_router.patch("/detail/")
async def user_patch_update(item: Annotated[UserPatch, Depends()], user=Depends(get_current_user)):
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


@user_router.patch("/")
async def user_coin_energy_update(coin: int, energy: int, user=Depends(get_current_user)):
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


@user_router.delete("/")
async def user_delete(user=Depends(get_current_user)):
    await User.delete(user.id)
    return {"ok": True, 'id': user.id}

# Instagram,
# https://www.instagram.com/
# Telegram,
# https://web.telegram.org/a/
# Youtube,
# https://www.youtube.com/
# Facebook,
# https://www.facebook.com/?locale=ru_RU
