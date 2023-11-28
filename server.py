import os
import time
from typing import Union
from main import GameStateV2
from pydantic import BaseModel
import uuid

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from utils import ws_input

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

runs = {}

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    run_id = await ws_input("run id > ", websocket)
    if run_id not in runs:
        runs[run_id] = GameStateV2()
    game_state = runs[run_id]
    if game_state.started == True:
        await websocket.send_text(f"Run {run_id} already started! Cannot join.")
        return

    player_id = uuid.uuid4().hex
    print(f"----------- BEGINNING {player_id} on run {run_id}!")
    ret = await game_state.play(player_id, websocket)
    print(ret)

    # while True:
    #     data = await websocket.receive_text()
    #     await websocket.send_text(f"You said: {data}\r$ ")

