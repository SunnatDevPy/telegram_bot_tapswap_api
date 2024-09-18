from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from db import User, Experience

experience = APIRouter(prefix='/experience', tags=['Experience'])


class ExperienceAdd(BaseModel):
    name: str
    price: int


@experience.post("")
async def experience_add(tap: Annotated[ExperienceAdd, Depends()]):
    tap = await Experience.create(**tap.dict())
    return {'ok': True, "tap_id": tap.id, "user_id": tap.user_id}


@experience.get('')
async def experience_list() -> list[ExperienceAdd]:
    users = await Experience.get_all()
    return users


@experience.get("/{experience_id}")
async def experience_detail(experience_id: int):
    experience = await Experience.get(experience_id)
    return {"detail": experience}


class ExperiencePatch(BaseModel):
    name: str
    price: int


@experience.patch("/{experience_id}", response_model=ExperiencePatch)
async def user_patch(user_id: int, item: ExperiencePatch):
    experience = await Experience.get(user_id)
    if experience:
        update_data = {k: v for k, v in item.dict().items() if v is not None}
        if update_data:
            await Experience.update(user_id, **update_data)
            return {"ok": True, "data": update_data}
        else:
            return {"ok": False, "message": "Nothing to update"}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@experience.put("/{experience_id}", response_model=ExperienceAdd)
async def user_put(user_id: int, items: ExperienceAdd):
    experience = await Experience.get(user_id)
    if experience:
        await User.update(experience.id, **items.dict())
        return {"ok": True, "data": items}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@experience.delete("/{experience_id}")
async def user_delete(experience_id: int):
    await Experience.delete(experience_id)
    return {"ok": True, 'id': experience_id}
