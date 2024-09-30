import random
from typing import Annotated, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from db import User
from db.models.model import Questions, ParamQuestion


async def update_requests():
    questions = await Questions.get_all()
    users = await User.get_all()
    for i in users:
        random_questions = random.sample(questions, 20)
        for j in random_questions:
            await ParamQuestion.create(question_id=j.id, answer=False, user_id=i.id)


questions_router = APIRouter(prefix='/questions', tags=['Questions'])
scheduler = AsyncIOScheduler()
scheduler.add_job(update_requests, CronTrigger(hour=0, minute=0))
scheduler.start()


class QuestionAdd(BaseModel):
    description: str
    a: str
    b: str
    c: str
    d: str
    answer: str


class QuestionList(BaseModel):
    id: int
    description: str
    a: str
    b: str
    c: str
    d: str
    answer: str


@questions_router.post("")
async def question_add(question_item: Annotated[QuestionAdd, Depends()]):
    question = await Questions.create(**question_item.dict())
    return {'ok': True, "id": question.id}


@questions_router.post("/answer/")
async def question_add(user_id: int, question_id: int, answer: str):
    question = await Questions.get(question_id)
    user = await User.get(user_id)
    if question.answer == answer:
        await User.update(user_id, ball=user.ball + 1)
        await ParamQuestion.update_question(user_id, question_id, answer=True)
        return {'user_id': user, "answer": True}
    else:
        return {'user_id': user, "answer": False}


@questions_router.get('')
async def questions_list() -> list[QuestionList]:
    users = await Questions.get_all()
    return users


class QuestionPatch(BaseModel):
    id: Optional[int] = None
    description: Optional[str] = None
    a: Optional[str] = None
    b: Optional[str] = None
    c: Optional[str] = None
    d: Optional[str] = None
    answer: Optional[str] = None


@questions_router.get("/{question_id}")
async def user_detail(question_id: int):
    question = await Questions.get(question_id)
    if question:
        return {'question': question}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


# coin energy update
@questions_router.patch("/{question_id}")
async def user_patch(question_id: int, item: Annotated[QuestionPatch, Depends()]):
    question = await Questions.get(question_id)
    if question:
        update_data = {k: v for k, v in item.dict().items() if v is not None}
        if update_data:
            await Questions.update(question_id, **update_data)
            return {"ok": True, "data": update_data}
        else:
            return {"ok": False, "message": "Nothing to update"}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@questions_router.delete("/{question_id}")
async def user_delete(question_id: int):
    await Questions.delete(question_id)
    return {"ok": True, 'id': question_id}
