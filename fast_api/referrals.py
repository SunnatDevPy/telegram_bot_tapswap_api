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
from fast_api.utils import update_status

referral_router = APIRouter(prefix='/referrals', tags=['Referral'])


class RefferalList(BaseModel):
    id: int
    referrer_id: int
    referred_user_id: int
    hour_coin: int


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
    await asyncio.sleep(28800)
    if user.id in active_tasks:
        del active_tasks[user.id]
        for i in await Referral.get_from_referral_id(user.id):
            await Referral.update(i.id, is_active=False)


timezone = pytz.timezone('Asia/Tashkent')


@referral_router.post('/activate/')
async def referral_activate_user(user: Annotated[UserId, Depends(get_current_user)]):
    if user.id in active_tasks:
        raise HTTPException(status_code=400, detail="Hozirgi vazifa davom etmoqda, kuting")
    else:
        utc_now = datetime.datetime.utcnow()
        tashkent_now = utc_now.replace(tzinfo=pytz.utc).astimezone(timezone)
        times_user[user.id] = {"start_time": tashkent_now,
                               "end_time": tashkent_now + timedelta(seconds=28800)}
        task = asyncio.create_task(claim_friends(user))
        active_tasks[user.id] = task
        for i in await Referral.get_from_referral_id(user.id):
            await Referral.update(i.id, is_active=True, hour_8_coin=0)
        return {
            'ok': True,
            "start_time": tashkent_now,
            "end_time": tashkent_now + timedelta(seconds=28800)
        }


@referral_router.post('/claim/')
async def activate_user(user: Annotated[UserId, Depends(get_current_user)]):
    coin = user.hour_coin
    await update_status(user)
    if user.id in active_tasks:
        raise HTTPException(status_code=400, detail="Hozirgi vazifa davom etmoqda, kuting")
    else:
        for i in await Referral.get_from_referral_id(user.id):
            await Referral.update(i.id, is_active=False, hour_8_coin=0)

        if user.id in times_user:
            del times_user[user.id]

        await User.update(user.id, coins=user.coins + coin, hour_coin=0)
        return {'ok': True,
                "firends_coin": coin, "time": times_user.get(user.id), 'status': "claim"}


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


# @referral_router.post("/add-coins/{referrer_id}")
# def add_coins_to_friends(referrer_id: int):
#     # Находим всех друзей, которых пригласил пользователь с referrer_id
#     referrals = db.query(Referral).filter(Referral.referrer_id == referrer_id).all()
#
#     if not referrals:
#         raise HTTPException(status_code=404, detail="No referrals found.")
#
#     # Добавляем указанное количество очков каждому другу
#     for referral in referrals:
#         referral.hour_8_coin += request.coins
#
#     db.commit()  # Сохраняем изменения в базе данных
#
#     return {"message": f"{request.coins} coins added to all referred users."}


# @app.get("/referral/points/{referrer_id}")
# def get_referral_points(referrer_id: int, db: Session = Depends(get_db)):
#     referrals = db.query(Referral).filter(Referral.referrer_id == referrer_id).all()
#
#     if not referrals:
#         raise HTTPException(status_code=404, detail="No referrals found.")
#
#     total_points = sum(referral.hour_8_coin for referral in referrals)
#     return {"total_points": total_points}


@referral_router.get("/unique-people")
async def get_unique_people():
    refferals = await Referral.get_alls()
    unique_people = await remove_duplicates(refferals)

    return unique_people

# Эндпоинт для получения списка людей и удаления дубликатов
