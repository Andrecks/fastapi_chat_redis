from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Form, status, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import List
import redis
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

    async def connect(self, websocket: WebSocket):
        # Check if the WebSocket connection already exists
        username = websocket.query_params.get("username")
        members = self.get_chat_members()
        if username not in members:
            self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message):
        if message['type'] == 'text':
            text_message = f"{message['username']}: {message['data']}"
            r.lpush("chat", text_message)
            r.ltrim("chat", 0, 9)
            for connection in self.active_connections:
                await connection.send_text(text_message)
        elif message['type'] == 'image':
            image_message = f"{message['username']} sent an image"
            r.lpush("chat", image_message)
            r.ltrim("chat", 0, 9)
            for connection in self.active_connections:
                await connection.send_json(message)

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
    return templates.TemplateResponse('chat.html', {"request": request, "username": username, "messages": messages, "members": members})

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
            data = await websocket.receive_bytes()
            image = Image.open(io.BytesIO(data))
            # Process the image here (e.g., save to disk, perform image recognition, etc.)
            await manager.send_message(f"{username} sent an image")
    except WebSocketDisconnect:
        if websocket in manager.active_connections:
            manager.disconnect(websocket)