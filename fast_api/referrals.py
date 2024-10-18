import asyncio
import datetime
from datetime import timedelta
from typing import Annotated

import pytz
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from db import User
from db.models.model import Referral
from fast_api.utils import friends_coin

referral_router = APIRouter(prefix='/referrals', tags=['Referral'])


class RefferalList(BaseModel):
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
async def activate_user(user_id: int):
    user = await User.get(user_id)
    if user:
        print(active_tasks)
        coin = await friends_coin(user_id)

        if user_id in active_tasks:
            raise HTTPException(status_code=400, detail="Hozirgi vazifa davom etmoqda, kuting")
        else:
            utc_now = datetime.datetime.utcnow()
            local_time = utc_now.astimezone(timezone)
            task = asyncio.create_task(claim_friends(user))
            active_tasks[user_id] = task
            return {'ok': True, "start_time": utc_now.astimezone(timezone),
                    "end_time": utc_now.astimezone(timezone) + timedelta(seconds=28800),
                    "firends_coin": coin * 8}

    else:
        raise HTTPException(status_code=404, detail="Item not found")
# 7123665308

# @referral_router.get("")
# async def referral_list_from_refferals() -> list[RefferalList]:
#     return await Referral.get_from_referral_and_referred_all()

@referral_router.get("/from_id/")
async def referral_list_id() -> list[RefferalList]:
    return await Referral.get_from_referral_ids(7123665308)



@referral_router.post('/claim/{user_id}')
async def activate_user(user_id: int):
    user = await User.get(user_id)
    if user:
        coin = await friends_coin(user_id)
        if user_id in active_tasks:
            raise HTTPException(status_code=400, detail="Hozirgi vazifa davom etmoqda, kuting")
        else:
            await User.update(user_id, coins=user.coins + coin)
            return {'ok': True,
                    "firends_coin": coin * 8, "status": 'claim'}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@referral_router.delete("/")
async def referral_delete(referral_id: int):
    await Referral.delete(referral_id)
    return {"ok": True, 'id': referral_id}
