from typing import List
from collections import defaultdict
from termcolor import colored
from model.event import Event
from utils import energy_color_map
from sound_utils import play_sound

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
    self.damage_survived_this_turn = 0
    self.dead = False

  def is_player(self):
    return self.__class__.__name__ == "Player"

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

  def get_target_string(self, encounter) -> str:
    if self in encounter.back:
      return f"b{encounter.back.index(self)+1}"
    elif self in encounter.front:
      return f"f{encounter.front.index(self)+1}"
    else:
      return ""

  def get_immediate(self, encounter):
    pos = self.position(encounter)
    print(f"Get immediate: my position is {pos}")
    if pos == 0:
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
    rendered_conditions = rendered_conditions.replace("charge", colored("charge", "yellow"))
    rendered_conditions = rendered_conditions.replace("stun", colored("stun", "blue"))
    rendered_conditions = rendered_conditions.replace("ward", colored("ward", "blue"))
    rendered_conditions = rendered_conditions.replace("retaliate", colored("retaliate", "magenta"))
    rendered_conditions = rendered_conditions.replace("sharp", colored("sharp", "red"))
    rendered_conditions = rendered_conditions.replace("vulnerable", colored("vulnerable", "red"))
    rendered_conditions = rendered_conditions.replace("prolific", colored("prolific", "yellow"))
    rendered_conditions = rendered_conditions.replace("slow", colored("slow", "magenta"))
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
    target_enduring = target.conditions["enduring"] or 1000
    empower_to_spend = max(0, min(damage_to_kill, target_enduring) - damage)
    spent_empower = min(self.conditions["empower"], empower_to_spend)
    self.conditions["empower"] -= spent_empower
    multiplier = 1.5 if target.conditions["vulnerable"] else 1
    final_damage = (damage + spent_empower + self.conditions["sharp"]) * multiplier
    self.assign_damage(target.conditions["retaliate"])
    damage_dealt = target.assign_damage(final_damage)
    if lifesteal:
      self.heal(damage_dealt)
    print(f"{self.name} attacks {target.name} for {damage_dealt} damage!")
    self.events.append(Event(["attack"], metadata={"damage_assigned": final_damage, "damage_dealt": damage_dealt, "target": target}))
    target.damage_survived_this_turn += final_damage
    print(f"--------- {target.name} Damage survived: {target.damage_survived_this_turn}")

    # play the proper sound
    if damage_dealt == 0:
      if damage <= 5:
        play_sound("light-attack-blocked.mp3", channel=1)
      else:
        play_sound("heavy-attack-blocked.mp3", channel=1)
    elif damage_dealt <= 5:
      play_sound("light-attack.wav", channel=1)
    elif damage_dealt <= 12:
      play_sound("medium-attack.mp3", channel=1)
    else:
      play_sound("heavy-attack.mp3", channel=1)

    return damage_dealt

  def assign_damage(self, damage) -> int:
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

    self.suffer(taken_damage)

    return taken_damage

  def suffer(self, damage):
    self.hp -= damage
    self.damage_taken_this_turn += damage
    if damage > 0:
      self.events.append(Event(["lose_hp"],
                               metadata={
                                 "damage": damage,
                                 "target": self
                               }))

  def heal(self, healing):
    self.hp = min(self.hp + healing, self.max_hp)
    input(f"{self.name} heals {healing} hp!")

  # Game phase handlers and game logic

  def pop_events(self) -> List[Event]:
    events = self.events
    self.events = []
    return events

  def execute_conditions(self):
    self.suffer(self.conditions["burn"])
    self.suffer(self.conditions["poison"])
    if self.conditions["regen"] > 0: self.heal(self.conditions["regen"])

  def end_round(self):
    self.damage_survived_this_turn = 0
    self.damage_taken_this_turn = 0
    # zero out
    self.conditions["block"] = 0
    
    # tick down
    self.conditions["burn"] = max(self.conditions["burn"] - 1, 0)
    self.conditions["regen"] = max(self.conditions["regen"] - 1, 0)
    self.conditions["stun"] = max(self.conditions["stun"] - 1, 0)
    self.conditions["prolific"] = max(self.conditions["prolific"] - 1, 0)
    self.conditions["slow"] = max(self.conditions["slow"] - 1, 0)
    self.conditions["inventive"] = max(self.conditions["inventive"] - 1, 0)
    self.conditions["vulnerable"] = max(self.conditions["vulnerable"] - 1, 0)
    self.conditions["dig"] = max(self.conditions["dig"] - 1, 0)
    