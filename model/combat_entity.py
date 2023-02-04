from typing import List
from collections import defaultdict
from termcolor import colored
from model.event import Event
from utils import energy_colors

class CombatEntity:
  def __init__(self, max_hp, name):
    self.max_hp = max_hp
    self.hp = max_hp
    self.name = name

    # current state
    self.conditions = defaultdict(lambda: 0)
    self.conditions["durable"] = None
    self.location = {"side": None, "position": None}
    self.events = []
    self.damage_taken_this_turn = 0

  @property
  def side(self):
    return self.location["side"]

  def position(self, encounter):
    if self in encounter.back:
      return encounter.back.index(self)
    elif self in encounter.front:
      return encounter.front.index(self)

  def render(self):
    condition_strs = []
    for k, v in self.conditions.items():
      if v:
        if k in energy_colors and v > 0:
          condition_strs.append(colored("*" * v, energy_colors[k]))
        else:
          condition_strs.append(f"{k} {v}")

    rendered_conditions = ", ".join(condition_strs)
    rendered_conditions = rendered_conditions.replace("burn", colored("burn", "red"))
    rendered_conditions = rendered_conditions.replace("block", colored("block", "blue"))
    rendered_conditions = rendered_conditions.replace("shield", colored("shield", "blue"))
    rendered_conditions = rendered_conditions.replace("armor", colored("armor", "cyan"))
    rendered_conditions = rendered_conditions.replace("durable", colored("durable", "cyan"))
    rendered_conditions = rendered_conditions.replace("regen", colored("regen", "green"))
    rendered_conditions = rendered_conditions.replace("poison", colored("poison", "green"))
    rendered_conditions = rendered_conditions.replace("empower", colored("empower", "yellow"))
    rendered_conditions = rendered_conditions.replace("searing", colored("searing", "yellow"))
    rendered_conditions = rendered_conditions.replace("stun", colored("stun", "blue"))
    rendered_conditions = rendered_conditions.replace("ward", colored("ward", "blue"))
    rendered_conditions = rendered_conditions.replace("sharp", colored("sharp", "red"))
    rendered_conditions = rendered_conditions.replace("prolific", colored("prolific", "yellow"))
    rendered_conditions = rendered_conditions.replace("inventive", colored("inventive", "cyan"))
    rendered_conditions = rendered_conditions.replace("dig", colored("dig", "yellow"))
    return f"{self.name}: {self.hp}/{self.max_hp}hp ({rendered_conditions})"

  # Manipulations

  def assign_damage(self, damage) -> int:
    if self.conditions["vulnerable"]:
      damage = int(damage * 1.5)
    damage_after_armor = damage - self.conditions["armor"]

    damage_to_block = min(damage_after_armor, self.conditions["block"])
    self.conditions["block"] -= damage_to_block
    damage_after_block = damage_after_armor - damage_to_block

    damage_to_shield = min(damage_after_block, self.conditions["shield"])
    self.conditions["shield"] -= damage_to_shield
    damage_after_shield = damage_after_block - damage_to_shield

    taken_damage = max(0, damage_after_shield)
    if (durable := self.conditions["durable"]) is not None:
      remaining_potential_damage = durable - self.damage_taken_this_turn
      taken_damage = min(taken_damage, remaining_potential_damage)
      print(f"potential: {remaining_potential_damage}, durable: {durable}, taken: {taken_damage}")

    self.hp -= taken_damage
    self.damage_taken_this_turn += taken_damage

    return taken_damage

  def heal(self, healing):
    self.hp = min(self.hp + healing, self.max_hp)

  # Game phase handlers and game logic

  def pop_events(self) -> List[Event]:
    events = self.events
    self.events = []
    return events

  def execute_conditions(self):
    self.heal(self.conditions["regen"])
    self.hp -= self.conditions["burn"]
    self.hp -= self.conditions["poison"]

  def end_round(self):
    # zero out
    self.conditions["block"] = 0
    self.damage_taken_this_turn = 0
    
    # tick down
    self.conditions["burn"] = max(self.conditions["burn"] - 1, 0)
    self.conditions["regen"] = max(self.conditions["regen"] - 1, 0)
    self.conditions["stun"] = max(self.conditions["stun"] - 1, 0)
    self.conditions["prolific"] = max(self.conditions["prolific"] - 1, 0)
    self.conditions["inventive"] = max(self.conditions["inventive"] - 1, 0)
    self.conditions["vulnerable"] = max(self.conditions["vulnerable"] - 1, 0)
    