from pygame import mixer
import os

mixer.init()

def play_sound(filename, channel=0):
  full_path = f"assets/sounds/{filename}"
  if os.path.exists(full_path):
    # mixer.music.load(full_path)
    # mixer.music.play()
    mixer.Channel(channel).play(mixer.Sound(full_path))
  else:
    print(f"Sound file {full_path} not found")