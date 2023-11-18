from typing import Union
from pydantic import BaseModel

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

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


@app.get("/")
async def get():
    return HTMLResponse(html)


async def websocket_input(prompt, websocket: WebSocket):
    await websocket.send_text(f"{prompt}")
    data = await websocket.receive_text()
    return data

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        new_or_existing = await websocket_input("New or existing character?:", websocket)
        if new_or_existing == "new":
            await websocket.send_text(f"You chose new.")
        elif new_or_existing == "existing":
            await websocket.send_text(f"You chose existing.")
        else:
            await websocket.send_text(f"Invalid choice: {new_or_existing}")
        # data = await websocket.receive_text()
        # await websocket.send_text(f"Message text was: {data}")