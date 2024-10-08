from typing import Any, Dict, List, Literal, Optional
from content.trigger_functions import trigger_player_defense_break
from model.combat_entity import CombatEntity
from model.triggers import EventTrigger
from termcolor import colored
import time
import random
import math
from copy import deepcopy
from model.event import Event
from model.enemy import EnemySpawn
from content.enemy_actions import AddConditionAction, MultiAction, NothingAction, involves_add_undying
from content.items import starting_weapons, minor_energy_potions, minor_energy_potions_dict
from content.enemy_factions import faction_dict
from utils import choose_obj, choose_str, energy_colors, colorize, get_combat_entities, choose_idx, get_spell, numbered_list, ws_input, ws_print, ws_update_player_state_reference
from sound_utils import faf_play_sound, play_sound, ws_play_sound


# --------- Helpers

def render_event(self) -> str:
  source_part = f"From: {self.source.name}" if self.source and isinstance(self.source, CombatEntity) else ""
  target_part = f"To: {self.target.name}" if self.target and isinstance(self.target, CombatEntity) else ""
  description_part = f" - {', '.join([source_part, target_part])}" if (source_part and target_part) else ""
  return f"{self.tags}{description_part}"

# -------- Classes


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
  def __init__(self, waves, player, difficulty, basic_items=[], special_items=[], unique_items=[], boss=False):
    self.waves = waves
    self.rituals = []
    self.boss = boss
    self.difficulty = difficulty
    self.enemy_spawns = []
    self.basic_items = basic_items
    self.special_items = special_items
    self.unique_items = unique_items
    for wave in self.waves:
      self.enemy_spawns += wave.instantiated_enemy_spawns
    self.player = player
    self.turn = 0
    self.back = []
    self.front = []
    self.dead_enemies = []
    self.events = []
    self.scheduled_commands = []
    self.spells_cast_this_turn = []
    self.dropped_items = []
    self.win = False

  # -------- @properties --------

  @property
  def min_turns(self):
    return 5 + len(self.waves)
  
  @property
  def max_turns(self):
    return 8 + len(self.waves) + (1 if self.difficulty >= 3 else 0)

  @property
  def enemy_sets(self):
    return sum([wave.enemy_sets for wave in self.waves], [])

  @property
  def combat_entities(self):
    return self.back + [self.player] + self.front

  @property
  def enemies(self) -> List[CombatEntity]:
    enemies_list = []
    for i in range(max(len(self.back), len(self.front))):
      if i < len(self.front):
        enemies_list.append(self.front[i])
      if i < len(self.back):
        enemies_list.append(self.back[i])
    return enemies_list
    
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
    difficulty_modifier = 1 if self.difficulty >= 3 else 0
    # you can escape 2 turns after the last enemy spawned,
    # but not earlier than turn 6, nor later than turn 9
    return min(max(last_enemy_spawn_turn + 2, self.min_turns), self.max_turns) + difficulty_modifier

  @property
  def overcome(self):
    if self.win:
      return True
    all_defeated = all(es.enemy.spawned and es.enemy in self.dead_enemies for es in self.enemy_spawns)
    no_undying = not any(enemy.conditions["undying"] > 0 for enemy in self.dead_enemies)
    return (self.turn > self.escape_turn or (all_defeated and no_undying)) and self.player.hp > 0

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
        faf_play_sound("enemy-death-small.mp3", enemy.websocket, channel=2)
      else:
        faf_play_sound("enemy-death-large.mp3", enemy.websocket, channel=2)
    except Exception as e:
      print(f"---------------------- {e}")

    try:
      idx = self.front.index(enemy)
      self.dead_enemies.append(self.front.pop(idx))
    except Exception as e:
      print(f"---------------------- {e}")

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
      if not enemy.conditions["undying"]:
        self.player.experience += enemy.experience
      enemy.dead = True
      self.events.append(Event(["enemy_death"], enemy, self, lambda s, t: self.move_to_grave(s)))

  async def run_event_triggers(self, event):
    # run passive spell triggers
    passive_spells = [spell.spell for spell in self.player.spellbook.current_page.spells
                      if spell.spell.type == "Passive"]
    for passive_spell in passive_spells:
      if trigger_output := passive_spell.triggers_on(self, event):
        await ws_input(f"Passive triggered: {passive_spell.description}", self.player.websocket)
        await passive_spell.cast(self, trigger_output=trigger_output)

    # run player triggers
    for event_trigger in self.player.event_triggers:
      if trigger_output := event_trigger.triggers_on(self, event):
        await event_trigger.execute(self, event, trigger_output=trigger_output)
      
  def gather_events_from_combat_entities(self):
    # gather any new events that were triggered
    for entity in self.combat_entities:
      self.events += entity.pop_events()

  async def resolve_events(self):
    self.run_state_triggers()
    self.gather_events_from_combat_entities()
    while len(self.events) > 0:
      # resolve every event
      event = self.events.pop(0)
      if event.blocking:
        await ws_input(f"Resolving event: {render_event(event)}", self.player.websocket)
      elif event.description:
        await ws_print(f"Resolving event: {render_event(event)}", self.player.websocket)
        # ws_print(f"Resolving event {event.render()}...")
      event.resolve()
      # run triggers based on this event
      await self.run_event_triggers(event)

      # Gather any more events
      self.run_state_triggers()
      self.gather_events_from_combat_entities()

  def banish(self, target, ward=0):
    if target is None:
      return
    idx = target.position(self)
    if target in self.back:
      self.back.pop(idx)
    if target in self.front:
      self.front.pop(idx)
    # Let's try not clearing conditions...
    target.clear_good_conditions()
    target.spawned = False
    target.conditions["ward"] += ward
    target.resurrected = False
    
  def call(self, magnitude, random=False):
    non_imminent_spawns = [es for es in self.enemy_spawns
                            if es.turn > self.turn + 1]
    if non_imminent_spawns:
      if random:
        target_spawn = random.choice(non_imminent_spawns)
      else:
        target_spawn = sorted(non_imminent_spawns, key=lambda es: es.turn)[0]
      target_spawn.turn -= magnitude

  async def explore(self):
    await ws_play_sound("explore.mp3", self.player.websocket)
    self.player.explored += 1
    self.player.experience += 1
    await self.player.gain_material(1)
    r = random.random()
    found_item = None
    if r < 0.02:
      await ws_play_sound("explore-find.mp3", self.player.websocket)
      found_item = deepcopy(random.choice(self.special_items))
      await ws_input(colored("What's this, grasped in the hand of a long dead mage? It hums with magic.", "magenta"), self.player.websocket)
    elif r < 0.08:
      found_item = deepcopy(random.choice(self.basic_items))
      await ws_input(colored("Something useful glints in the torchlight...", "green"), self.player.websocket)
    elif r < 0.16:
      await ws_play_sound("explore-find.mp3", self.player.websocket)
      found_item = deepcopy(random.choice(minor_energy_potions))
      await ws_input(colored("Something useful glints in the torchlight...", "green"), self.player.websocket)
    else:
      found_item = None
      await ws_print(colored(f"Something lies within these passages... (explored {self.player.explored})", "blue"), self.player.websocket)
    if found_item:
      await ws_print(f"Found: {found_item.render()}", self.player.websocket)
      self.player.inventory.append(deepcopy(found_item))
      self.player.seen_items.append(deepcopy(found_item))
      await ws_update_player_state_reference(self.player)

  async def observe(self):
    self.player.experience += 2
    observed_factions = [e.faction for e in self.faced_enemy_queue]
    observed_factions = observed_factions[0:1] # just take immediate for now
    if not observed_factions:
      return
    await self.player.gain_secrets(observed_factions[0], 1)
    for faction in observed_factions:
      faction_obj = faction_dict[faction]
      if self.player.rituals_dict.get(faction) is None:
        self.player.rituals.append(deepcopy(faction_obj.ritual))
      self.player.rituals_dict[faction].progress += 1
      await ws_print(colored(f"{faction_obj.ritual.name} advanced to {faction_obj.ritual.progress}/{faction_obj.ritual.required_progress}!", "yellow"), self.player.websocket)


  async def handle_command(self, cmd):
    await ws_print(f"Handling command '{cmd}' ...", self.player.websocket)
    cmd_tokens = cmd.split(" ")
    try:
      if cmd_tokens[0] == "experience":
        magnitude = int(cmd_tokens[1])
        self.player.experience += magnitude
      elif cmd_tokens[0] == "time":
        magnitude = int(cmd_tokens[1])
        self.player.spend_time(magnitude)
      elif cmd_tokens[0] == "use":
        item_index = int(cmd_tokens[1])
        item_idx = item_index - 1
        item = self.player.inventory[item_idx]
        if self.player.time >= item.time_cost and item.charges > 0 and item.useable:
          self.player.spend_time(cost=item.time_cost)
          await item.use(self)
          await ws_play_sound("inventory.mp3", self.player.websocket)
          await ws_update_player_state_reference(self.player)
        else:
          await ws_input(colored("Not enough time / charges to use that item!", "red"), self.player.websocket)
      elif cmd in ["explore", "x"]:
        self.player.spend_time()
        await self.explore()
      elif cmd in ["observe", "o"]:
        self.player.spend_time()
        await self.observe()
      elif cmd == "face?":
        await self.player.switch_face(event=False)
      elif cmd == "face!":
        await self.player.switch_face()
      elif cmd == "face":
        self.player.spend_time()
        await self.player.switch_face()
      elif cmd == "page":
        self.player.spend_time()
        await self.player.spellbook.switch_page(self.player.websocket)
        self.events.append(Event(["page"]))
      elif cmd == "page?":
        await self.player.spellbook.switch_page(self.player.websocket)
      elif cmd == "page!":
        await self.player.spellbook.switch_page(self.player.websocket)
        self.events.append(Event(["page"]))
      elif cmd_tokens[0] in ["recharge", "re"]:
        target = await get_spell(self, cmd_tokens[1], self.player.websocket)
        target.recharge()
      elif cmd_tokens[0] in ["refresh", "rf"]:
        target = await get_spell(self, cmd_tokens[1], self.player.websocket)
        target.exhausted = False
      elif cmd_tokens[0] in ["cast", "ecast", "ccast"]:
        target = self.player.spellbook.current_page.spells[int(cmd_tokens[1]) - 1]
        if not await target.castable_by(self.player):
          return
        self.player.spend_time()
        self.spells_cast_this_turn.append(target)
        await target.cast(self,
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
      elif cmd_tokens[0] == "wild":
        color = await choose_str(energy_colors, "Choose a color to gain > ", self.player.websocket)
        await self.handle_command(f"{color} p 1")
      elif cmd_tokens[0] == "call":
        magnitude = int(cmd_tokens[1])
        self.call(magnitude)
      elif cmd_tokens[0] == "banish":
        ward = int(cmd_tokens[2]) if len(cmd_tokens) > 2 else 0
        targets = await get_combat_entities(self, cmd_tokens[1], websocket=self.player.websocket)
        for target in targets:
          self.banish(target, ward=ward)
      elif cmd_tokens[0] == "damage" or cmd_tokens[0] == "d":
        targets = await get_combat_entities(self, cmd_tokens[1], websocket=self.player.websocket)
        magnitude = int(cmd_tokens[2])
        for target in targets:
          self.player.attack(target, magnitude)
      elif cmd_tokens[0] == "lifesteal":
        targets = await get_combat_entities(self, cmd_tokens[1], websocket=self.player.websocket)
        magnitude = int(cmd_tokens[2])
        for target in targets:
          self.player.attack(target, magnitude, lifesteal=True)
      elif cmd_tokens[0] == "suffer" or cmd_tokens[0] == "s":
        targets = await get_combat_entities(self, cmd_tokens[1], websocket=self.player.websocket)
        magnitude = int(cmd_tokens[2])
        for target in targets:
          target.suffer(magnitude)
        await ws_play_sound("suffer.mp3", self.player.websocket)
      elif cmd_tokens[0] == "heal":
        targets = await get_combat_entities(self, cmd_tokens[1], websocket=self.player.websocket)
        magnitude = int(cmd_tokens[2])
        for target in targets:
          target.hp += magnitude
      elif cmd_tokens[0] == "delay":
        magnitude = int(cmd_tokens[1])
        delayed_command = " ".join(cmd_tokens[2:])
        self.scheduled_commands.append((delayed_command, self.turn + magnitude))
      elif cmd_tokens[0] == "break":
        break_command = " ".join(cmd_tokens[1:])
        event_trigger = EventTrigger(triggers_on=trigger_player_defense_break,
                                     executor=[break_command],
                                     turns_remaining=1, tags=["defense_break"])
        self.player.event_triggers.append(event_trigger)
      elif cmd_tokens[0] == "repeat":
        magnitude = int(cmd_tokens[1])
        repeated_command = " ".join(cmd_tokens[2:])
        for _ in range(magnitude):
          await self.handle_command(repeated_command)
      else:
        condition = cmd_tokens[0]
        targets = await get_combat_entities(self, cmd_tokens[1], websocket=self.player.websocket)
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
        await ws_play_sound(f"apply-{condition}.mp3", self.player.websocket, channel=1)
    except (KeyError, IndexError, ValueError, TypeError) as e:
      await ws_print(str(e), self.player.websocket)
    await self.resolve_events()

  # Phase handlers

  async def ritual_upkeep(self):
    for ritual in self.rituals:
      await ritual.run_events(self)
    
  async def player_upkeep(self):
    prolific = self.player.conditions["prolific"]
    slow = self.player.conditions["slow"]
    time = 4
    if prolific:
      time += 4
      self.player.conditions["prolific"] = max(self.player.conditions["prolific"] - 1, 0)
    if slow:
      slow_applied = min(3, slow)
      time -= slow_applied
      self.player.conditions["slow"] -= slow_applied
    self.player.time = time
    if self.turn > 0:
      self.events.append(Event(["begin_turn"]))
    await self.resolve_events()

  # Phases

  async def init_with_player(self, player):
    self.player = player

    chosen_ritual = True
    activable_rituals = [ritual for ritual in self.player.rituals if ritual.activable]
    while chosen_ritual is not None and activable_rituals:
      activable_rituals = [ritual for ritual in self.player.rituals if ritual.activable]
      await ws_print(numbered_list(activable_rituals), self.player.websocket)
      chosen_ritual = await choose_obj(activable_rituals, colored("Choose a ritual to activate > ", "cyan"), self.player.websocket)
      if chosen_ritual:
        self.rituals.append(chosen_ritual)
        chosen_ritual.progress -= chosen_ritual.required_progress
        chosen_ritual.level += 1


  async def upkeep_phase(self):
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
        enemy.resurrected = True
        to_spawn.append(EnemySpawn(self.turn, "b", enemy))
    self.dead_enemies = [e for e in self.dead_enemies if e.dead]
    back_spawns = [(es.enemy, self.back) for es in to_spawn if es.side == "b"]
    front_spawns = [(es.enemy, self.front) for es in to_spawn if es.side == "f"]
    for enemy, destination in (front_spawns + back_spawns):
      if self.player.conditions["ward"] > 0:
        await ws_input(f"{enemy.name} was warded!", self.player.websocket)
        self.player.conditions["ward"] -= 1
      elif enemy.conditions["ward"] > 0:
        await ws_input(f"{enemy.name} was warded!", self.player.websocket)
        enemy.conditions["ward"] -= 1
      else:
        destination.append(enemy)
        enemy.spawned = True
        enemy.spawned_turn = self.turn
        enemy.websocket = self.player.websocket
        if enemy.resurrected and involves_add_undying(enemy.entry):
          if isinstance(enemy.entry, MultiAction):
            for action in enemy.entry.non_undying_action_list:
              self.events += action.act(enemy, self)
        else:
          self.events += enemy.entry.act(enemy, self)
        self.events.append(Event(["enemy_spawn"], metadata={"turn": self.turn, "enemy": enemy}))
    await self.render_combat()
    await self.ritual_upkeep()
    await self.player_upkeep()
    # update the helper UI pane
    await ws_update_player_state_reference(self.player)

  async def player_end_phase(self):
    # collapse spent items in inventory
    self.player.inventory = [item for item in self.player.inventory if item.charges > 0]
    # player end step
    for entity in self.combat_entities:
      entity.execute_conditions()
    # tick searing presence
    if (faced := self.faced_enemy_queue) and (searing := self.player.conditions["searing"]):
      damage = faced[0].assign_damage(searing)
      await ws_print(f"{faced[0].name} took {damage} damage from searing presence!", self.player.websocket)
      await ws_play_sound("tick-searing.mp3", self.player.websocket)
    # add end_turn event
    if self.turn > 0:
      self.events.append(Event(["end_turn"]))
    await self.resolve_events()
    # recharge random spell
    if self.turn > 0:
      off_page_spells = sum([page.spells for i, page in enumerate(self.player.spellbook.pages)
                             if i != self.player.spellbook.current_page_idx], [])
      recharge_candidates = [sp for sp in off_page_spells
                            if sp.charges < sp.max_charges and
                            sp.spell.type != "Passive"]
      # recharge a spell on the current page with p=0.5 if there's nothing to recharge on other pages
      if len(recharge_candidates) == 0:
        recharge_candidates = [sp for sp in self.player.spellbook.current_page.spells
                              if sp.charges < sp.max_charges and
                              sp.spell.type != "Passive"]
      if recharge_candidates:
        random.choice(recharge_candidates).recharge()
    # unexhaust all spells
    for spell in self.player.spellbook.spells:
      spell.exhausted = False
    await self.resolve_events()

  async def enemy_phase(self):
    # do enemy turn
    for enemy in self.enemies:
      if enemy.conditions["stun"] <= 0:
        self.events += enemy.action.act(enemy, self)
      else:
        enemy.conditions["stun"] = max(enemy.conditions["stun"] - 1, 0)
        await ws_print(f"{enemy.name} is stunned!", self.player.websocket)
    await self.resolve_events()

  async def post_enemy_scheduled_commands(self):
    # execute any scheduled commands
    for cmd, turn in self.scheduled_commands:
      if self.turn == turn:
        await self.handle_command(cmd)

  async def round_end_phase(self):
    if self.turn > 0:
      self.events.append(Event(["end_round"]))
    await self.resolve_events()
    for entity in self.combat_entities:
      entity.end_round()

  async def end_player_turn(self):
    await ws_play_sound("turn-end.mp3", self.player.websocket)
    if self.win:
      return
    await self.player_end_phase()
    await self.enemy_phase()
    await self.post_enemy_scheduled_commands()
    await self.round_end_phase()

    await self.upkeep_phase()

  async def end_encounter(self):

    # If you have 3 excess energy of one color, turn it into a potion
    for color in ["red", "blue", "gold"]:
      while self.player.conditions[color] >= 3:
        self.player.inventory.append(deepcopy(minor_energy_potions_dict[color]))
        self.player.conditions[color] -= 3
        await ws_input(f"Converted 3 {color} energy into a potion!", self.player.websocket)

    experience_gained = 0
    for es in self.enemy_sets:
      experience_gained += (es.experience + 8 * es.level)
      await self.player.gain_secrets(es.faction, 3 * (es.level + 1))
    self.player.experience += experience_gained
    await ws_print(colored(f"You gained {experience_gained} experience! Now at {self.player.level_progress_str}", "green"), self.player.websocket)

    # reset player state
    for spell in self.player.spellbook.spells:
      spell.charges = 2
      spell.exhausted = False
    self.player.spellbook.current_page_idx = 0
    # Save one page to archive
    if self.player.remaining_blank_archive_pages > 0:
      await ws_print(self.player.spellbook.render(), self.player.websocket)
      chosen_page = await choose_obj(self.player.spellbook.pages, colored("Choose a page to archive > ", "cyan"), self.player.websocket)
      if chosen_page:
        self.player.archived_pages.append(deepcopy(chosen_page))
        self.player.remaining_blank_archive_pages -= 1

    self.player.facing = "front"
    self.player.clear_conditions()
    self.player.damage_survived_this_turn = 0
    self.player.damage_taken_this_turn = 0
    self.player.events = []
    # NOTE: Just let the player keep their ritual progress
    # for ritual in self.player.rituals:
    #   if ritual.progress >= ritual.required_progress:
    #     continue
    #   if random.random() < (ritual.progress / ritual.required_progress):
    #     await ws_print(colored(f"{ritual.name} completed!", "yellow"), self.player.websocket)
    #     ritual.progress = ritual.required_progress
    #   else:
    #     await ws_print(colored(f"{ritual.name} failed!", "red"), self.player.websocket)
    #     ritual.progress = 0
    await self.player.check_level_up()


  # Rendering

  def render_preview(self, preview_enemy_sets=None):
    preview_enemy_sets = preview_enemy_sets or self.enemy_sets[0:1]
    preview_enemy_set_names = ", ".join([es.name for es in preview_enemy_sets])
    return colorize(
      colored("Enemy Sets: ", "red") +
      f"{len(self.enemy_sets)} ({preview_enemy_set_names}), "
      f"Ambient {self.ambient_energy}")

  async def render_combat(self, show_intents=False):
    await ws_print("\n"*20, self.player.websocket)
    await ws_print(self.player.spellbook.render_current_page() + "\n", self.player.websocket)
    await ws_print(colored(f"-------- Front --------", "light_green"), self.player.websocket)
    for i, enemy in reversed(list(enumerate(self.front, start=1))):
      render_str = f"[f{i}] - {enemy.render()}"
      if show_intents:
        render_str += f"\n       {colored(enemy.action, 'dark_grey')}"
      await ws_print(render_str, self.player.websocket)

    turn_str = f"(T{self.turn})"
    if self.turn == self.escape_turn:
      turn_str = colored(turn_str, "magenta")

    face_character = "↑" if self.player.facing == "front" else "↓"
    bookend = colored(f"{face_character*8} ", "green" if self.player.facing == "front" else "red")
    await ws_print(f"\n {bookend}" + f"{self.player.render()} {turn_str}" + f"{bookend} \n", self.player.websocket)
    for i, enemy in enumerate(self.back, start=1):
      render_str = f"[b{i}] - {enemy.render()}"
      if show_intents:
        render_str += f"\n       {colored(enemy.action, 'dark_grey')}"
      await ws_print(render_str, self.player.websocket)
    await ws_print(colored(f"-------- Back --------", "light_red"), self.player.websocket)
    

  