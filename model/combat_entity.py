import asyncio
from typing import Any, List
from pydantic import validator, BaseModel
import math
from collections import defaultdict
from termcolor import colored
from model.event import Event
from utils import energy_color_map, energy_pip_symbol, faf_print, ws_input
from sound_utils import faf_play_sound, play_sound

class CombatEntity(BaseModel):
  max_hp: int
  hp: int
  name: str

  # current state
  conditions: Any = defaultdict(lambda: 0)
  location: dict = {"side": None, "position": None}
  events: List[Event] = []
  dead: bool = False
  resurrected: bool = False
  event_triggers: list = []

  # combat bookkeeping
  damage_taken_this_turn: int = 0
  damage_survived_this_turn: int = 0
  face_count: int = 0 # relevant for player only
  spawned_turn: int = None # relevant for enemies only

  class Config:
    arbitrary_types_allowed = True

  @validator("conditions", always=True)
  def none_conditions(cls, data, values):
    if data["enduring"] == 0:
      data["enduring"] = None
    if data["durable"] == 0:
      data["durable"] = None
    return data

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
          condition_strs.append(colored(energy_pip_symbol * v, energy_color_map[k]))
        else:
          condition_strs.append(f"{k} {v}")

    rendered_conditions = ", ".join(condition_strs)
    rendered_conditions = rendered_conditions.replace("burn", colored("burn", "red"))
    rendered_conditions = rendered_conditions.replace("block", colored("block", "blue"))
    rendered_conditions = rendered_conditions.replace("shield", colored("shield", "blue"))
    rendered_conditions = rendered_conditions.replace("encase", colored("encase", "cyan"))
    rendered_conditions = rendered_conditions.replace("armor", colored("armor", "cyan"))
    rendered_conditions = rendered_conditions.replace("durable", colored("durable", "cyan"))
    rendered_conditions = rendered_conditions.replace("enduring", colored("enduring", "magenta"))
    rendered_conditions = rendered_conditions.replace("regen", colored("regen", "green"))
    rendered_conditions = rendered_conditions.replace("poison", colored("poison", "magenta"))
    rendered_conditions = rendered_conditions.replace("empower", colored("empower", "yellow"))
    rendered_conditions = rendered_conditions.replace("searing", colored("searing", "yellow"))
    rendered_conditions = rendered_conditions.replace("evade", colored("evade", "cyan"))
    rendered_conditions = rendered_conditions.replace("charge", colored("charge", "yellow"))
    rendered_conditions = rendered_conditions.replace("stun", colored("stun", "blue"))
    rendered_conditions = rendered_conditions.replace("ward", colored("ward", "blue"))
    rendered_conditions = rendered_conditions.replace("retaliate", colored("retaliate", "magenta"))
    rendered_conditions = rendered_conditions.replace("sharp", colored("sharp", "red"))
    rendered_conditions = rendered_conditions.replace("vulnerable", colored("vulnerable", "red"))
    rendered_conditions = rendered_conditions.replace("doom", colored("doom", "magenta"))
    rendered_conditions = rendered_conditions.replace("prolific", colored("prolific", "yellow"))
    rendered_conditions = rendered_conditions.replace("slow", colored("slow", "magenta"))
    rendered_conditions = rendered_conditions.replace("inventive", colored("inventive", "cyan"))
    rendered_conditions = rendered_conditions.replace("dig", colored("dig", "yellow"))
    rendered_conditions = rendered_conditions.replace("undying", colored("undying", "magenta"))
    return f"{self.name}: {self.hp}/{self.max_hp}hp ({rendered_conditions})"

  # Manipulations

  def clear_conditions(self):
    self.conditions = defaultdict(lambda: 0)
    self.conditions["durable"] = None
    self.conditions["enduring"] = None

  def clear_good_conditions(self):
    self.conditions["regen"] = 0
    self.conditions["empower"] = 0
    self.conditions["searing"] = 0
    self.conditions["charge"] = 0
    self.conditions["ward"] = 0
    self.conditions["sharp"] = 0
    self.conditions["armor"] = 0
    self.conditions["block"] = 0
    self.conditions["shield"] = 0
    self.conditions["encase"] = 0
    self.conditions["prolific"] = 0
    self.conditions["inventive"] = 0
    self.conditions["dig"] = 0
    self.conditions["undying"] = 0
    self.conditions["retaliate"] = 0
    self.conditions["durable"] = None
    self.conditions["enduring"] = None

  def attack(self, target, damage, lifesteal=False):
    if target is None:
      faf_print(f"{self.name} attacks nothing.", self.websocket)
      return 0

    max_useful_damage = (target.conditions["block"] +
                      target.conditions["shield"] +
                      target.conditions["armor"] +
                      self.conditions["encase"] +
                      target.conditions["encase"] +
                      min(target.hp, target.conditions["enduring"] or 1000, target.conditions["durable"] or 1000) -
                      self.conditions["sharp"])
    target_enduring = target.conditions["enduring"] or 1000
    empower_to_spend = max(0, min(max_useful_damage, target_enduring) - damage)
    spent_empower = min(self.conditions["empower"], empower_to_spend)
    self.conditions["empower"] -= spent_empower
    multiplier = 1.5 if target.conditions["vulnerable"] else 1
    final_damage = math.ceil((damage + spent_empower + self.conditions["sharp"]) * multiplier)
    final_damage = max(0, final_damage) # make sure it can't be negative

    # first break through encase if there is any
    if self.conditions["encase"] > 0:
      damage_to_encase = min(self.conditions["encase"], damage)
      self.conditions["encase"] -= damage_to_encase
      final_damage -= damage_to_encase
      faf_print(f"{self.name} attacks it encasement for {damage_to_encase} damage!", self.websocket)
    
    if target.conditions["evade"] > 0:
      faf_play_sound("attack-evaded.mp3", self.websocket, channel=1)
      faf_print(f"{self.name} attacks {target.name} but they evade!", self.websocket)
      target.conditions["evade"] -= 1
      final_damage = 0

    potential_lifesteal = target.hp
    self.assign_damage(target.conditions["retaliate"], source=target)
    damage_dealt = target.assign_damage(final_damage, source=self, increment_damage_survived=False)
    if lifesteal:
      self.heal(min(damage_dealt, potential_lifesteal))
    # NOTE: this is a little too noisy
    # faf_print(f"{self.name} attacks {target.name} for {damage_dealt} damage!", self.websocket)
    self.events.append(Event(["attack"], metadata={"damage_assigned": final_damage, "damage_dealt": damage_dealt, "target": target, "attacker": self}))
    target.damage_survived_this_turn += final_damage

    # play the proper sound
    if damage_dealt == 0:
      if damage <= 5:
        faf_play_sound("light-attack-blocked.mp3", self.websocket, channel=1)
      else:
        faf_play_sound("heavy-attack-blocked.mp3", self.websocket, channel=1)
    elif damage_dealt <= 5:
      faf_play_sound("light-attack.wav", self.websocket, channel=1)
    elif damage_dealt <= 12:
      faf_play_sound("medium-attack.mp3", self.websocket, channel=1)
    else:
      faf_play_sound("heavy-attack.mp3", self.websocket, channel=1)

    return damage_dealt

  def assign_damage(self, damage, source=None, increment_damage_survived=True) -> int:
    damage_to_encase = min(damage, self.conditions["encase"])
    self.conditions["encase"] -= damage_to_encase
    damage_after_encase = damage - damage_to_encase

    damage_after_armor = max(0, damage_after_encase - self.conditions["armor"])

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

    self.suffer(taken_damage, increment_damage_survived=increment_damage_survived)

    # create events for triggers
    if ((damage_to_block > 0 and self.conditions["block"] == 0) or
       (damage_to_shield > 0 and self.conditions["shield"] == 0) or
       (damage_to_encase > 0 and self.conditions["encase"] == 0)):
      self.events.append(Event(["defense_break"], metadata={"target": self, "source": source}))

    return taken_damage

  def suffer(self, damage, increment_damage_survived=True):
    self.hp -= damage
    self.damage_taken_this_turn += damage
    if increment_damage_survived:
      self.damage_survived_this_turn += damage
    if damage > 0:
      self.events.append(Event(["lose_hp"],
                               metadata={
                                 "damage": damage,
                                 "target": self
                               }))

  def heal(self, healing):
    self.hp = min(self.hp + healing, self.max_hp)
    if self.websocket:
        # asyncio.create_task(ws_input(f"{self.name} heals {healing} hp!", self.websocket))
        faf_print(f"{self.name} heals {healing} hp!", self.websocket)

  # Game phase handlers and game logic

  def pop_events(self) -> List[Event]:
    events = self.events
    self.events = []
    return events

  def execute_conditions(self):
    self.suffer(self.conditions["burn"])
    self.conditions["burn"] = max(self.conditions["burn"] - 1, 0)

    self.suffer(self.conditions["poison"])
    if (doom := self.conditions["doom"]) >= self.hp:
      self.suffer(doom)
    if self.conditions["regen"] > 0:
      self.heal(self.conditions["regen"])
      self.conditions["regen"] -= 1
    
    self.conditions["shield"] = max(self.conditions["shield"], 0)

  def end_round(self):
    self.damage_survived_this_turn = 0
    self.damage_taken_this_turn = 0
    self.face_count = 0

    # Tick down event trigger durations
    for event_trigger in self.event_triggers:
      if event_trigger.turns_remaining != None:
        event_trigger.turns_remaining -= 1
    self.event_triggers = [et for et in self.event_triggers if not et.finished]

    # zero out
    self.conditions["block"] = 0
    self.conditions["evade"] = 0
    
    # progress conditions
    self.conditions["inventive"] = max(self.conditions["inventive"] - 1, 0)
    self.conditions["vulnerable"] = max(self.conditions["vulnerable"] - 1, 0)
    self.conditions["dig"] = max(self.conditions["dig"] - 1, 0)

    # doom
    self.conditions["doom"] = max(self.conditions["doom"] * 2, 0)
    