import random
from termcolor import colored
import re

energy_colors = ["red", "blue", "gold", "green", "purple"]
energy_pip_symbol = "●"

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

def without_ansi_escapes(s):
  ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
  return ansi_escape.sub('', s)

def colorize(s):
  for target_str, color in energy_color_map.items():
    s = s.replace(target_str, colored(target_str, color))
  return s

def numbered_list(l) -> str:
  return "\n".join(f"{i + 1} - {item.render()}" for i, item in enumerate(l))

def aligned_line(line_items, column_width=25):
  padded_line_items = []
  for line in line_items:
    true_length = len(without_ansi_escapes(line))
    padding_amount = column_width - true_length
    if padding_amount < 0:
      padded_line = line[:padding_amount - 4] + "... "
    else:
      padded_line = line + (" " * (column_width - true_length))
    padded_line_items.append(padded_line)
  return "".join(padded_line_items)

# choosing

def choose_str(choices, prompt):
  while True:
    try:
      choice = input(prompt)
      if choice == "done":
        return None
      if choice in choices:
        return choice
      print("Invalid choice...")
    except (ValueError, TypeError, IndexError) as e:
      print(e)

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

def choose_binary(prompt, choices=["y", "n"]) -> bool:
  while True:
    try:
      choice = input(f"{prompt} ({choices[0]}/{choices[1]}) > ")
      if choice == choices[0]:
        return True
      elif choice == choices[1]:
        return False
    except (ValueError, TypeError, IndexError) as e:
      print(e)

def get_spell(enc, target_string):
  if target_string == "r":
    spell_idx = random.choice(range(len(enc.player.spellbook.current_page.spells)))
  elif target_string in ["l", "last"]:
    return enc.last_spell_cast
  elif target_string == "_":
    input_target_string = input(colored("Choose a spell > ", "cyan"))
    return get_spell(enc, input_target_string)
  else:
    spell_idx = int(target_string) - 1
  target = enc.player.spellbook.current_page.spells[spell_idx]
  return target

TARGET_RESTRICTION_PREDICATES = {
  "damaged": lambda ce, enc: ce.hp < ce.max_hp,
  "entered": lambda ce, enc: ce.spawned_turn == enc.turn
}

def get_combat_entities(enc, target_string):
  if target_string == "p":
    return [enc.player]
  elif target_string == "a":
    return enc.front + enc.back
  elif target_string == "i":
    return [enc.player.get_immediate(enc)]
  elif target_string == "iside":
    return enc.faced_enemy_queue
  elif target_string == "bi":
    return [enc.unfaced_enemy_queue[0]]
  elif target_string[0] == "i" and (n := target_string[1:].isnumeric()):
    return [enc.player.get_immediate(enc, offset=n-1)]
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
  elif target_string == "distant":
    return [enc.faced_enemy_queue[-1]]
  elif target_string[0] == "_":
    restriction = target_string[1:]
    is_valid = TARGET_RESTRICTION_PREDICATES.get(restriction)

    input_target_string = input(colored("Choose a target > ", "green"))
    targets = get_combat_entities(enc, input_target_string)
    while is_valid is not None and not is_valid(targets[0], enc):
      print(colored("Invalid target!", "red"))
      input_target_string = input(colored("Choose a target > ", "green"))
      target = get_combat_entities(enc, input_target_string)
    return targets
      
  
def command_reference():
  help_string = """
  UI Commands:
   - help: Display this message
   - map: Display the map
   - inventory,inv: Display your inventory
   - intent,int: Toggle display of enemy intents
  Targeting:
    In many commands, you will see text like this: <target>. This is to be filled in by you with a 'target string'
    that determines which entity you wish to target with this effect. 
    - To target yourself, use `p`.
    - To target an enemy on the front side, use `f<n>` where `<n>` is replaced by a number. 1 is the first enemy on the front side, 2 is the second, etc.
    - To taget an enemy on the back side, use `b<n>`, see above for the meaning of `<n>`.
    - To target all enemies on the front side, use `f`
    - To target all enemies on the back side, use `b`
    - To target all enemies, use `a`
    - To target a random enemy, use `r`
    - To target the immediate enemy (first enemy on the side you are facing), use `i`
  Combat Commands: (text like <this> is placeholder, to be filled in by you)
   - die: lose the game. Currently, you must manually use this command when you reach 0 hp.
   - damage <target> <amount>: deal damage to given target.
   - suffer <target> <amount>: same as damage, but bypasses all damage modifiers, like block, sharp, etc.
   - heal <target> <amount>: heals the target for the specified amount of hp
   - <condition_name> <target> <amount>: applies `amount` stacks of the condition to the target.
   - face: turns your character to face the opposite side
   - face?: same as `face`, but doesn't cost you a time
   - page: flips to the next page
   - page?: same as `page` but doesn't cost you a time (useful if you just want to check what's on the other page)
   - use <n>: uses the n'th item in your inventory
   - cast <n>: casts the n'th spell on this page
   - time <n>: removes n units of time. If you want to get time back use negative numbers.
  """
  input(help_string)

