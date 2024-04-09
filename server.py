
from main import GameStateV2
import uuid

from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from utils import ws_input, ws_print
from sound_utils import ws_play_sound

app = FastAPI()

app.mount("/sounds", StaticFiles(directory="assets/sounds"), name="sounds")

@app.get("/game")
async def read_index():
    return FileResponse('index.html')

runs = {}
app.state.player_id_counter = 1

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

    player_id = "p" + str(app.state.player_id_counter)
    app.state.player_id_counter += 1

    print(f"----------- BEGINNING {player_id} on run {run_id}!")
    ret = await game_state.play(player_id, websocket)
    print(ret)

