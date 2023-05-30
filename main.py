from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Form, status, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import List
import redis
import json
import base64
import io
from PIL import Image

# Создание объекта Redis
r = redis.Redis(host='localhost', port=6379, db=0)

app = FastAPI()

templates = Jinja2Templates(directory="templates")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        print(self.active_connections)
    async def connect(self, websocket: WebSocket):
        # Check if the WebSocket connection already exists
        if websocket not in self.active_connections:
            self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str):
        # Сохранение сообщения в Redis
        r.lpush("chat", message)
        # Обрезание списка до последних 10 сообщений
        r.ltrim("chat", 0, 9)
        
        # Отправка сообщений всем подключениям
        for connection in self.active_connections:
            await connection.send_text(message)

    def get_chat_members(self):
        return [connection.query_params.get("username") for connection in self.active_connections]


manager = ConnectionManager()

@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse('login.html', {"request": request})

@app.post("/chat")
async def post_chat(response: Response, username: str = Form(...)):
    response = RedirectResponse(url=f'/chat', status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="username", value=username)  # Сохраняем имя пользователя в cookie
    return response

@app.get("/chat")
async def get_chat(request: Request):
    # Извлечение имени пользовате ля из cookie
    username = request.cookies.get("username")

    # Извлечение последних 10 сообщений из Redis
    messages_bytes = r.lrange("chat", 0, -1)[::-1]
    messages = [message.decode("utf-8") for message in messages_bytes]
    members = manager.get_chat_members()
    return templates.TemplateResponse('chat.html', {"request": request, "messages": messages, "members": members})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    username = websocket.query_params.get('username')  # Expects username as the first message
    if username:
        await manager.connect(websocket)
    else:
        return {"error": "Username is required"}
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            if message['type'] == 'image':
                image_data = message['data']
                # Process the image data here (e.g., save to disk, perform image recognition, etc.)
                await manager.send_message(f"{username} sent an image")
            else:
                await manager.send_message(f"{username}: {data}")
    except WebSocketDisconnect:
        if websocket in manager.active_connections:
            manager.disconnect(websocket)