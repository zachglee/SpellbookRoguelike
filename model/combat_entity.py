from typing import List
from collections import defaultdict
from termcolor import colored
from model.event import Event
from utils import energy_color_map

class CombatEntity:
  def __init__(self, max_hp, name):
    self.max_hp = max_hp
    self.hp = max_hp
    self.name = name

    # current state
    self.conditions = defaultdict(lambda: 0)
    self.conditions["enduring"] = None
    self.conditions["durable"] = None
    self.location = {"side": None, "position": None}
    self.events = []
    self.damage_taken_this_turn = 0

  def side(self, encounter):
    if self in encounter.back: return "back"
    if self in encounter.front: return "front"
    return None
  
  def side_queue(self, encounter):
    if self in encounter.back: return encounter.back
    if self in encounter.front: return encounter.front
    return None

  def position(self, encounter):
    if self in encounter.back:
      return encounter.back.index(self)
    elif self in encounter.front:
      return encounter.front.index(self)
    
  def get_immediate(self, encounter):
    if pos := self.position(encounter) == 0:
      return encounter.player
    else:
      return self.side_queue(encounter)[pos - 1]

  def render(self):
    condition_strs = []
    for k, v in self.conditions.items():
      if v:
        if k in energy_color_map and v > 0:
          condition_strs.append(colored("*" * v, energy_color_map[k]))
        else:
          condition_strs.append(f"{k} {v}")

    rendered_conditions = ", ".join(condition_strs)
    rendered_conditions = rendered_conditions.replace("burn", colored("burn", "red"))
    rendered_conditions = rendered_conditions.replace("block", colored("block", "blue"))
    rendered_conditions = rendered_conditions.replace("shield", colored("shield", "blue"))
    rendered_conditions = rendered_conditions.replace("armor", colored("armor", "cyan"))
    rendered_conditions = rendered_conditions.replace("durable", colored("durable", "cyan"))
    rendered_conditions = rendered_conditions.replace("enduring", colored("enduring", "magenta"))
    rendered_conditions = rendered_conditions.replace("regen", colored("regen", "green"))
    rendered_conditions = rendered_conditions.replace("poison", colored("poison", "magenta"))
    rendered_conditions = rendered_conditions.replace("empower", colored("empower", "yellow"))
    rendered_conditions = rendered_conditions.replace("searing", colored("searing", "yellow"))
    rendered_conditions = rendered_conditions.replace("stun", colored("stun", "blue"))
    rendered_conditions = rendered_conditions.replace("ward", colored("ward", "blue"))
    rendered_conditions = rendered_conditions.replace("retaliate", colored("retaliate", "magenta"))
    rendered_conditions = rendered_conditions.replace("sharp", colored("sharp", "red"))
    rendered_conditions = rendered_conditions.replace("vulnerable", colored("vulnerable", "red"))
    rendered_conditions = rendered_conditions.replace("prolific", colored("prolific", "yellow"))
    rendered_conditions = rendered_conditions.replace("inventive", colored("inventive", "cyan"))
    rendered_conditions = rendered_conditions.replace("dig", colored("dig", "yellow"))
    return f"{self.name}: {self.hp}/{self.max_hp}hp ({rendered_conditions})"

  # Manipulations

  def clear_conditions(self):
    self.conditions = defaultdict(lambda: 0)
    self.conditions["durable"] = None
    self.conditions["enduring"] = None

  def attack(self, target, damage, lifesteal=False):
    damage_to_kill = target.conditions["block"] + target.conditions["shield"] + target.conditions["armor"] + target.hp - self.conditions["sharp"]
    empower_to_spend = max(0, damage_to_kill - damage)
    spent_empower = min(self.conditions["empower"], empower_to_spend)
    self.conditions["empower"] -= spent_empower
    final_damage = damage + spent_empower + self.conditions["sharp"]
    self.assign_damage(target.conditions["retaliate"])
    damage_dealt = target.assign_damage(final_damage)
    if lifesteal:
      self.heal(damage_dealt)
    return damage_dealt

  def assign_damage(self, damage) -> int:
    if self.conditions["vulnerable"]:
      damage = int(damage * 1.5)
    damage_after_armor = max(0, damage - self.conditions["armor"])

    damage_to_block = min(damage_after_armor, self.conditions["block"])
    self.conditions["block"] -= damage_to_block
    damage_after_block = damage_after_armor - damage_to_block

    damage_to_shield = min(damage_after_block, self.conditions["shield"])
    self.conditions["shield"] -= damage_to_shield
    damage_after_shield = damage_after_block - damage_to_shield

    taken_damage = max(0, damage_after_shield)
    if (durable := self.conditions["durable"]) is not None:
      taken_damage = min(taken_damage, durable)
    if (enduring := self.conditions["enduring"]) is not None:
      remaining_potential_damage = enduring - self.damage_taken_this_turn
      taken_damage = min(taken_damage, remaining_potential_damage)

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
    self.hp -= self.conditions["burn"]
    self.hp -= self.conditions["poison"]
    self.heal(self.conditions["regen"])

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
    self.conditions["dig"] = max(self.conditions["dig"] - 1, 0)
    