from fastapi import APIRouter
from requests import Request

referral_router = APIRouter(prefix='/referral', tags=['Referral'])

# @app.post("/register/")
# async def register_user(user_id: int):
#     referral_code = request.query_params.get("ref")
#
#     new_user = User(username=username)
#     db.add(new_user)
#     db.commit()
#
#     if referral_code:
#
#         referrer = db.query(User).filter_by(referral_code=referral_code).first()
#         if referrer:
#
#             referrer.points += 1
#             referral = Referral(referrer_id=referrer.id, referred_user_id=new_user.id)
#             db.add(referral)
#             db.commit()
#
#     return {"message": "User registered successfully"}