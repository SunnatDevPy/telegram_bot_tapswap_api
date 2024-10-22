from typing import Annotated, Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from db import User
from db.models.model import Event, UserAndEvent
from fast_api.jwt_ import get_current_user
from fast_api.utils import get_events, update_status

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


class UserId(BaseModel):
    id: Optional[int] = None


@event_router.post("")
async def event_add(event: Annotated[EventAdd, Depends()]):
    event = await Event.create(**event.dict())
    users = await User.get_all()
    for i in users:
        await UserAndEvent.create(user_id=i.id, event_id=event.id)
    return {'ok': True, "event": event.id}


@event_router.post("/")
async def event_active_from_user(event_id: int, user: Annotated[UserId, Depends(get_current_user)]):
    event = await Event.get(event_id)
    if event and user:
        await UserAndEvent.update_event(user.id, event_id, status=True)
        await User.update(user.id, coins=user.coins + event.coin)
        await update_status(user)
        return {'ok': True, "user": user, "ball": event.coin}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@event_router.get('')
async def event_list() -> list[EventList]:
    events = await Event.get_alls()
    return events


@event_router.get('/list/')
async def event_from_user_list(user: Annotated[UserId, Depends(get_current_user)]):
    return await get_events(user.id)


@event_router.post('/change/{user_id}')
async def event_change_from_user(user: Annotated[UserId, Depends(get_current_user)]):
    events = await UserAndEvent.get_from_user_id(user.user_id)
    if events:
        for i in events:
            await UserAndEvent.update(i.id, status=False)
        return await get_events(user.user_id)
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@event_router.post('/all/user/')
async def events_change_all_users():
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
async def events_from_user_delete(user: Annotated[UserId, Depends(get_current_user)]):
    users = await User.get_alls()
    if users:
        for user in users:
            await UserAndEvent.delete(user.id)
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


class ParamEventList(BaseModel):
    id: Optional[int] = None
    event_id: Optional[int] = None
    status: Optional[str] = None
    user_id: Optional[int] = None


@event_router.get('')
async def param_event_list() -> list[ParamEventList]:
    events = await UserAndEvent.get_alls()
    return events


@event_router.patch("/{event_id}")
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
async def events_all_update(item: Annotated[EventPatch, Depends()], user: Annotated[UserId, Depends(get_current_user)]):
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


async def remove_duplicates_events(people: List[ParamEventList]) -> List[ParamEventList]:
    seen = set()
    unique_people = []

    for person in people:
        identifier = (person.event_id, person.user_id)
        if identifier not in seen:
            unique_people.append(person)
            seen.add(identifier)
        else:
            await UserAndEvent.delete(person.id)

    return unique_people


@event_router.get("/unique-event")
async def get_unique_event():
    user_events = await UserAndEvent.get_alls()
    unique_people = await remove_duplicates_events(user_events)
    return unique_people

# @event_router.delete("/{event_id}")
# async def event_delete(event_id: int):
#     await Event.delete(event_id)
#     return {"ok": True, 'id': event_id}
