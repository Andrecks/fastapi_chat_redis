from fastapi import WebSocket
from typing import List
import redis


r = redis.Redis(host='localhost', port=6379, db=0)
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.active_users: List[str] = []  # Store active usernames

    async def connect(self, websocket: WebSocket, username: str):
        self.active_connections.append(websocket)
        self.active_users.append(username)
        await self.send_user_list()

    async def disconnect(self, websocket: WebSocket, username: str):
        self.active_connections.remove(websocket)
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
        user_list = "user_list:" + ",".join(self.active_users)
        await self.send_message(user_list)

    def return_message_bytes(self):
        return r.lrange("chat", 0, -1)[::-1]