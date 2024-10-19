from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.security import HTTPBasic
from sqladmin import Admin
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles

from db import database
from fast_api.auth_py import AuthBackend
from fast_api.events import event_router
from fast_api.experiences import experience
from fast_api.jwt_ import jwt_router
from fast_api.questions import questions_router
from fast_api.referrals import referral_router
from fast_api.statusiec import status_router
from fast_api.user import user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.create_all()
    yield


app = FastAPI(lifespan=lifespan, debug=False, docs_url='/hellos', redoc_url=None)

app.mount("/static", StaticFiles(directory="static"), name="static")
admin = Admin(app, database._engine, authentication_backend=AuthBackend("stockminiapp"))
app.add_middleware(SessionMiddleware, secret_key="stockminiapp")


# admin.add_view(ProductAdmin)
# admin.add_view(CategoryAdmin)

@app.on_event("startup")
async def startup_event():
    pass


@app.on_event("shutdown")
async def shutdown_event():
    pass


security = HTTPBasic()
# football-stock.uz
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8489", "https://football-stock.uz"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(experience)
app.include_router(status_router)
app.include_router(referral_router)
app.include_router(questions_router)
app.include_router(event_router)
app.include_router(jwt_router)
