import asyncio
import datetime
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from requests import Response

from db import User, Experience
from db.models.model import UserAndExperience
from fast_api.utils import hour_coin_check

experience = APIRouter(prefix='/experience', tags=['Experience'])


class ExperienceAdd(BaseModel):
    name: str
    description: str
    price: int
    photo: str
    degree: int
    hour_coin: int


async def save_numbers_every_hour(user_id):
    hour = await hour_coin_check(int(user_id))
    coin = 0
    activation_time = datetime.datetime.now()
    for _ in range(3):
        await asyncio.sleep(3600)
        coin += hour
    end_time = activation_time + timedelta(hours=3)
    return {"coin": coin, "activate_time": activation_time, "end_time": end_time}


@experience.post("/{user_id}")
async def experience_activate_degree(user_id: int, activate: bool):
    users = await User.get(user_id)
    if users and activate:

        hour = await save_numbers_every_hour(user_id)
        await User.update(user_id, coins=users.coins + hour.get('coin'))
        return {'ok': True, "user": users, "response": hour}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@experience.post("")
async def experience_add(experience_id: Annotated[ExperienceAdd, Depends()]):
    experience = await Experience.create(**experience_id.dict())
    users = await User.get_all()
    for i in users:
        await UserAndExperience.create(user_id=i.id, degree=experience.degree, hour_coin=experience.hour_coin,
                                       price=experience.price,
                                       experience_id=experience.id)
    return {'ok': True, "experience": experience.id}


@experience.get('')
async def experience_list() -> list[ExperienceAdd]:
    experience = await Experience.get_all()
    return experience


@experience.post("/sale/{experience_id}")
async def experience_detail(experience_id: int, user_id: int):
    user = await User.get(user_id)
    experience_from_user = await UserAndExperience.get_experience_from_user(user_id, experience_id)
    if experience_from_user and user_id:
        if user.coins > experience_from_user.price:
            if experience_from_user.degree == 4 or experience_from_user.degree == 9 or experience_from_user.degree == 15:
                bonus = 1
                max_energy = 400
            else:
                bonus = 0
                max_energy = 0
            await UserAndExperience.update(experience_from_user.id, degree=experience_from_user.degree + 1,
                                           price=experience_from_user.price + experience_from_user.price,
                                           hour_coin=experience_from_user.hour_coin + int(
                                               (experience_from_user.price * 30) / 100))
            await User.update(user_id, coins=user.coins - experience_from_user.price, bonus=user.bonus + bonus,
                              max_energy=user.max_energy + 50 + max_energy)

            return await User.get(user_id)
        else:
            raise HTTPException(status_code=404, detail="Kartochka qimmat ishlab ke")
    else:
        raise HTTPException(status_code=404, detail="User topilmadi yoki daraja unga tegishli emas")


class ExperiencePatch(BaseModel):
    name: str
    description: str
    price: int
    photo: str
    degree: int
    hour_coin: int


@experience.patch("/{experience_id}", response_model=ExperiencePatch)
async def experience_patch(experience_id: int, item: ExperiencePatch):
    experience = await Experience.get(experience_id)
    if experience:
        update_data = {k: v for k, v in item.dict().items() if v is not None}
        if update_data:
            await Experience.update(experience_id, **update_data)
            return {"ok": True, "data": update_data}
        else:
            return {"ok": False, "message": "Nothing to update"}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@experience.delete("/{experience_id}")
async def experience_delete(experience_id: int):
    await Experience.delete(experience_id)
    return {"ok": True, 'id': experience_id}
