from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from db import User

user_router = APIRouter(prefix='/users', tags=['User'])


class UserAdd(BaseModel):
    first_name: str
    last_name: str
    username: Optional[str] = None
    phone: str
    is_admin: Optional[bool] = False

    status_id: id
    coins: int
    bonus: int
    energy: int
    max_energy: int


class UserOk(BaseModel):
    ok: bool = True
    id: int


@user_router.post("")
async def user_add(user: Annotated[UserAdd, Depends()]):
    user = await User.create(**user.dict())
    return {'ok': True, "id": user.id}


@user_router.get('')
async def user_list() -> list[UserAdd]:
    users = await User.get_all()
    return users


class UserPatch(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    phone: Optional[str] = None
    is_admin: Optional[bool] = False

    status_id: id = None
    coins: int = None
    bonus: int = None
    energy: int = None
    max_energy: int


class UserCoin(BaseModel):
    coins: int = None
    energy: int = None


@user_router.get("/{user_id}")
async def user_detail(user_id: int):
    user = await User.get(user_id)
    return {"detail": user}


# @user_router.patch("coin/{user_id}", response_model=UserCoin)
# async def user_patch(user_id: int, item: UserCoin):
#     user = await User.get(user_id)
#     if user:
#         coin = 0
#         energy = 0
#         if item.minus == '+':
#             coin = user.coins + item.coins
#             energy = user.energy + item.coins if item.energy != 0 else 0
#         elif item.minus == '-':
#             coin = user.coins - item.coins
#             energy = user.energy - item.coins if item.energy != 0 else 0
#         update_data = {k: v for k, v in item.dict().items() if v is not None}
#         if update_data:
#             await User.update(user_id, coins=int(coin), energy=energy)
#             return {"ok": True, "data": update_data}
#         else:
#             return {"ok": False, "message": "Nothing to update"}
#     else:
#         raise HTTPException(status_code=404, detail="Item not found")


@user_router.patch("/{user_id}", response_model=UserPatch)
async def user_patch(user_id: int, item: UserPatch):
    user = await User.get(user_id)
    if user:
        update_data = {k: v for k, v in item.dict().items() if v is not None}
        if update_data:
            await User.update(user_id, **update_data)
            return {"ok": True, "data": update_data}
        else:
            return {"ok": False, "message": "Nothing to update"}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@user_router.put("/{user_id}", response_model=UserAdd)
async def user_put(user_id: int, items: UserAdd):
    user = await User.get(user_id)
    if user:
        await User.update(user.id, **items.dict())
        return {"ok": True, "data": items}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@user_router.delete("/{user_id}")
async def user_delete(user_id: int):
    await User.delete(user_id)
    return {"ok": True, 'id': user_id}
