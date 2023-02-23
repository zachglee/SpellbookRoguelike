import random
from termcolor import colored

energy_colors = ["red", "blue", "gold", "green", "purple"]

# For rendering
energy_color_map = {
  "red": "red",
  "blue": "blue",
  "gold": "yellow",
  "green": "green",
  "purple": "magenta",
  "Red": "red",
  "Blue": "blue",
  "Gold": "yellow",
  "Green": "green",
  "Purple": "magenta",
}

# rendering

def colorize(s):
  for target_str, color in energy_color_map.items():
    s = s.replace(target_str, colored(target_str, color))
  return s

def numbered_list(l):
  return "\n".join(f"{i + 1} - {item.render()}" for i, item in enumerate(l))

# choosing

def choose_obj(choices, prompt):
  while True:
    try:
      choice = input(prompt)
      if choice == "done":
        return None
      return choices[int(choice) - 1]
    except (ValueError, TypeError, IndexError) as e:
      print(e)

def choose_idx(choices, prompt):
  while True:
    try:
      choice = input(prompt)
      if choice == "done":
        return None
      choice_obj = choices[int(choice) - 1]
      return int(choice) - 1
    except (ValueError, TypeError, IndexError) as e:
      print(e)

def choose_binary(prompt, choices=["y", "n"]):
  while True:
    try:
      choice = input(f"{prompt} ({choices[0]}/{choices[1]}) > ")
      if choice == choices[0]:
        return True
      elif choice == choices[1]:
        return False
    except (ValueError, TypeError, IndexError) as e:
      print(e)

def get_combat_entities(enc, target_string):
  if target_string == "p":
    return [enc.player]
  elif target_string == "a":
    return enc.front + enc.back
  elif target_string == "f":
    return enc.front
  elif target_string == "r":
    return [random.choice(enc.enemies)]
  elif target_string == "b":
    return enc.back
  elif target_string[0] == "b":
    target_pos = int(target_string[1])
    return [enc.back[target_pos - 1]]
  elif target_string[0] == "f":
    target_pos = int(target_string[1])
    return [enc.front[target_pos - 1]]