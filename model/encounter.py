from typing import Literal
from termcolor import colored
import time
import random
import math
from abc import ABC, abstractmethod
from copy import deepcopy
from model.combat_entity import CombatEntity
from model.event import Event
from content.enemy_actions import NothingAction
from content.rituals import rituals
from content.items import starting_weapons, signature_items, minor_energy_potions
from utils import energy_colors, colorize, get_combat_entities, choose_idx, get_spell
from sound_utils import play_sound


class Enemy(CombatEntity):
  def __init__(self, hp, name, action, entry=NothingAction(), exp=None):
    super().__init__(hp, name)
    self.faction = None
    self.action = action
    self.entry = entry
    self.spawned = False
    self.experience = exp or math.ceil(self.max_hp / 2)
    # add ability triggers?

class EnemySpawn:
  def __init__(self, turn, side: Literal["f", "b"], enemy, wave=1):
    self.turn = turn
    self.original_turn = turn # unaffected by ward
    self.side = side
    self.enemy = enemy
    self.wave = wave

class EnemySet:
  def __init__(self, name, enemy_spawns, faction="Unknown", exp=None):
    self.name = name
    self.enemy_spawns = enemy_spawns
    self.experience = exp or 15
    self.faction = faction
  
  @property
  def instantiated_enemy_spawns(self):
    enemy_spawns = []
    for es in self.enemy_spawns:
      instantiated_enemy = deepcopy(es.enemy)
      # instantiated_enemy.faction = self.faction
      enemy_spawns.append(EnemySpawn(es.turn, es.side, instantiated_enemy))
    return enemy_spawns

class EnemyWave:
  def __init__(self, enemy_sets, delay=0):
    self.enemy_sets = enemy_sets
    self.delay = delay
  
  @property
  def instantiated_enemy_spawns(self):
    enemy_spawns = []
    for i, enemy_set in enumerate(self.enemy_sets):
        enemy_set_spawns = [EnemySpawn(es.turn + self.delay, es.side, es.enemy, wave=i+1)
                            for es in enemy_set.instantiated_enemy_spawns]
        enemy_spawns += enemy_set_spawns
    return enemy_spawns

