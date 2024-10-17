import random
from typing import Annotated, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from db import User
from db.models.model import Questions, ParamQuestion
from fast_api.utils import get_questions_from_user


async def update_requests():
    questions = await Questions.get_all()
    users = await User.get_alls()
    for i in users:
        if len(questions) >= 5:
            randoms = random.sample(questions, 5)
        else:
            randoms = random.sample(questions, len(questions))
        for j in randoms:
            await ParamQuestion.create(question_id=j.id, answer=False, user_id=i.id)


async def delete_question():
    users = await User.get_alls()
    for i in users:
        await ParamQuestion.delete_question(i.id)


questions_router = APIRouter(prefix='/questions', tags=['Questions'])
scheduler = AsyncIOScheduler()
scheduler.add_job(delete_question, CronTrigger(hour=0, minute=0))
scheduler.add_job(update_requests, CronTrigger(hour=2, minute=0))


class QuestionAdd(BaseModel):
    description: str
    a: str
    b: str
    c: str
    d: str
    ball: int
    answer: str


class QuestionList(BaseModel):
    id: int
    description: str
    a: str
    b: str
    c: str
    d: str
    ball: int
    answer: str


class ParamQuestionList(BaseModel):
    id: int
    question_id: int
    user_id: int
    answer: bool


@questions_router.post("")
async def question_add(question_item: Annotated[QuestionAdd, Depends()]):
    question = await Questions.create(**question_item.dict())
    return {'ok': True, "id": question.id}


@questions_router.post("/{active}")
async def question_add_all_user(active: bool):
    if active == True:
        await update_requests()
        return {'ok': True, "yes": "accsess"}


@questions_router.post("/delete/param/{active}")
async def question_add_delete_user(active: bool):
    if active == True:
        await delete_question()
        return {'ok': True, "yes": "accsess"}


@questions_router.post("/answer/")
async def question_answer_add(user_id: int, question_id: int, answer: str):
    question = await ParamQuestion.get_question_from_user(user_id, question_id)
    user = await User.get(user_id)
    if question and user:
        quest = await Questions.get(question.question_id)
        if quest.answer == answer:
            await User.update(user_id, coins=user.coins + quest.ball)
            await ParamQuestion.update_question(user_id, question_id, answer=True)
            return {"answer": True, 'ball': quest.ball}
        else:
            return {"answer": False}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@questions_router.get('')
async def questions_list() -> list[QuestionList]:
    users = await Questions.get_all()
    return users


@questions_router.get('/param/')
async def param_questions_list() -> list[ParamQuestionList]:
    users = await ParamQuestion.get_all()
    return users


@questions_router.get('/{user_id}')
async def questions_from_user_list(user_id: int):
    users = await User.get(user_id)
    if users:
        return await get_questions_from_user(user_id)
    else:
        raise HTTPException(status_code=404, detail="Item not found")


class QuestionPatch(BaseModel):
    id: Optional[int] = None
    description: Optional[str] = None
    a: Optional[str] = None
    b: Optional[str] = None
    c: Optional[str] = None
    d: Optional[str] = None
    ball: Optional[int] = None
    answer: Optional[str] = None


@questions_router.get("/{question_id}")
async def question_detail(question_id: int):
    question = await Questions.get(question_id)
    if question:
        return {'question': question}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


# coin energy update
@questions_router.patch("/{question_id}")
async def question_patch(question_id: int, item: Annotated[QuestionPatch, Depends()]):
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


@questions_router.patch("/all/")
async def question_all_update(item: Annotated[QuestionPatch, Depends()]):
    question = await Questions.get_all()
    if question:
        update_data = {k: v for k, v in item.dict().items() if v is not None}
        if update_data:
            for i in question:
                await Questions.update(i.id, **update_data)
            return {"ok": True, "data": update_data}
        else:
            return {"ok": False, "message": "Nothing to update"}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@questions_router.delete("/{question_id}")
async def question_delete(question_id: int):
    await Questions.delete(question_id)
    return {"ok": True, 'id': question_id}
