from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from fast_api.experiences import experience
from fast_api.user import user_router

from db import database


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.create_all()
    yield


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

origins = [
    "http://localhost",
    "http://localhost:8000",
    "https://example.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Список допустимых источников
    allow_credentials=True,  # Разрешить отправку кук (если нужно)
    allow_methods=["*"],  # Разрешить все методы (GET, POST, и т.д.)
    allow_headers=["*"],  # Разрешить все заголовки
)

app.include_router(user_router)
app.include_router(experience)
