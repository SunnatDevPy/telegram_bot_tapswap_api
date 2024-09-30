from datetime import date

from fastapi import HTTPException

from db import Experience, Statusie, User
from db.models.model import UserAndExperience, Referral, Questions, ParamQuestion


async def generate_questions(user_id):
    questions = await Questions.get_all()
    param = await ParamQuestion.get_from_user_id(user_id)
    if date.day != param[0].updated_at.day:
        for i in range(0, 21):
            list_ = []

            list_.append()

    else:
        raise HTTPException(status_code=404, detail="Error generate questions")


async def hour_coin_check(user_id):
    experience: list['UserAndExperience'] = await UserAndExperience.get_from_user_id_experience(user_id)
    profit = 0
    if experience:
        for i in experience:
            profit += i.hour_coin
    return profit


async def get_detail_experience(data):
    list_ = []
    for i in data:
        experience = await Experience.get(i.experience_id)
        list_.append(
            {
                "id": i.id,
                "user_id": i.user_id,
                "hour_coin": i.hour_coin,
                "experience_id": i.experience_id,
                "degree": i.degree,
                "price": i.price,
                "photo": experience.photo,
                "name": experience.name,
                "description": experience.description,
                "created_at": i.created_at,
                "updated_at": i.updated_at
            }
        )
    return list_


async def friends_detail(user_id):
    list_ = {}
    friends_price = 0
    for i in await Referral.get_from_referral_id(user_id):
        user: User = await User.get(i.referred_user_id)
        status: Statusie = await Statusie.get(user.status_id)
        list_.update({"user_id": user.id, "values": {"status": status.name, "coin": user.coins,
                                                     "first_name": user.first_name,
                                                     "username": user.username,
                                                     "benefit": int((user.coins * 2.5) / 100)}})
        friends_price += int((user.coins * 2.5) / 100)
    return list_, friends_price


async def top_players_from_statu():
    list_ = {}
    for i in await Statusie.get_all():
        users: list['User'] = await User.get_from_type(i.id)
        s = []
        for son, j in enumerate(users):
            s.append({"user_id": j.id, "status": i.name, "coin": j.coins, "first_name": j.first_name,
                      "username": j.username})

        list_.update({f"{i.name}": s})
    return list_


async def top_players_from_statu_rank(user_id, status):
    users: list['User'] = await User.get_from_type_rank(status.id)
    for son, j in enumerate(users):
        if j.id == user_id:
            return {"status": status.name, "rank": son + 1}
