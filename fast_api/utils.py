from db import Experience, Statusie, User
from db.models.model import Referral, Questions, ParamQuestion, Event, UserAndEvent


async def get_events(user_id):
    events = await UserAndEvent.get_from_user_id(user_id)
    list_ = []
    for i in events:
        event: Event = await Event.get(i.event_id)
        list_.append({
            "event_id": event.id,
            "user_id": i.user_id,
            "status": i.status,
            "name": event.name,
            "url": event.url,
            "coin": event.coin,
            "timer": event.timer,
            "photo": event.photo

        })
    return list_


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
                "next_coin": i.next_coin,
                "created_at": i.created_at,
                "updated_at": i.updated_at
            }
        )
    return list_


async def get_questions_from_user(user_id):
    list_ = []
    questions = await ParamQuestion.get_from_user_id(user_id)
    for i in questions:
        quest = await Questions.get(i.question_id)
        list_.append(
            {
                "id": quest.id,
                "user_id": i.user_id,
                "description": quest.description,
                "a": quest.a,
                "b": quest.b,
                "c": quest.c,
                "d": quest.d,
                "ball": quest.ball,
                "answer": quest.answer,
                "created_at": i.created_at,
                "updated_at": i.updated_at
            }
        )
    return list_


async def friends_detail(user_id):
    list_ = []
    friends_price = 0
    for i in await Referral.get_from_referral_id(user_id):
        user: User = await User.get(i.referred_user_id)
        status: Statusie = await Statusie.get(user.status_id)
        list_.append({"user_id": user.id, "status": status.name, "coins": user.coins, "username": user.username,
                      "benefit": int((user.coins * 1.5) / 100)})
        friends_price += int((user.coins * 1.5) / 100)
    return list_, friends_price


async def friends_coin(user_id):
    friends_price = 0
    for i in await Referral.get_from_referral_id(user_id):
        user: User = await User.get(i.referred_user_id)
        friends_price += int((user.coins * 2.5) / 100)
    return friends_price


async def top_players_from_statu():
    list_ = []
    for i in await Statusie.get_all():
        users = await User.get_from_type(i.id)
        list_.append({f"{i.name}": users})
    return list_


async def top_players_from_statu_rank(user_id, status):
    users: list['User'] = await User.get_from_type_rank(status.id)
    for son, j in enumerate(users):
        if j.id == user_id:
            return {"status": status.name, "rank": son + 1}
