from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.security import HTTPBasic
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles

from db import database
from fast_api.events import event_router
from fast_api.experiences import experience
from fast_api.jwt_ import jwt_router
from fast_api.questions import scheduler, questions_router
from fast_api.referrals import referral_router
from fast_api.statusiec import status_router
from fast_api.user import user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.create_all()
    yield


app = FastAPI(lifespan=lifespan, debug=False, docs_url='/docs', redoc_url=None)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
async def startup_event():
    scheduler.start()


@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()


security = HTTPBasic()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8489", "https://stock-football-mini-app.vercel.app/"],
    # Список допустимых источников
    allow_credentials=True,  # Разрешить отправку кук (если нужно)
    allow_methods=["*"],  # Разрешить все методы (GET, POST, и т.д.)
    allow_headers=["*"],  # Разрешить все заголовки
)

app.include_router(user_router)
app.include_router(experience)
app.include_router(status_router)
app.include_router(referral_router)
app.include_router(questions_router)
app.include_router(event_router)
app.include_router(jwt_router)

# admin = Admin(
#     engine=database._engine,
#     title="Coin",
#     base_url='/admin',
#     auth_provider=UsernameAndPasswordProvider()
# )
#
#
# class UserModelView(ModelView):
#     exclude_fields_from_edit = ('created_at', 'updated_at')
#
#
# admin.add_view(UserModelView(User))
# admin.add_view(ModelView(Event))
# admin.add_view(ModelView(UserAndEvent))
# admin.add_view(ModelView(Referral))
# admin.add_view(ModelView(Experience))
# admin.add_view(ModelView(UserAndExperience))
# admin.add_view(ModelView(Statusie))
# admin.add_view(ModelView(Questions))
# admin.add_view(ModelView(ParamQuestion))
#
# admin.mount_to(app)
