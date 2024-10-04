from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from db import database
from fast_api.events import event_router
from fast_api.experiences import experience
from fast_api.questions import scheduler, questions_router
from fast_api.referrals import referral_router
from fast_api.statusiec import status_router
from fast_api.user import user_router


# Запускаем планировщик при старте приложения


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.create_all()
    yield


app = FastAPI(lifespan=lifespan, debug=True)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
async def startup_event():
    scheduler.start()


# Останавливаем планировщик при завершении работы приложения
@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Список допустимых источников
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


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("Hello! You are connected to the WebSocket server.")
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        print("Client disconnected")


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")
