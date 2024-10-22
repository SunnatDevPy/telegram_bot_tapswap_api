import asyncio
import datetime
from datetime import timedelta
from typing import Annotated
from typing import List, Optional

import pytz
from fastapi import APIRouter
from fastapi import HTTPException, Depends
from pydantic import BaseModel

from db import User
from db.models.model import Referral
from fast_api.jwt_ import get_current_user
from fast_api.utils import friends_coin, update_status

referral_router = APIRouter(prefix='/referrals', tags=['Referral'])


class RefferalList(BaseModel):
    id: int
    referrer_id: int
    referred_user_id: int
    created_at: datetime.datetime


class UserId(BaseModel):
    id: Optional[int] = None


@referral_router.post("/")
async def register_user(user: Annotated[UserId, Depends(get_current_user)]):
    return {"url": f"https://t.me/share/url?url=https://t.me/Stockfootball_bot?start={user.id}"}


@referral_router.post("")
async def referral_add(user: Annotated[RefferalList, Depends()], users: Annotated[UserId, Depends(get_current_user)]):
    user = await Referral.create(**user.dict())
    return {'ok': True, "id": user.id}


@referral_router.get("")
async def referral_list() -> list[RefferalList]:
    return await Referral.get_alls()


active_tasks = {}
times_user = {}


async def claim_friends(user):
    await asyncio.sleep(10)
    if user.id in active_tasks:
        del active_tasks[user.id]


timezone = pytz.timezone('Asia/Tashkent')


@referral_router.post('/activate/')
async def referral_activate_user(user: Annotated[UserId, Depends(get_current_user)]):
    coin = await friends_coin(user.id)
    if user.id in active_tasks:
        raise HTTPException(status_code=400, detail="Hozirgi vazifa davom etmoqda, kuting")
    else:
        utc_now = datetime.datetime.utcnow()
        tashkent_now = utc_now.replace(tzinfo=pytz.utc).astimezone(timezone)  # Convert UTC to Tashkent timezone
        times_user[user.id] = {"start_time": tashkent_now,
                               "end_time": tashkent_now + timedelta(seconds=10)}
        task = asyncio.create_task(claim_friends(user))
        active_tasks[user.id] = task

        return {
            'ok': True,
            "start_time": tashkent_now,
            "end_time": tashkent_now + timedelta(seconds=10),
            "firends_coin": coin * 8
        }


@referral_router.post('/claim/')
async def activate_user(user: Annotated[UserId, Depends(get_current_user)]):
    coin = await friends_coin(user.id)
    await update_status(user)
    if user.id in active_tasks:
        raise HTTPException(status_code=400, detail="Hozirgi vazifa davom etmoqda, kuting")
    else:
        if user.id in times_user:
            del times_user[user.id]
        await User.update(user.id, coins=user.coins + (coin * 8))
        return {'ok': True,
                "firends_coin": coin * 8, "time": times_user.get(user.id), 'status': "claim"}


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
