from db import Experience
from db.models.model import UserAndExperience


async def hour_coin(user_id):
    experience: list[UserAndExperience] = await UserAndExperience.get_from_user_id(user_id)
    profit = 0
    if experience:
        for i in experience:
            exp: Experience = await Experience.get(i.experience_id)
            profit += exp.hour_coin
    else:
        return profit
