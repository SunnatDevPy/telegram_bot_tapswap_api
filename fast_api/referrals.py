import asyncio
import datetime
from datetime import timedelta
from typing import Annotated, List

import pytz
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from db import User
from db.models.model import Referral
from fast_api.utils import friends_coin, update_status

referral_router = APIRouter(prefix='/referrals', tags=['Referral'])


class RefferalList(BaseModel):
    id: int
    referrer_id: int
    referred_user_id: int
    created_at: datetime.datetime


timezone = pytz.timezone('Asia/Tashkent')


@referral_router.post("/{user_id}")
async def register_user(user_id: int):
    return {"url": f"https://t.me/share/url?url=https://t.me/Stockfootball_bot?start={user_id}"}


@referral_router.post("")
async def referral_add(user: Annotated[RefferalList, Depends()]):
    user = await Referral.create(**user.dict())
    return {'ok': True, "id": user.id}


@referral_router.get("")
async def referral_list() -> list[RefferalList]:
    return await Referral.get_alls()


active_tasks = {}


async def claim_friends(user):
    await asyncio.sleep(28800)
    if user.id in active_tasks:
        del active_tasks[user.id]


@referral_router.post('/activate/{user_id}')
async def referral_activate_user(user_id: int):
    user = await User.get(user_id)
    if user:
        coin = await friends_coin(user_id)
        if user_id in active_tasks:
            raise HTTPException(status_code=400, detail="Hozirgi vazifa davom etmoqda, kuting")
        else:
            utc_now = datetime.datetime.utcnow()
            task = asyncio.create_task(claim_friends(user))
            active_tasks[user_id] = task
            return {'ok': True, "start_time": utc_now.astimezone(timezone),
                    "end_time": utc_now.astimezone(timezone) + timedelta(seconds=28800),
                    "firends_coin": coin * 8}

    else:
        raise HTTPException(status_code=404, detail="Item not found")


@referral_router.post('/claim/{user_id}')
async def activate_user(user_id: int):
    user = await User.get(user_id)
    if user:
        coin = await friends_coin(user_id)
        await update_status(user)
        if user_id in active_tasks:
            raise HTTPException(status_code=400, detail="Hozirgi vazifa davom etmoqda, kuting")
        else:
            await User.update(user_id, coins=user.coins + (coin * 8))
            return {'ok': True,
                    "firends_coin": coin * 8, "status": 'claim'}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@referral_router.delete("/")
async def referral_delete(referral_id: int):
    await Referral.delete(referral_id)
    return {"ok": True, 'id': referral_id}


async def remove_duplicates(people: List[RefferalList]) -> List[RefferalList]:
    seen = set()
    unique_people = []

    for person in people:
        identifier = (person.referrer_id, person.referred_user_id)
        if identifier not in seen:
            unique_people.append(person)
            seen.add(identifier)
        else:
            await Referral.delete(person.id)

    return unique_people


@referral_router.get("/unique-people")
async def get_unique_people():
    refferals = await Referral.get_alls()
    unique_people = await remove_duplicates(refferals)

    return unique_people

# Эндпоинт для получения списка людей и удаления дубликатов
