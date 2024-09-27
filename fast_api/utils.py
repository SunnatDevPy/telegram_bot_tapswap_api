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


async def top_players_from_statu():
    list_ = {}
    for i in await Statusie.get_all():
        users: list['User'] = await User.get_from_type(i.id)
        s = []
        for son, j in enumerate(users):
            s.append({"user_id": j.id, "status": i.name, "coin": j.coins, "first_name": j.first_name,
                      "username": j.username})
            user = s[son]
        list_.update({f"{i.name}": s[:11], f"user_orin_{son}": 1})
    return list_
