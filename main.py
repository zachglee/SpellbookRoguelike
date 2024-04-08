import asyncio
import random
import dill
import os
from drafting import encounter_draft, haven_library_draft
from model.encounter import Encounter, EnemyWave
from model.map import Map
from model.party_member_state import PartyMemberState
from model.player import Player
from model.spellbook import LibrarySpell
from sound_utils import play_sound, ws_play_sound
from termcolor import colored
from generators import generate_spell_pools
from model.haven import Haven
from utils import choose_obj, command_reference, get_combat_entities, help_reference, numbered_list, render_secrets_dict, ws_input, ws_print

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
      await asyncio.sleep(0.5)

  # Generators

  async def generate_new_character(self, spell_pool, websocket=None):
    await ws_print("Starting a new character...", websocket)
    # signature_spell_options = generate_library_spells(3, spell_pool=spell_pool)
    # await ws_print(numbered_list(signature_spell_options), websocket)
    # chosen_spell = await choose_obj(signature_spell_options, colored("Choose signature spell > ", "red"), websocket)
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
    encounter = Encounter([EnemyWave(encounter_enemysets)], player,
                          basic_items=self.current_region.basic_items,
                          special_items=self.current_region.special_items,
                          boss=boss)
    return encounter

  # Game Phases

  async def handle_command(self, cmd, encounter):
    cmd_tokens = cmd.split(" ")
    try:
      if cmd == "die":
        await self.player_death(encounter.player)
        return
      elif cmd == "sound":
        await ws_print("play_sound:apply-sharp.mp3", websocket=encounter.player.websocket)
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
      cmd = await ws_input("> ", encounter.player.websocket)
      if cmd == "done":
        await encounter.end_player_turn()
        break
      if cmd:
        await self.handle_command(cmd, encounter)

  async def encounter_phase(self, encounter):
    while not encounter.overcome:
      await self.run_encounter_round(encounter)
    await encounter.render_combat()
    await encounter.end_encounter()
    self.save()

  async def discovery_phase(self, player):
    await ws_play_sound("passage-discovery.mp3", player.websocket)
    await ws_print(colored(f"You explored a total of {player.explored} times.", "green"), player.websocket)
    player.explored = STARTING_EXPLORED
    self.save()

  async def player_death(self, player):
    if player.conditions["undying"] > 0:
      player.hp = 3
      player.conditions["undying"] -= 1
      return
    # player.material = 0
    # death admin
    await ws_play_sound("player-death.mp3", player.websocket)
    await ws_print(player.render(), player.websocket)
    await ws_input("Gained 100xp...", player.websocket)
    player.experience += 100
    await self.discovery_phase(player)
    await player.check_level_up()
    player.wounds += 1
    player.location = 0
    player.hp = 0
    # player.stranded = True
    
    await self.end_run(player)
    # random.choice(self.map.region_drafts).stranded_characters.append(player)
    self.save()
    raise GameOver()

  async def end_run(self, player):
    self.map.end_run()
    await player.memorize()
    await player.learn_rituals()

    # await ws_print(render_secrets_dict(player.secrets_dict), player.websocket)
    # chosen_faction = await choose_str(list(player.secrets_dict.keys()), "Choose a faction whose secrets to record > ", player.websocket)
    # if chosen_faction:
    #   self.haven.secrets_dict[chosen_faction] += player.secrets_dict[chosen_faction]
    for faction, secrets in player.secrets_dict.items():
      self.haven.secrets_dict[faction] += secrets

    player.age += 1
    num_keys = len([item for item in player.inventory if item.name == "Ancient Key"])
    player.inventory = []

    player.websocket = None
    self.save()

  async def choose_character(self, websocket):
    available_characters = []
    for fname in os.listdir("saves/characters"):
      with open(f"saves/characters/{fname}", "rb") as f:
        character = dill.load(f)
        if not character.stranded and character.supplies > 0:
          available_characters.append(character)
    await ws_print(numbered_list([c.name for c in available_characters]), websocket)
    character_choice = await ws_input("Choose a character ('new' to make a new character) > ", websocket)
    if character_choice == "new":
      # signature_spell_pool = [sp for sp in self.map.region_drafts[0].spell_pool # sum([rd.spell_pool for rd in self.map.region_drafts], [])
      #                         if sp.type in ["Producer", "Passive", "Converter"]]
      player = await self.generate_new_character([], websocket)
      # player = await self.generate_new_character(generate_spell_pools()[0], websocket)
    else:
      character_file = f"saves/characters/{character_choice}.pkl"
      with open(character_file, "rb") as f:
        player = dill.load(f)
    unchosen_characters = [c for c in available_characters if c != player]
    for character in unchosen_characters:
      character.heal(3)
    player.init()
    return player
  
  async def choose_map(self, websocket):
    existing_maps = load_maps_from_files()
    await ws_print(numbered_list(existing_maps), websocket)
    map_choice = await choose_obj(existing_maps, "Choose a map for your run (or type 'done' to start a new map) > ", websocket)
    if map_choice:
      map = map_choice
      await ws_print(f"You embark on {map.render()}...", websocket)
    else:
      map = Map(name=None, n_regions=self.run_length)
      await ws_print(f"This new land is called... {colored(map.name, 'magenta')}", websocket)

    # choose difficulty
    difficulty = int(await ws_input(f"Choose a difficulty > ", websocket))
    map.difficulty = difficulty

    return map

  async def play_setup(self, player_id=None, websocket=None):
    # if a Haven save file doesn't exist, make one
    print(os.path.exists("saves/haven.pkl"))
    print(self.haven)
    if not os.path.exists("saves/haven.pkl") and not self.haven:
      starting_library = []
      while len([ls for ls in starting_library if ls.spell.type == "Producer"]) < 2:
        starting_library = [LibrarySpell(sp) for sp in random.sample(generate_spell_pools(n_pools=1)[0], 10)]
      self.haven = Haven(library=starting_library)
    elif not self.haven:
      with open("saves/haven.pkl", "rb") as f:
        self.haven = dill.load(f)

    # Choose Character
    player = await self.choose_character(websocket)
    self.party_member_states[player_id] = PartyMemberState(player)
    player.id = player_id
    player.websocket = websocket

    # Do the character haven draft
    await haven_library_draft(player, self)

    # Player 1 makes the choice about map
    if player_id == "1":
      # Choose Map
      map = await self.choose_map(websocket)
      self.map = map
      map.init()
    await self.wait_for_teammates(player_id, "mapchoice")

    return player, map

  async def play_encounter(self, player, encounter, num_pages=3, page_capacity=3):
    await encounter.init_with_player(player)
    await encounter_draft(player, num_pages=num_pages, page_capacity=page_capacity)
    await self.encounter_phase(encounter)

  async def play(self, player_id, websocket=None):
    player, map = await self.play_setup(player_id=player_id, websocket=websocket)
    self.started = True
    await self.haven.pre_embark(player) # FIXME: make this not a method but a function (controller pattern)
    for i, region_draft in enumerate(self.map.region_drafts[:self.run_length]):
      self.current_region_idx = i
      region_shop = self.map.region_shops[i]

      await ws_input(colored(f"You will fight {region_draft.combat_size} enemy sets next combat!", "red"), websocket)
      await region_draft.play(player, self)
      await region_shop.play(player, self) # FIXME: refactor to be a function, controller pattern
      encounter = self.generate_encounter(player, combat_size=region_draft.combat_size)
      await self.play_encounter(player, encounter, num_pages=3)

      # Persistent enemy sets
      escaped_enemyset = random.choice(encounter.enemy_sets)
      await ws_input(colored(f"You've escaped {escaped_enemyset.name}...", "green"), websocket)
      persistent_enemysets = [es for es in encounter.enemy_sets if es != escaped_enemyset]
      player.pursuing_enemysets += persistent_enemysets
      stronger_enemysets = [random.choice(persistent_enemysets)]
      for enemyset in stronger_enemysets:
        enemyset.level_up()
        await ws_input(colored(f"{enemyset.name} still follows you, stronger...", "red"), websocket)
      escaped_enemyset.level = 0

      await self.discovery_phase(player)

    # End of run rewards
    num_keys = len([item for item in player.inventory if item.name == "Ancient Key"])
    player.experience += 50 * num_keys
    await ws_print(colored(f"You gained {50 * num_keys} experience from keys!", "green"), websocket)

    completed_difficulty = None
    if num_keys >= self.map.completed_difficulties[self.map.difficulty]:
      completed_difficulty = self.map.difficulty
      self.map.completed_difficulties[self.map.difficulty] += 1
      await ws_print(colored(f"You've completed difficulty {self.map.difficulty}!", "green"), websocket)

    if completed_difficulty in [0, 1]:
      # get a new spell for the haven
      await ws_print(self.haven.render(), websocket)
      choices = random.sample(self.map.region_drafts[0].spell_pool, 4)
      await ws_print("\n" + numbered_list(choices), websocket)
      chosen_spell = await choose_obj(choices, "Choose a spell to add to the haven library > ", websocket)
      self.haven.library.append(LibrarySpell(chosen_spell))
    if completed_difficulty == 2:
      # add a new ritual
      ritual_choices = [faction.ritual for faction in self.map.factions]
      await ws_print("\n" + numbered_list(ritual_choices), websocket)
      chosen_ritual = await choose_obj(ritual_choices, "Choose a ritual to add to the haven > ", websocket)
      self.haven.rituals.append(chosen_ritual)
    if completed_difficulty == 3:
      # get a new map
      new_map = Map(name=None, n_regions=self.run_length, difficulty=0)
      new_map.save()
      await ws_input(f"You've discovered a new land... {colored(new_map.name, 'magenta')}", websocket)

    await self.end_run(player)
    await ws_print(self.haven.render(), websocket)


# helpers



