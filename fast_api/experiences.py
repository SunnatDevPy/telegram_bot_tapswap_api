import asyncio
import datetime
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from db import User, Experience
from db.models.model import UserAndExperience

experience = APIRouter(prefix='/experience', tags=['Experience'])


class ExperienceAdd(BaseModel):
    name: str
    description: str
    price: int
    photo: str
    degree: int
    hour_coin: int


async def save_numbers_every_hour(user):
    await asyncio.sleep(10800)
    hour_coin = user.hour_coin * 3
    await User.update(user.id, coins=user.coins + hour_coin)
    if user.id in active_tasks:
        del active_tasks[user.id]


active_tasks = {}


@experience.post("/{user_id}")
async def experience_activate_degree(user_id: int, activate: bool):
    users = await User.get(user_id)
    if users and activate:
        print(active_tasks)
        if user_id in active_tasks:
            raise HTTPException(status_code=400, detail="8 soatdan o'tib ketmadi")
        task = asyncio.create_task(save_numbers_every_hour(users))
        active_tasks[user_id] = task
        return {'ok': True, "start_time": datetime.datetime.now(),
                "end_time": datetime.datetime.now() + timedelta(seconds=10800),
                "hour_coin_8": users.hour_coin * 3}
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
    experience = await Experience.get_alls()
    return experience


@experience.post("/sale/{experience_id}")
async def experience_detail(experience_id: int, user_id: int):
    user = await User.get(user_id)
    experience_ = await UserAndExperience.get_experience_from_users(user_id, experience_id)
    if experience_ and user_id:
        if user.coins > experience_.price or user.coins - experience_.price > 0:
            if experience_.degree == 4 or experience_.degree == 9 or experience_.degree == 14:
                bonus = 1
                max_energy = 400
            else:
                bonus = 0
                max_energy = 0
            await User.update(user_id, coins=user.coins - experience_.price, bonus=user.bonus + bonus,
                              max_energy=user.max_energy + 10 + max_energy,
                              hour_coin=user.hour_coin + experience_.next_coin)
            await UserAndExperience.update(experience_.id, degree=experience_.degree + 1,
                                           price=experience_.price + experience_.price,
                                           hour_coin=experience_.hour_coin + experience_.next_coin,
                                           next_coin=int((experience_.price * 0.5) / 100))
            return user
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
