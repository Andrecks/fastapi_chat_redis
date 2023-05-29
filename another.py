from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Form, status, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import List
import redis

# Create Redis connection
r = redis.Redis(host='localhost', port=6379, db=0)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.active_users: List[str] = []  # Store active usernames

    async def connect(self, websocket: WebSocket, username: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.active_users.append(username)
        await self.send_user_list()

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        username = self.get_username(websocket)
        if username:
            self.active_users.remove(username)
            await self.send_user_list()

    async def send_message(self, message: str):
        # Save the message to Redis
        r.lpush("chat", message)
        r.ltrim("chat", 0, 9)  # Trim the list to store only the last 10 messages

        # Send the message to all connected clients
        for connection in self.active_connections:
            await connection.send_text(message)

    async def send_user_list(self):
        # Prepare the user list message
        user_list = ",".join(self.active_users)
        message = f"/users,{user_list}"

        # Send the user list to all connected clients
        for connection in self.active_connections:
            await connection.send_text(message)

    def get_username(self, websocket: WebSocket) -> str:
        # Retrieve the username associated with the websocket
        for i, conn in enumerate(self.active_connections):
            if conn == websocket:
                return self.active_users[i]
        return ""

manager = ConnectionManager()

# @app.post("/")
# async def post_chat(response: Response, username: str = Form(...)):
#     response = RedirectResponse(url="/chat", status_code=status.HTTP_303_SEE_OTHER)
#     response.set_cookie(key="username", value=username)
#     return response

@app.get("/chat")
async def get_chat(request: Request):
    username = request.cookies.get("username")
    messages_bytes = r.lrange("chat", 0, -1)[::-1]
    messages = [message.decode("utf-8") for message in messages_bytes]
    return templates.TemplateResponse('chat.html', {"request": request, "username": username, "messages": messages})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    username = websocket.query_params.get('username')
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"{username}: {data}")