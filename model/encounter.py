from termcolor import colored
import random
import math
from abc import ABC, abstractmethod
from copy import deepcopy
from model.combat_entity import CombatEntity
from model.event import Event
from content.enemy_actions import NothingAction
from utils import energy_colors


class Enemy(CombatEntity):
  def __init__(self, hp, name, action, entry=NothingAction()):
    super().__init__(hp, name)
    self.action = action
    self.entry = entry
    self.spawned = False
    # add ability triggers?

class EnemySpawn:
  def __init__(self, turn, side, enemy):
    self.turn = turn
    self.side = side
    self.enemy = enemy

class EnemySet:
  def __init__(self, name, enemy_spawns):
    self.name = name
    self.enemy_spawns = enemy_spawns
  
  @property
  def instantiated_enemy_spawns(self):
    return [EnemySpawn(es.turn, es.side, deepcopy(es.enemy)) for es in self.enemy_spawns]

class Encounter:
  def __init__(self, enemy_sets, player):
    self.enemy_sets = enemy_sets
    self.enemy_spawns = []
    for enemy_set in enemy_sets:
      self.enemy_spawns += enemy_set.instantiated_enemy_spawns
    self.player = player
    self.turn = 0
    self.back = []
    self.front = []
    self.dead_enemies = []
    self.events = []

  # -------- @properties --------

  @property
  def combat_entities(self):
    return self.back + [self.player] + self.front

  @property
  def enemies(self):
    return self.back + self.front
    
  @property
  def faced_enemy_queue(self):
    if self.player.facing == "front":
      return self.front
    elif self.player.facing == "back":
      return self.back

  @property
  def escape_turn(self):
    last_enemy_spawn_turn = max(es.turn for es in self.enemy_spawns)
    return max(last_enemy_spawn_turn + 2, 7)

  @property
  def overcome(self):
    all_defeated = all(es.enemy.spawned and es.enemy in self.dead_enemies for es in self.enemy_spawns) 
    return self.turn > self.escape_turn or all_defeated

  # -------- Helpers --------

  def all_other_enemies(self, enemy):
    return [e for e in self.enemies if not e is enemy]

  def move_to_grave(self, enemy):
    try:
      idx = self.back.index(enemy)
      self.dead_enemies.append(self.back.pop(idx))
    except ValueError:
      pass

    try:
      idx = self.front.index(enemy)
      self.dead_enemies.append(self.front.pop(idx))
    except ValueError:
      pass

    print(f"{enemy.name} died!")
    return enemy

  def update_enemy_self_knowledge(self):
    for i, enemy in enumerate(self.back):
      enemy.location = {"side": "back", "position": i}
    for i, enemy in enumerate(self.front):
      enemy.location = {"side": "front", "position": i}

  def run_state_triggers(self):
    back_dead_enemies = [enemy for enemy in self.back if enemy.hp <= 0]
    front_dead_enemies = [enemy for enemy in self.front if enemy.hp <= 0]

    dead_enemies = back_dead_enemies + front_dead_enemies
    for enemy in dead_enemies:
      self.events.append(Event(["enemy_death"], enemy, self, lambda s, t: self.move_to_grave(enemy)))

  def resolve_events(self):
    self.run_state_triggers()
    while len(self.events) > 0:
      # resolve every event
      for event in self.events:
        event.resolve()
        input(f"Resolved event {event}...")
      self.events = []

      # state triggers
      self.run_state_triggers()

      # gather any new events that were triggered
      for entity in self.combat_entities:
        self.events += entity.pop_events()

  # Phase handlers

  def player_upkeep(self):
    prolific = self.player.conditions["prolific"]
    self.player.time = (8 if prolific else 4)

  def upkeep_phase(self):
    # begin new round
    self.player_upkeep()
    for entity in self.combat_entities:
      entity.end_round()
    self.turn += 1
    to_spawn = [es for es in self.enemy_spawns if not es.enemy.spawned and es.turn <= self.turn]
    back_spawns = [(es.enemy, self.back) for es in to_spawn if es.side == "b"]
    front_spawns = [(es.enemy, self.front) for es in to_spawn if es.side == "f"]
    for enemy, destination in (front_spawns + back_spawns):
      if self.player.conditions["ward"] > 0:
        print(f"{enemy.name} was warded!")
        self.player.conditions["ward"] -= 1
      else:
        destination.append(enemy)
        enemy.spawned = True
        self.events += enemy.entry.act(enemy, self)
    self.resolve_events()

  def player_end_phase(self):
    # player end step
    for entity in self.combat_entities:
      entity.execute_conditions()
    # tick searing presence
    if (faced := self.faced_enemy_queue) and (searing := self.player.conditions["searing"]):
      damage = faced[0].assign_damage(searing)
      print(f"{faced[0].name} took {damage} damage from searing presence!")
    # recharge random spell
    recharge_candidates = [sp for sp in self.player.spellbook.spells
                          if sp.charges < sp.max_charges and "Passive" not in sp.spell]
    if len(recharge_candidates) > 0:
      random.choice(recharge_candidates).recharge()
    #
    self.resolve_events()

  def enemy_phase(self):
    # do enemy turn
    for enemy in self.enemies:
      if enemy.conditions["stun"] <= 0:
        self.events += enemy.action.act(enemy, self)
      else:
        print(f"{enemy.name} is stunned!")
    self.resolve_events()

  def end_player_turn(self):
    self.player_end_phase()
    self.enemy_phase()
    self.upkeep_phase()

  def end_encounter(self):
    # add player loot
    for color, v in self.player.conditions.items():
      if color in energy_colors:
        self.player.loot[f"{color.title()} Essence"] += v
    for enemy in self.dead_enemies:
      bounties = math.ceil(enemy.max_hp / 5)
      self.player.loot["Bounties"] += bounties

    # reset player state
    for spell in self.player.spellbook.spells:
      spell.charges = 2
      spell.exhausted = False
    self.player.spellbook.current_page_idx = 0
    self.player.facing = "front"
    for condition in self.player.conditions.keys():
      self.player.conditions[condition] = 0
    self.player.conditions["durable"] = None


  # Rendering

  def render_combat(self):
    print(self.player.spellbook.render_current_page() + "\n")
    print(f"-------- Front --------")
    for enemy in reversed(self.front):
      print(f"- {enemy.render()}")

    turn_str = f"(T{self.turn})"
    if self.turn == self.escape_turn:
      turn_str = colored(turn_str, "magenta")

    face_character = "↑" if self.player.facing == "front" else "↓"
    bookend = colored(f"{face_character*8} ", "green" if self.player.facing == "front" else "red")
    print(f"\n {bookend}" + f"{self.player.render()} {turn_str}" + f"{bookend} \n")
    for enemy in self.back:
      print(f"- {enemy.render()}")
    print(f"-------- Back --------")
    

  