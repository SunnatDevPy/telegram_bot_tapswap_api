import asyncio
import datetime
from datetime import timedelta
from time import time, sleep

from fastapi import APIRouter, HTTPException

from db import User
from fast_api.utils import friends_detail

referral_router = APIRouter(prefix='/referral', tags=['Referral'])


async def starting_friends(user):
    friend_price = await friends_detail(user.id)
    await User.update(user.id, coins=user.coins + friend_price[-1])
    activation_time = datetime.datetime.now()
    for _ in range(8):
        sleep(2)
    end_time = activation_time + timedelta(hours=8)
    return {"coin": friend_price[-1], "activate_time": activation_time, "end_time": end_time}


@referral_router.post("/{user_id}")
async def register_user(user_id: int):
    return {"url": f"https://t.me/share/url?url=https://t.me/AlEzozMIlliyTaomlarbot?start={user_id}"}


@referral_router.post('/activate/{user_id}')
async def activate_user(user_id: int):
    user = await User.get(user_id)
    if user:
        res = await starting_friends(user)
        return res
    else:
        raise HTTPException(status_code=404, detail="Item not found")
