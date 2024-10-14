from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from db import User
from db.models.model import Event, UserAndEvent
from fast_api.utils import get_events

event_router = APIRouter(prefix='/events', tags=['Events'])


class EventAdd(BaseModel):
    name: str
    url: str
    timer: int
    coin: int


class EventList(BaseModel):
    id: int
    name: str
    timer: int
    url: str
    coin: int


@event_router.post("")
async def event_add(event: Annotated[EventAdd, Depends()]):
    event = await Event.create(**event.dict())
    users = await User.get_all()
    print(event)
    for i in users:
        await UserAndEvent.create(user_id=i.id, event_id=event.id)
    return {'ok': True, "event": event.id}


@event_router.post("/{user_id}")
async def event_add(user_id: int, event_id: int):
    event = await Event.get(event_id)
    user = await User.get(user_id)
    if event and user:
        await UserAndEvent.update_event(user_id, event_id, status=True)
        await User.update(user_id, coins=user.coins + event.coin)
        return {'ok': True, "user": user, "ball": event.coin}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@event_router.get('')
async def event_list() -> list[EventList]:
    event = await Event.get_alls()
    return event


@event_router.get('/{user_id}')
async def event_from_user_list(user_id: int):
    return await get_events(user_id)


class EventPatch(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    coin: Optional[int] = None


@event_router.patch("/{event_id}", response_model=EventPatch)
async def event_patch(event_id: int, item: EventPatch):
    event = await Event.get(event_id)
    if event:
        update_data = {k: v for k, v in item.dict().items() if v is not None}
        if update_data:
            await Event.update(event, **update_data)
            return {"ok": True, "data": update_data}
        else:
            return {"ok": False, "message": "Nothing to update"}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@event_router.delete("/{event_id}")
async def event_delete(event_id: int):
    await Event.delete(event_id)
    return {"ok": True, 'id': event_id}
