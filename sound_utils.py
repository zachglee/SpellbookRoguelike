from pygame import mixer
import os

mixer.init()

def play_sound(filename):
  full_path = f"assets/sounds/{filename}"
  if os.path.exists(full_path):
    mixer.music.load(full_path)
    mixer.music.play()
  else:
    print(f"Sound file {full_path} not found")