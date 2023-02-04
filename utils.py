from termcolor import colored

# For rendering
energy_colors = {
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

def colorize(s):
  for target_str, color in energy_colors.items():
    s = s.replace(target_str, colored(target_str, color))
  return s

