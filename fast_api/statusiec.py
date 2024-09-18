from db import Statusie
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from db import User

status_router = APIRouter(prefix='/status', tags=['Status'])


class StatusAdd(BaseModel):
    first_name: str
    last_name: str
    username: Optional[str] = None
    phone: str
    is_admin: Optional[bool] = False
    coins: int
    role: Optional[str] = 'user'


@status_router.post("")
async def user_add(status: Annotated[StatusAdd, Depends()]):
    status = await Statusie.create(**status.dict())
    return {'ok': True, "id": status.id}


@status_router.get('')
async def user_list() -> list[StatusAdd]:
    status = await Statusie.get_all()
    return status


@status_router.get("/{status_id}")
async def user_detail(user_id: int):
    user = await User.get(user_id)
    return {"detail": user}


class StatusPatch(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    phone: Optional[str] = None
    is_admin: Optional[bool] = False
    coins: Optional[int] = None
    role: Optional[str] = 'user'


@status_router.patch("/{status_id}", response_model=StatusPatch)
async def user_patch(status_id: int, item: StatusPatch):
    user = await Statusie.get(status_id)
    if user:
        update_data = {k: v for k, v in item.dict().items() if v is not None}
        if update_data:
            await Statusie.update(status_id, **update_data)
            return {"ok": True, "data": update_data}
        else:
            return {"ok": False, "message": "Nothing to update"}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@status_router.put("/{status_id}", response_model=StatusAdd)
async def user_put(status_id: int, items: StatusAdd):
    user = await Statusie.get(status_id)
    if user:
        await Statusie.update(user.id, **items.dict())
        return {"ok": True, "data": items}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@status_router.delete("/{status_id}")
async def user_delete(status_id: int):
    await Statusie.delete(status_id)
    return {"ok": True, 'id': status_id}
