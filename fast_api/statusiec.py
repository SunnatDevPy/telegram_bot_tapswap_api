from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from db import Statusie

status_router = APIRouter(prefix='/status', tags=['Status'])


class StatusAdd(BaseModel):
    name: str
    limit_coin: int


@status_router.post("")
async def status_add(status: Annotated[StatusAdd, Depends()]):
    status = await Statusie.create(**status.dict())
    return {'ok': True, "id": status.id}


@status_router.get('')
async def status_list() -> list[StatusAdd]:
    status = await Statusie.get_all()
    return status


@status_router.get("/{status_id}")
async def status_detail(status_id: int):
    user = await Statusie.get(status_id)
    return {"detail": user}


class StatusPatch(BaseModel):
    name: str
    limit_coin: int


@status_router.patch("/{status_id}", response_model=StatusPatch)
async def status_patch(status_id: int, item: StatusPatch):
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
async def status_put(status_id: int, items: StatusAdd):
    status = await Statusie.get(status_id)
    if status:
        await Statusie.update(status.id, **items.dict())
        return {"ok": True, "data": items}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@status_router.delete("/{status_id}")
async def status_delete(status_id: int):
    await Statusie.delete(status_id)
    return {"ok": True, 'id': status_id}
