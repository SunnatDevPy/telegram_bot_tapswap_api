import random

from db import Questions, ParamQuestion


async def update_question(user_id):
    questions = await Questions.get_all()
    if len(questions) >= 5:
        randoms = random.sample(questions, 5)
    else:
        randoms = random.sample(questions, len(questions))
    for j in randoms:
        await ParamQuestion.create(question_id=j.id, answer=False, user_id=user_id)
