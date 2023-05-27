from pygame import mixer

mixer.init()

def play_sound(filename):
  mixer.music.load(f"assets/sounds/{filename}")
  mixer.music.play()