from db import Experience, Statusie, User
from db.models.model import UserAndExperience


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