def help_reference(subject):
  if subject == "burn":
    help_text = ("Burn is a condition. At the end of every turn, an entity with burn"
                "suffers damage equal to its burn and its burn decreases by 1.")
  elif subject == "poison":
    help_text = ("Poison is a condition. At the end of every turn, an entity with poison"
                "suffers damage equal to its poison.")
  elif subject == "stun":
    help_text = ("Stun is a condition. Instead of acting, a stunned enemy decreases its stun by 1.")
  elif subject == "searing":
    help_text = ("Searing is a condition. At the end of every turn, an entity with searing"
                "deals damage equal to its searing to the entity it's immediately facing.")
  elif subject == "sharp":
    help_text = ("Sharp is a condition. All attacks made by an entity with sharp "
                 "deal extra damage equal to the amount of sharp it has.")
  elif subject == "empower":
    help_text = ("Empower is a condition. The next attack an empowered entity makes consumes "
                 "its empower and deals that much extra damage. If there is more than enough empower "
                 "to kill the target entity, only the amount of empower needed to kill the entity is consumed.")
  elif subject == "armor":
    help_text = ("Armor is a condition. An entity with armor takes that much less damage from attacks.")
  elif subject == "block":
    help_text = ("Block is a condition. Damage is dealt to an entity's block instead of its shield or hp. "
                 "One point of damage removes one point of block. "
                 "All block is removed at the end of the turn.")
  elif subject == "shield":
    help_text = ("Shield is a condition. It operates like block but does not disappear at the end of the turn. "
                 "Damage is taken first to block, then to shield, then to hp.")
  elif subject == "regen":
    help_text = ("Regen is a condition. At the end of every turn, an entity with regen "
                  "gains that much hp and reduces its regen by 1.")
  elif subject == "ward":
    help_text = ("Ward is a condition. It applies only to players. "
                 "When an enemy would spawn, it does not and the player's ward is reduced by 1.")
  elif subject == "prolific":
    help_text = ("Prolific is a condition. It applies only to players. While a player has any prolific, "
                 "they gain an extra 4 time at the start of the turn. Reduces by 1 at the end of every turn.")
  elif subject == "inventive":
    help_text = ("Inventive is a condition. It applies only to players. While a player has any inventive, "
                 "they may spend energy as if it were any color. Reduces by 1 at the end of every turn.")
  elif subject == "suffer":
    help_text = ("Suffering damage is different from taking damage in that it cannot be mitigated and is "
                 "always taken directly to hp.")
  elif subject == "retaliate":
    help_text = ("Retaliate is a condition. Whenever an entity with retaliate is attacked, its attacker "
                 "suffers damage equal to its retaliate.")
  elif subject == "slow":
    help_text = ("Slow is a condition. A player with slow loses 1 time at the start of every turn. "
                 "Reduces by 1 every turn.")
  elif subject == "dig":
    help_text = ("Dig is a condition. The spells of a player with dig may go to -1 charge. "
                 "Reduces by 1 every turn.")
  elif subject == "enduring":
    help_text = ("Enduring is a condition. An entity with x enduring may lose up to, but no more than, x hp in a turn.")
  elif subject == "vulnerable":
    help_text = ("Vulnerable is a condition. An entity with vulnerable takes 50% more damage from all attacks.")
  elif subject == "durable":
    help_text = ("Durable is a condition. An entity with x durable cannot lose more than x hp in a single attack.")
  # TODO: encase, undying, evade
  else:
    help_text = (f"Sorry, there is no help entry for '{subject}'")
  input(help_text)
  
