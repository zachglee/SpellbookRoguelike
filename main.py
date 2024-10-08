import asyncio
import random
import dill
import os
from drafting import draft_ritual_for_haven, draft_spell_for_haven, encounter_draft, haven_library_draft, haven_rolling_draft
from model.encounter import Encounter, EnemyWave
from model.map import Map
from model.party_member_state import PartyMemberState
from model.player import Player
from model.region_draft import RegionDraft
from model.spellbook import LibrarySpell
from sound_utils import ws_play_sound
from termcolor import colored
from generators import generate_endgame_enemy_composition, generate_faction_sets, generate_starting_haven_library
from model.haven import Haven
from utils import choose_obj, choose_number, command_reference, get_combat_entities, help_reference, numbered_list, ws_input, ws_print

STARTING_EXPLORED = 1

def load_maps_from_files():
  maps = []
  for fname in os.listdir("saves/maps"):
    with open(f"saves/maps/{fname}", "rb") as f:
      map = dill.load(f)
      maps.append(map)
  return sorted(maps, key=lambda m: m.difficulty)

class GameOver(Exception):
  pass

class WinEncounter(Exception):
  pass

class GameStateV2:
  def __init__(self):
    self.map = None
    self.current_region_idx = 0
    self.player = None
    self.haven = None

    #
    self.show_intents = False
    self.run_length = 3
    self.started = False
    self.party_member_states = {} # Dict of player id to PartyMemberState

  # Properties

  @property
  def current_region(self):
    return self.map.region_drafts[self.current_region_idx]

  # Admin

  def save(self):
    self.map.save()
    for player in [pms.player for pms in self.party_member_states.values()]:
      player.save()
    self.haven.save()

  async def wait_for_teammates(self, my_id, choice_id, teammate_ids=None):
    player_state = self.party_member_states[my_id]
    player_state.completed_choices.append(choice_id)

    if teammate_ids is None:
      teammate_ids = [id for id in self.party_member_states if id != my_id]
    teammate_states = [self.party_member_states[tid] for tid in teammate_ids]
    await ws_print(f"Waiting for {teammate_ids} to be finished with choice {choice_id}...", player_state.player.websocket)
    while True:
      if all(len(player_state.completed_choices) <= len(teammate_state.completed_choices) for teammate_state in teammate_states):
        break
      await asyncio.sleep(1)

  # Generators

  async def generate_new_character(self, spell_pool, websocket=None):
    await ws_print("Starting a new character...", websocket)
    name = await ws_input("What shall they be called? > ", websocket)
    library = [] # [LibrarySpell(chosen_spell.spell, copies=2, signature=True)]
    player = Player.make(hp=30, name=name,
                    spellbook=None,
                    inventory=[],
                    library=library)
                    # signature_spell=chosen_spell)
    return player
  
  def generate_encounter(self, player, combat_size=3, boss=False):
    # generate the encounter
    random.shuffle(player.pursuing_enemysets)
    encounter_enemysets = player.pursuing_enemysets[0:combat_size]
    for enemyset in encounter_enemysets:
      enemyset.obscured = False
    player.pursuing_enemysets = player.pursuing_enemysets[combat_size:] 
    encounter = Encounter([EnemyWave(encounter_enemysets)], player, self.map.difficulty,
                          basic_items=self.current_region.basic_items,
                          special_items=self.current_region.special_items,
                          boss=boss)
    return encounter

  # Game Phases

  async def handle_command(self, cmd, encounter):
    cmd_tokens = cmd.split(" ")
    try:
      if cmd == "win":
        raise WinEncounter()
      elif cmd == "die":
        await self.player_death(encounter.player, encounter)
        return
      elif cmd == "debug":
        targets = await get_combat_entities(self, cmd_tokens[1], websocket=encounter.player.websocket)
        for target in targets:
          await ws_print(target.__dict__, encounter.player.websocket)
        return
      elif cmd == "help":
        await command_reference(websocket=encounter.player.websocket)
      elif cmd in ["inventory", "inv", "i"]:
        await ws_print(encounter.player.render_inventory(), encounter.player.websocket)
        await ws_play_sound("inventory.mp3", encounter.player.websocket)
        return
      elif cmd in ["ritual", "rituals", "rit"]:
        await ws_print(encounter.player.render_rituals(), encounter.player.websocket)
        return
      elif cmd in ["intent", "intents", "int"]:
        self.show_intents = not self.show_intents
        return
      elif cmd == "face?":
        await encounter.player.switch_face(event=False)
        return
      elif cmd == "page?":
        await encounter.player.spellbook.switch_page(encounter.player.websocket)
        return
      elif cmd[-1] == "?":
        subject = cmd[:-1]
        await help_reference(subject, websocket=encounter.player.websocket)
        return
    except (KeyError, IndexError, ValueError, TypeError) as e:
      await ws_print(str(e), encounter.player.websocket)

    # If not a UI command, see if it can be handled as an encounter command
    await encounter.handle_command(cmd)

  async def run_encounter_round(self, encounter):
    while True:
      await encounter.render_combat(show_intents=self.show_intents)
      # check if the player died
      if encounter.player.hp <= 0:
        await self.handle_command("die", encounter)
        return
      cmd = await ws_input(colored("-- cast | use | face | page | explore --", "dark_grey") + "\n> ", encounter.player.websocket)
      if cmd == "done":
        await encounter.end_player_turn()
        break
      if cmd:
        await self.handle_command(cmd, encounter)
        await encounter.render_combat(show_intents=self.show_intents)
        if encounter.player.time <= 0:
          await encounter.end_player_turn()
          break

  async def encounter_phase(self, encounter):
    encounter.player.revive_cost = None
    while not encounter.overcome:
      try:
        await self.run_encounter_round(encounter)
      except WinEncounter:
        break
    await encounter.render_combat()
    await encounter.end_encounter()

    # if the player didn't just die, give the option to revive a dead teammate
    if encounter.player.revive_cost is None:
      await self.wait_for_teammates(encounter.player.id, "postcombat")

      revivable_teammates = [pms.player for pms in self.party_member_states.values()
                            if pms.player.revive_cost is not None]
      print(f"-------------- Revivable teammates: {revivable_teammates}")
      for teammate in revivable_teammates:
        await ws_input(colored(f"You revive {teammate.name} for {teammate.revive_cost}hp...", "red"), encounter.player.websocket)
        encounter.player.hp -= teammate.revive_cost
        teammate.hp = 3
        if encounter.player.hp <= 0:
          raise GameOver()
      await self.wait_for_teammates(encounter.player.id, "revive")

    self.save()

  async def discovery_phase(self, player):
    await ws_play_sound("passage-discovery.mp3", player.websocket)
    await ws_print(colored(f"You explored a total of {player.explored} times.", "green"), player.websocket)
    player.explored = STARTING_EXPLORED
    self.save()

  async def player_death(self, player, encounter):
    if player.conditions["undying"] > 0:
      player.hp = 3
      player.conditions["undying"] -= 1
      return
    await ws_play_sound("player-death.mp3", player.websocket)
    await encounter.render_combat()

    # Wait to see if the player will be revived
    player.revive_cost = 6 + (10 - encounter.turn)
    await ws_input(colored(f"You have died. It will cost {player.revive_cost} to revive you...", "red"), player.websocket)
    await self.wait_for_teammates(encounter.player.id, "postcombat")
    await self.wait_for_teammates(player.id, "revive")
    if player.hp > 0:
      raise WinEncounter()

    # Death admin
    await ws_input("Gained 100xp...", player.websocket)
    player.experience += 100
    await self.discovery_phase(player)
    await player.check_level_up()
    player.wounds += 1
    player.hp = 0
    
    await self.end_run(player)
    self.save()
    raise GameOver()

  async def end_run(self, player):
    self.map.end_run()
    await ws_print(self.haven.render(), player.websocket)
    await player.discover_spells()

    for faction, secrets in player.secrets_dict.items():
      self.haven.secrets_dict[faction] += secrets

    player.age += 1
    # End of run rewards
    num_keys = len([item for item in player.inventory if item.name == "Ancient Key"])
    player.experience += 50 * num_keys
    self.haven.keys += num_keys
    await ws_print(colored(f"You gained {50 * num_keys} experience from keys!", "green"), player.websocket)

    player.inventory = []

    player.websocket = None
    self.save()

  async def choose_character(self, websocket):
    available_characters = []
    for fname in os.listdir("saves/characters"):
      with open(f"saves/characters/{fname}", "rb") as f:
        character = dill.load(f)
        available_characters.append(character)
    await ws_print(numbered_list([c.name for c in available_characters]), websocket)
    character_choice = await ws_input("Choose a character ('new' to make a new character) > ", websocket)
    if character_choice == "new":
      player = await self.generate_new_character([], websocket)
    else:
      character_file = f"saves/characters/{character_choice}.pkl"
      with open(character_file, "rb") as f:
        player = dill.load(f)
    player.init()
    return player
  
  async def choose_map(self, websocket):
    existing_maps = load_maps_from_files()
    existing_maps = [m for m in existing_maps if not m.completed]
    while True:
      await ws_print(numbered_list(existing_maps), websocket)
      map_choice = await choose_obj(existing_maps, "Choose a map for your run (or type 'done' to start a new map) > ", websocket)
      if map_choice:
        map = map_choice
        await ws_print(f"You embark on {map.render()}...", websocket)
        break
      elif map_choice is None and self.haven.keys >= self.haven.season + 1:
        # self.haven.keys -= 1
        # map = Map(name=None, difficulty=random.choice([1, 2, 3]))
        # await ws_print(f"This new land is called... {colored(map.name, 'magenta')}", websocket)
        # break
        for i in range(4):
          map = map = Map(name=None, difficulty=i + self.haven.season)
          if i == 3:
            map.boss = True
          map.save()
        existing_maps = load_maps_from_files()
        self.haven.season += 1
        continue
      else:
        await ws_input(f"You don't have enough keys to unlock a new map ({self.haven.keys}/{self.haven.season+1}) ...", websocket)

    # choose difficulty
    # while map.name != "Endgame":
    #   difficulty = await choose_number("Choose a difficulty > ", websocket=websocket)
    #   if map.completed_difficulties[difficulty] == 0:
    #     map.difficulty = difficulty
    #     break
    #   else:
    #     await ws_input(colored("You've already completed this difficulty. Choose another.", "red"), websocket)

    return map

  async def play_setup(self, player_id=None, websocket=None):
    # Load Haven or create one if it doesn't exist
    if not os.path.exists("saves/haven.pkl") and not self.haven:
      starting_library = generate_starting_haven_library()
      self.haven = Haven(library=starting_library)
      # Also create the starting maps
      for i in range(4):
        map = map = Map(name=None, difficulty=i)
        map.save()
    elif not self.haven:
      with open("saves/haven.pkl", "rb") as f:
        self.haven = dill.load(f)

    # If endgame map doesn't exist create one and save it
    # if not os.path.exists("saves/maps/Endgame.pkl"):
    #   region_drafts = []
    #   factions = generate_faction_sets(n_sets=1, set_size=3, overlap=1)[0]
    #   base_enemy_composition = generate_endgame_enemy_composition(factions)
    #   region_draft = RegionDraft(combat_size=6, factions=factions, spell_pool=[],
    #                              n_spell_picks=0, n_enemy_picks=0, mandatory_enemysets=base_enemy_composition)
    #   region_drafts.append(region_draft)
    #   endgame_map = Map(name="Endgame", n_regions=1, region_drafts=region_drafts, difficulty=4)
    #   endgame_map.save()

    # Choose Character
    player = await self.choose_character(websocket)
    self.party_member_states[player_id] = PartyMemberState(player)
    player.id = player_id
    player.websocket = websocket

    await ws_input(f"Once all party members have joined, press enter.", websocket)

    # Do the character haven draft
    for pid in list(self.party_member_states.keys()):
      if pid == player.id:
        # await haven_library_draft(player, self)
        await haven_rolling_draft(player, self)
      await self.wait_for_teammates(player.id, f"{pid}-havenlibrarydraft")

    # Player 1 makes the choice about map
    if player_id == "p1":
      # Choose Map
      map = await self.choose_map(websocket)
      self.map = map
      map.init()
    await self.wait_for_teammates(player_id, "mapchoice")
    map = self.map # If you're not player 1 you need to pick up the map from the game state

    # if self.haven.runs % 2 == 0 and self.haven.runs > 0:
    #   # You must pay 2 keys to embark
    #   if self.haven.keys < 2:
    #     await ws_input(colored("You don't have enough keys to embark!", "red"), websocket)
    #     raise GameOver()
    #   self.haven.keys -= 2
    #   await ws_input(colored("You spend 2 keys to survive...", "green"), websocket)
    
    self.haven.runs += 1

    return player, map

  async def play_encounter(self, player, encounter, num_pages=3, page_capacity=3):
    await encounter.init_with_player(player)
    await encounter_draft(player, num_pages=num_pages, page_capacity=page_capacity)
    await self.encounter_phase(encounter)

  async def play(self, player_id, websocket=None):
    player, map = await self.play_setup(player_id=player_id, websocket=websocket)
    self.started = True
    await self.haven.pre_embark(player)
    for i, region_draft in enumerate(self.map.region_drafts[:self.run_length]):
      self.current_region_idx = i
      region_shop = self.map.region_shops[i]

      await ws_input(colored(f"You will fight {region_draft.combat_size} enemy sets next combat!", "red"), websocket)
      await region_draft.play(player, self)
      await region_shop.play(player, self) # FIXME: refactor to be a function, controller pattern
      encounter = self.generate_encounter(player, combat_size=region_draft.combat_size)
      await self.play_encounter(player, encounter, num_pages=3)

      # Persistent enemy sets
      for _ in range(self.map.num_escapes):
        escaped_enemyset = random.choice(encounter.enemy_sets)
        await ws_input(colored(f"You've escaped {escaped_enemyset.name}...", "green"), websocket)
        persistent_enemysets = [es for es in encounter.enemy_sets if es != escaped_enemyset]
        escaped_enemyset.level = 0

      player.pursuing_enemysets += persistent_enemysets
      stronger_enemysets = [random.choice(persistent_enemysets)]
      for enemyset in stronger_enemysets:
        enemyset.level_up()
        await ws_input(colored(f"{enemyset.name} still follows you, stronger...", "red"), websocket)

      await self.discovery_phase(player)

    if self.map.difficulty in [0, 1]:
      await draft_spell_for_haven(self, websocket)
    if self.map.difficulty in [3, 4]:
      await draft_spell_for_haven(self, websocket)
      await draft_spell_for_haven(self, websocket)
    if self.map.difficulty in [2, 5]:
      await draft_ritual_for_haven(self, websocket)


    # self.map.completed_difficulties[self.map.difficulty] += 1
    # self.map.difficulty += 1
    self.map.completed = True
    await self.end_run(player)
    await ws_print(self.haven.render(), websocket)


# helpers



