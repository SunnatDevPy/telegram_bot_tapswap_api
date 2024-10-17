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
    photo: str


class EventList(BaseModel):
    id: int
    name: str
    timer: int
    url: str
    coin: int
    photo: str


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
    events = await Event.get_alls()
    return events


@event_router.get('/{user_id}')
async def event_from_user_list(user_id: int):
    return await get_events(user_id)


@event_router.post('/change/{user_id}')
async def event_from_user_event(user_id: int):
    events = await UserAndEvent.get_from_user_id(user_id)
    if events:
        for i in events:
            await UserAndEvent.update(i.id, status=False)
        return await get_events(user_id)
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@event_router.post('/all/user/')
async def event_from_user():
    events = await Event.get_alls()
    users = await User.get_alls()
    if events:
        for user in users:
            for event in events:
                await UserAndEvent.create(user_id=user.id, event_id=event.id, status=False)
        return {"ok": True}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@event_router.post('/delete/user/')
async def event_from_user_delete():
    users = await User.get_alls()
    if users:
        for user in users:
            await UserAndEvent.delete_question(user.id)
        return {"ok": True}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


class EventPatch(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    coin: Optional[int] = None
    photo: Optional[str] = None


class ParamEventPatch(BaseModel):
    event_id: Optional[int] = None
    status: Optional[str] = None
    user_id: Optional[int] = None
    claim: Optional[bool] = None


@event_router.patch("/{event_id}", response_model=EventPatch)
async def event_patch(event_id: int, item: Annotated[EventPatch, Depends()]):
    event = await Event.get(event_id)
    if event:
        update_data = {k: v for k, v in item.dict().items() if v is not None}
        if update_data:
            await Event.update(event.id, **update_data)
            return {"ok": True, "data": event}
        else:
            return {"ok": False, "message": "Nothing to update"}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@event_router.patch("/all/")
async def events_all_update(item: Annotated[EventPatch, Depends()]):
    question = await Event.get_all()
    if question:
        update_data = {k: v for k, v in item.dict().items() if v is not None}
        if update_data:
            for i in question:
                await Event.update(i.id, **update_data)
            return {"ok": True, "data": update_data}
        else:
            return {"ok": False, "message": "Nothing to update"}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@event_router.delete("/{event_id}")
async def event_delete(event_id: int):
    await Event.delete(event_id)
    return {"ok": True, 'id': event_id}
