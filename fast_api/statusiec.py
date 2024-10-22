from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from db import Statusie
from fast_api.jwt_ import get_current_user

status_router = APIRouter(prefix='/status', tags=['Status'])


class UserId(BaseModel):
    id: Optional[int] = None


class StatusAdd(BaseModel):
    name: str
    limit_coin: int
    level: int


class StatusList(BaseModel):
    id: int
    name: str
    limit_coin: int
    level: int


@status_router.post("")
async def status_add(status: Annotated[StatusAdd, Depends()], user: Annotated[UserId, Depends(get_current_user)]):
    status = await Statusie.create(**status.dict())
    return {'ok': True, "id": status.id}


@status_router.get('')
async def status_list() -> list[StatusList]:
    status = await Statusie.get_alls()
    return status


@status_router.get("/{status_id}")
async def status_detail(status_id: int):
    user = await Statusie.get(status_id)
    return {"detail": user}


class StatusPatch(BaseModel):
    name: Optional[str] = None
    limit_coin: Optional[int] = None
    level: Optional[int] = None


@status_router.patch("/{status_id}")
async def status_patch(status_id: int, item: Annotated[StatusPatch, Depends()],
                       user: Annotated[UserId, Depends(get_current_user)]):
    user = await Statusie.get(status_id)
    if user:
        update_data = {k: v for k, v in item.dict().items() if v is not None}
        if update_data:
            await Statusie.update(status_id, **update_data)
            return {"ok": True, "data": user}
        else:
            return {"ok": False, "message": "Nothing to update"}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@status_router.delete("/{status_id}")
async def status_delete(status_id: int, user: Annotated[UserId, Depends(get_current_user)]):
    await Statusie.delete(status_id)
    return {"ok": True, 'id': status_id}
