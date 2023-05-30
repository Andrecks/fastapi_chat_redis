
import json
import os
from fastapi import (FastAPI, Form, Request, Response, WebSocket,
                     WebSocketDisconnect, status)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, PackageLoader

from connection_manager import ConnectionManager

app = FastAPI()
templates = Jinja2Templates(directory="templates")
env = Environment(loader=PackageLoader("main", "templates"))
app.mount("/static", StaticFiles(directory="static"), name="static")


def to_json(value):
    import json
    return json.dumps(value)
env.filters['tojson'] = to_json

templates.env = env
manager = ConnectionManager()

@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse('login.html', {"request": request})

@app.post("/chat")
async def post_chat(response: Response, username: str = Form(...)):
    response = RedirectResponse(url=f'/chat', status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="nickname", value=username)  # Сохраняем имя пользователя в cookie
    return response

@app.get("/chat")
async def get_chat(request: Request):
    messages_bytes = manager.return_message_bytes()
    messages = []
    for message in messages_bytes:
        text = message.decode("utf-8")
        if text.split(',')[0].endswith('base64'):
            messages.append(f"img64:{text.split(':')[0]}:{text.split(',')[1]}")
        else:
            messages.append(text)

    members = manager.active_connections
    return templates.TemplateResponse('chat.html', {"request": request, "messages": messages, "members": members})

# image data:{username}:base64,{base64}
# message data: {userrname} : {message}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    nickname = websocket.query_params.get('nickname')  # Expects username as the first message
    await manager.connect(websocket, nickname)
    try:
        while True:

            data = await websocket.receive_text()
            # print(data)
            try:
                json_data = json.loads(data)
                if json_data.get('type') == 'image':
                    base64_image = json_data.get('base64')
                await manager.send_message(f"{nickname}:base64,{base64_image}")

            except:
                await manager.send_message(f"{nickname}: {data}")

    except WebSocketDisconnect:
        await manager.disconnect(websocket, nickname)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=os.getenv('FASTAPI_HOST'), port=8000)
