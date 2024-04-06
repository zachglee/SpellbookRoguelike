import asyncio
from pygame import mixer
import os

mixer.init()

def play_sound(filename, channel=0):
  full_path = f"assets/sounds/{filename}"
  if os.path.exists(full_path):
    mixer.Channel(channel).play(mixer.Sound(full_path))
  else:
    print(f"Sound file {full_path} not found")

async def ws_play_sound(filename, websocket, channel=0):
  await websocket.send_text(f"play_sound:{filename}")

def faf_play_sound(filename, websocket, channel=0):
  asyncio.create_task(ws_play_sound(filename, websocket))