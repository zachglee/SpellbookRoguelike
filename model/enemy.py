from typing import Any, Dict, Literal, Optional
from model.action import Action
from termcolor import colored
import math
from copy import deepcopy
from model.combat_entity import CombatEntity
from content.enemy_actions import NothingAction


class Enemy(CombatEntity):

  faction: Optional[str] = None
  action: Action = NothingAction()
  entry: Action = NothingAction()
  spawned: bool = False
  experience: Optional[int] = None
  websocket: Any = None

  class Config:
    arbitrary_types_allowed = True

  @classmethod
  def make(cls, hp, name, action, entry=NothingAction(), exp=None):
    exp = exp or math.ceil(hp / 2)
    return cls(hp=hp, max_hp=hp, name=name, action=action, entry=entry, experience=exp)

class EnemySpawn:
  def __init__(self, turn, side: Literal["f", "b"], enemy, wave=1):
    self.turn = turn
    self.original_turn = turn # unaffected by ward
    self.side = side
    self.enemy = enemy
    self.wave = wave

class EnemySet:
  def __init__(self, name, enemy_spawns, faction="Unknown", exp=None, description=""):
    self.name = name
    self.enemy_spawns = enemy_spawns
    self.experience = exp or 15
    self.faction: str = faction
    self.level = 0
    self.description = description

    self.pickable = True
    self.obscured = False
    self.persistent = False
  
  @property
  def instantiated_enemy_spawns(self):
    enemy_spawns = []
    for es in self.enemy_spawns:
      instantiated_enemy = deepcopy(es.enemy)
      instantiated_enemy.faction = self.faction
      enemy_spawns.append(EnemySpawn(es.turn, es.side, instantiated_enemy))
    return enemy_spawns

  def level_up(self):
    for es in self.enemy_spawns:
      es.enemy.hp = math.ceil(es.enemy.hp * 1.5)
      es.enemy.max_hp = math.ceil(es.enemy.max_hp * 1.5)
    self.level += 1

  def render(self, show_rules_text=False):
    if self.obscured:
      return_str = colored(f"???", "red")
      if self.persistent:
        return_str += colored(f" (Persistent)", "red")
      if self.level > 0:
        return_str += colored(f" (Lv{self.level})", "red")
      return return_str

    return_str = colored(f"{self.name}", "red")
    if self.level > 0:
      return_str += colored(f" (Lv{self.level})", "red")
    if self.persistent:
      return_str += colored(f" (Persistent)", "red")
    if show_rules_text:
      spawn_turns_str = "Spawn " + "".join([f"{es.turn}" for es in self.enemy_spawns])
      reference_enemy = self.enemy_spawns[-1].enemy
      hp_str = f"{reference_enemy.hp}/{reference_enemy.max_hp}hp"
      intent_str = str(reference_enemy.action)
      description_str = f"{spawn_turns_str} : {hp_str} : {intent_str}"
    else:
      description_str = self.description
    return_str += colored(f" - {description_str}", "magenta")
    return return_str

  def __repr__(self):
    return self.render()