class Encounter:
  def __init__(self, waves, player, ambient_energy=None, basic_items=[], special_items=[], boss=False):
    self.waves = waves
    self.rituals = []
    self.ambient_energy = ambient_energy or random.choice(energy_colors)
    self.boss = boss
    self.enemy_spawns = []
    self.basic_items = basic_items
    self.special_items = special_items
    for wave in self.waves:
      self.enemy_spawns += wave.instantiated_enemy_spawns
    self.player = player
    self.turn = 0
    self.back = []
    self.front = []
    self.dead_enemies = []
    self.events = []
    self.max_turns = 9
    self.min_turns = 6
    self.scheduled_commands = []
    self.spells_cast_this_turn = []

  # -------- @properties --------

  @property
  def enemy_sets(self):
    return sum([wave.enemy_sets for wave in self.waves], [])

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
  def unfaced_enemy_queue(self):
    if self.player.facing == "front":
      return self.back
    elif self.player.facing == "back":
      return self.front

  @property
  def escape_turn(self):
    last_enemy_spawn_turn = max(es.original_turn for es in self.enemy_spawns if es.turn <= self.max_turns)
    # you can escape 2 turns after the last enemy spawned,
    # but not earlier than turn 6, nor later than turn 9
    return min(max(last_enemy_spawn_turn + 2, self.min_turns), self.max_turns)

  @property
  def overcome(self):
    all_defeated = all(es.enemy.spawned and es.enemy in self.dead_enemies for es in self.enemy_spawns) 
    return (self.turn > self.escape_turn or all_defeated) and self.player.hp > 0

  @property
  def last_spell_cast(self):
    if self.spells_cast_this_turn:
      return self.spells_cast_this_turn[-1] 

  # -------- Helpers --------

  def get_containing_side_queue(self, enemy):
    if enemy in self.back:
      return self.back
    elif enemy in self.front:
      return self.front
    else:
      raise ValueError(f"{enemy.name} not in either side queue!")

  def all_other_enemies(self, enemy):
    return [e for e in self.enemies if not e is enemy]

  def move_to_grave(self, enemy):
    try:
      enemy.dead = True
      idx = self.back.index(enemy)
      self.dead_enemies.append(self.back.pop(idx))
      if enemy.max_hp <= 10:
        play_sound("enemy-death-small.mp3", channel=2)
      else:
        play_sound("enemy-death-large.mp3", channel=2)
    except Exception as e:
      print(f"---------------------- {e}")

    try:
      idx = self.front.index(enemy)
      self.dead_enemies.append(self.front.pop(idx))
    except Exception as e:
      print(f"---------------------- {e}")

    print(f"{enemy.name} died!")
    return enemy

  def update_enemy_self_knowledge(self):
    for i, enemy in enumerate(self.back):
      enemy.location = {"side": "back", "position": i}
    for i, enemy in enumerate(self.front):
      enemy.location = {"side": "front", "position": i}

  def run_state_triggers(self):
    back_dead_enemies = [enemy for enemy in self.back if enemy.hp <= 0 and not enemy.dead]
    front_dead_enemies = [enemy for enemy in self.front if enemy.hp <= 0 and not enemy.dead]

    dead_enemies = back_dead_enemies + front_dead_enemies
    for enemy in dead_enemies:
      self.player.experience += enemy.experience
      enemy.dead = True
      self.events.append(Event(["enemy_death"], enemy, self, lambda s, t: self.move_to_grave(s)))

  def run_event_triggers(self, event):
    # run passive spell triggers
    passive_spells = [spell.spell for spell in self.player.spellbook.current_page.spells
                      if spell.spell.type == "Passive"]
    for passive_spell in passive_spells:
      if trigger_output := passive_spell.triggers_on(self, event):
        print(f"-------------- TRIGGERED! {passive_spell.description} --------------")
        passive_spell.cast(self, trigger_output=trigger_output)
      
  def gather_events_from_combat_entities(self):
    # gather any new events that were triggered
    for entity in self.combat_entities:
      self.events += entity.pop_events()

  def resolve_events(self):
    self.run_state_triggers()
    self.gather_events_from_combat_entities()
    while len(self.events) > 0:
      # resolve every event
      event = self.events.pop(0)
      if event.blocking:
        input(f"Resolving event {event}...")
      else:
        print(f"Resolving event {event}...")
      event.resolve()
      # run triggers based on this event
      self.run_event_triggers(event)

      # Gather any more events
      self.run_state_triggers()
      self.gather_events_from_combat_entities()

  def use_item(self, idx=None):
    if idx:
      item_idx = idx - 1
    else:
      item_idx = choose_idx(self.player.inventory, "use item > ")
    item = self.player.inventory[item_idx]
    item.use(self)
    self.player.inventory = [item for item in self.player.inventory if item.charges > 0]

  def banish(self, target, ward=0):
    idx = target.position(self)
    if target in self.back:
      self.back.pop(idx)
    if target in self.front:
      self.front.pop(idx)
    target.clear_conditions()
    target.spawned = False
    target.conditions["ward"] += ward

    

  def explore(self):
    play_sound("explore.mp3")
    self.player.explored += 1
    r = random.random()
    if r < 0.02:
      play_sound("explore-find.mp3")
      found_item = deepcopy(random.choice(self.special_items))
      input(colored("What's this, grasped in the hand of a long dead mage? It hums with magic.", "magenta"))
    elif r < 0.08:
      found_item = deepcopy(random.choice(self.basic_items))
      input(colored("Something useful glints in the torchlight...", "green"))
    elif r < 0.12:
      play_sound("explore-find.mp3")
      found_item = deepcopy(random.choice(minor_energy_potions))
      input(colored("Something useful glints in the torchlight...", "green"))
    else:
      found_item = None
      print(colored(f"Something lies within these passages... (explored {self.player.explored})", "blue"))
    
    if found_item:
      print(f"Found: {found_item.render()}")
      self.player.inventory.append(found_item)

  def handle_command(self, cmd):
    print(f"Handling command '{cmd}' ...")
    cmd_tokens = cmd.split(" ")
    try:
      if cmd == "win":
        self.turn = 10
      elif cmd_tokens[0] == "experience":
        magnitude = int(cmd_tokens[1])
        self.player.experience += magnitude
      elif cmd_tokens[0] == "time":
        magnitude = int(cmd_tokens[1])
        self.player.spend_time(magnitude)
      elif cmd_tokens[0] == "use":
        item_index = int(cmd_tokens[1])
        item_idx = item_index - 1
        item = self.player.inventory[item_idx]
        if self.player.time >= item.time_cost:
          self.player.spend_time(cost=item.time_cost)
          item.use(self)
          self.player.inventory = [item for item in self.player.inventory if item.charges > 0]
          play_sound("inventory.mp3")
        else:
          input(colored("Not enough time to use that item!", "red"))
      elif cmd in ["explore", "x"]:
        self.player.spend_time()
        self.explore()
      elif cmd == "face?":
        self.player.switch_face()
      elif cmd == "face":
        self.player.spend_time()
        self.player.switch_face()
      elif cmd == "page":
        self.player.spend_time()
        self.player.spellbook.switch_page()
        self.events.append(Event(["page"]))
      elif cmd == "page?":
        self.player.spellbook.switch_page()
        self.events.append(Event(["page"]))
      elif cmd_tokens[0] in ["recharge", "re"]:
        target = get_spell(self, cmd_tokens[1])
        target.recharge()
      elif cmd_tokens[0] in ["cast", "ecast", "ccast"]:
        target = self.player.spellbook.current_page.spells[int(cmd_tokens[1]) - 1]
        if target.spell.type == "Passive":
          input(colored("Cannot cast passive spells.", "red"))
          return
        self.player.spend_time()
        self.spells_cast_this_turn.append(target)
        target.cast(self,
                  cost_energy=not cmd_tokens[0] == "ccast",
                  cost_charges=not cmd_tokens[0] == "ecast")
        self.events.append(Event(["spell_cast"], metadata={"spell": target}))
      elif cmd_tokens[0] == "fcast":
        target = self.player.spellbook.current_page.spells[int(cmd_tokens[1]) - 1]
        self.spells_cast_this_turn.append(target)
        target.cast(self, cost_energy=False, cost_charges=False)
      elif cmd_tokens[0] in energy_colors and cmd_tokens[1] == "to" and cmd_tokens[2] in energy_colors:
        self.player.conditions[cmd_tokens[0]] -= 1
        self.player.conditions[cmd_tokens[2]] += 1
      elif cmd_tokens[0] == "call":
        magnitude = int(cmd_tokens[1])
        non_imminent_spawns = [es for es in self.enemy_spawns
                                if es.turn > self.turn + 1]
        if non_imminent_spawns:
          sorted(non_imminent_spawns, key=lambda es: es.turn)[0].turn -= magnitude
      elif cmd_tokens[0] == "banish":
        ward = int(cmd_tokens[2]) if len(cmd_tokens) > 2 else 0
        targets = get_combat_entities(self, cmd_tokens[1])
        for target in targets:
          self.banish(target, ward=ward)
      elif cmd_tokens[0] == "damage" or cmd_tokens[0] == "d":
        targets = get_combat_entities(self, cmd_tokens[1])
        magnitude = int(cmd_tokens[2])
        for target in targets:
          self.player.attack(target, magnitude)
      elif cmd_tokens[0] == "lifesteal":
        targets = get_combat_entities(self, cmd_tokens[1])
        magnitude = int(cmd_tokens[2])
        for target in targets:
          self.player.attack(target, magnitude, lifesteal=True)
      elif cmd_tokens[0] == "suffer" or cmd_tokens[0] == "s":
        targets = get_combat_entities(self, cmd_tokens[1])
        magnitude = int(cmd_tokens[2])
        for target in targets:
          target.suffer(magnitude)
        play_sound("suffer.mp3")
      elif cmd_tokens[0] == "heal":
        targets = get_combat_entities(self, cmd_tokens[1])
        magnitude = int(cmd_tokens[2])
        for target in targets:
          target.hp += magnitude
      elif cmd_tokens[0] == "delay":
        magnitude = int(cmd_tokens[1])
        delayed_command = " ".join(cmd_tokens[2:])
        self.scheduled_commands.append((delayed_command, self.turn + magnitude))
      elif cmd_tokens[0] == "repeat":
        magnitude = int(cmd_tokens[1])
        repeated_command = " ".join(cmd_tokens[2:])
        for _ in range(magnitude):
          self.handle_command(repeated_command)
      else:
        condition = cmd_tokens[0]
        targets = get_combat_entities(self, cmd_tokens[1])
        if cmd_tokens[2][0] == "=":
          magnitude = int(cmd_tokens[2][1:])
          set_value = True
        else:
          magnitude = int(cmd_tokens[2])
          set_value = False

        for target in targets:
          if set_value:
            target.conditions[condition] = magnitude
          else:
            target.conditions[condition] = (target.conditions[condition] or 0) + magnitude

          if condition == "enduring" and target.conditions["enduring"] == 0:
            target.conditions["enduring"] = None
          if condition == "durable" and target.conditions["durable"] == 0:
            target.conditions["durable"] = None
        play_sound(f"apply-{condition}.mp3", channel=1)
    except (KeyError, IndexError, ValueError, TypeError) as e:
      print(e)
    self.resolve_events()

  # Phase handlers

  def ritual_upkeep(self):
    for ritual in self.rituals:
      if ritual.encounter_trigger(self):
        ritual.effect(self)
        print(colored(f"{ritual.name} triggered on turn {self.turn}!", "yellow"))
    
  def player_upkeep(self):
    prolific = self.player.conditions["prolific"]
    slow = self.player.conditions["slow"]
    time = 4
    if prolific:
      time += 4
      self.player.conditions["prolific"] = max(self.player.conditions["prolific"] - 1, 0)
    if slow:
      time -= 1
      self.player.conditions["slow"] = max(self.player.conditions["slow"] - 1, 0)
    self.player.time = time
    self.events.append(Event(["begin_turn"]))
    self.resolve_events()

  def upkeep_phase(self):
    # begin new round
    self.turn += 1
    self.spells_cast_this_turn = []
    # Spawn enemies
    to_spawn = [es for es in self.enemy_spawns if not es.enemy.spawned and es.turn <= self.turn]
    # Resurrect enemies
    for enemy in self.dead_enemies:
      undying = enemy.conditions["undying"]
      if undying:
        enemy.hp = 3
        enemy.clear_conditions()
        enemy.conditions["undying"] = max(0, undying - 1)
        enemy.spawned = False
        enemy.dead = False
        to_spawn.append(EnemySpawn(self.turn, "b", enemy))
    back_spawns = [(es.enemy, self.back) for es in to_spawn if es.side == "b"]
    front_spawns = [(es.enemy, self.front) for es in to_spawn if es.side == "f"]
    for enemy, destination in (front_spawns + back_spawns):
      if self.player.conditions["ward"] > 0:
        print(f"{enemy.name} was warded!")
        self.player.conditions["ward"] -= 1
      elif enemy.conditions["ward"] > 0:
        print(f"{enemy.name} was warded!")
        enemy.conditions["ward"] -= 1
      else:
        destination.append(enemy)
        enemy.spawned = True
        self.events += enemy.entry.act(enemy, self)
    self.player_upkeep()
    self.ritual_upkeep()

  def player_end_phase(self):
    # self.resolve_events()
    # player end step
    for entity in self.combat_entities:
      entity.execute_conditions()
    # tick searing presence
    if (faced := self.faced_enemy_queue) and (searing := self.player.conditions["searing"]):
      damage = faced[0].assign_damage(searing)
      print(f"{faced[0].name} took {damage} damage from searing presence!")
      play_sound("tick-searing.mp3")
    # add end_turn event
    self.events.append(Event(["end_turn"]))
    self.resolve_events()
    # recharge random spell
    recharge_candidates = [sp for sp in self.player.spellbook.spells
                          if sp.charges < sp.max_charges and
                          sp.spell.type != "Passive" and
                          "Unrechargeable" not in sp.spell.description and
                          sp.echoing is None]
    if len(recharge_candidates) > 0:
      random.choice(recharge_candidates).recharge()
    # unexhaust all spells
    for spell in self.player.spellbook.spells:
      spell.exhausted = False
    self.resolve_events()

  def enemy_phase(self):
    # do enemy turn
    for enemy in self.enemies:
      if enemy.conditions["stun"] <= 0:
        self.events += enemy.action.act(enemy, self)
      else:
        print(f"{enemy.name} is stunned!")
    self.resolve_events()

  def post_enemy_scheduled_commands(self):
    # execute any scheduled commands
    for cmd, turn in self.scheduled_commands:
      if self.turn == turn:
        self.handle_command(cmd)

  def round_end_phase(self):
    self.events.append(Event(["end_round"]))
    self.resolve_events()
    for entity in self.combat_entities:
      entity.end_round()

  def end_player_turn(self):
    play_sound("turn-end.mp3")
    self.player_end_phase()
    self.enemy_phase()
    self.post_enemy_scheduled_commands()
    self.round_end_phase()

    self.damage_taken_this_turn = 0
    self.damage_survived_this_turn = 0

    self.upkeep_phase()

  def end_encounter(self):
    # progress rituals
    for ritual in self.player.rituals:
      ritual.progressor(self)
      print(f"{ritual.name} progressed!")
      input(ritual.render())

    # add player loot
    for color, v in self.player.conditions.items():
      if color in energy_colors:
        self.player.resources[color] += v
    experience_gained = 0
    for es in self.enemy_sets:
      experience_gained += es.experience
    self.player.experience += experience_gained
    print(colored(f"You gained {experience_gained} experience! Now at {self.player.level_progress_str}", "green"))

    # reset player state
    for spell in self.player.spellbook.spells:
      spell.charges = 2
      spell.exhausted = False
    self.player.spellbook.current_page_idx = 0
    self.player.facing = "front"
    self.player.clear_conditions()
    self.player.damage_survived_this_turn = 0
    self.player.damage_taken_this_turn = 0
    self.player.events = []


  # Rendering

  def render_preview(self, preview_enemy_sets=None):
    preview_enemy_sets = preview_enemy_sets or self.enemy_sets[0:1]
    preview_enemy_set_names = ", ".join([es.name for es in preview_enemy_sets])
    return colorize(
      colored("Enemy Sets: ", "red") +
      f"{len(self.enemy_sets)} ({preview_enemy_set_names}), "
      f"Ambient {self.ambient_energy}")

  def render_combat(self, show_intents=False):
    print(self.player.spellbook.render_current_page() + "\n")
    print(f"-------- Front --------")
    for enemy in reversed(self.front):
      render_str = f"- {enemy.render()}"
      if show_intents:
        render_str += f" | {enemy.action}"
      print(render_str)

    turn_str = f"(T{self.turn})"
    if self.turn == self.escape_turn:
      turn_str = colored(turn_str, "magenta")

    face_character = "↑" if self.player.facing == "front" else "↓"
    bookend = colored(f"{face_character*8} ", "green" if self.player.facing == "front" else "red")
    print(f"\n {bookend}" + f"{self.player.render()} {turn_str}" + f"{bookend} \n")
    for enemy in self.back:
      render_str = f"- {enemy.render()}"
      if show_intents:
        render_str += f" | {enemy.action}"
      print(render_str)
    print(f"-------- Back --------")
    

  