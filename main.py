import random
import dill
import os
from drafting import destination_draft, encounter_draft
from model.encounter import Encounter, EnemyWave
from model.map import Map
from model.player import Player
from model.spellbook import LibrarySpell
from sound_utils import play_sound
from termcolor import colored
from generators import generate_faction_sets, generate_library_spells, generate_shop, generate_spell_pools
from model.region_draft import RegionDraft
from content.items import minor_energy_potions, health_potions
from utils import party_members, choose_obj, choose_str, command_reference, get_combat_entities, help_reference, numbered_list, ws_input, ws_print

STARTING_EXPLORED = 1

class GameOver(Exception):
  pass

class GameStateV2:
  def __init__(self, n_regions=4):
    self.map = None
    self.current_region_idx = 0
    self.player = None

    #
    self.show_intents = False
    self.run_length = None
    self.started = False

    #
    # self.websocket = websocket

  # Properties

  @property
  def current_region(self):
    return self.map.region_drafts[self.current_region_idx]

  # Admin

  def save(self):
    with open(f"saves/maps/{self.map.name}.pkl", "wb") as f:
      dill.dump(self.map, f)
    for player in party_members.values():
      player.save()

  # Generators

  async def generate_new_character(self, spell_pool, websocket=None):
    await ws_print("Starting a new character...", websocket)
    signature_spell_options = generate_library_spells(3, spell_pool=spell_pool)
    await ws_print(numbered_list(signature_spell_options), websocket)
    chosen_spell = await choose_obj(signature_spell_options, colored("Choose signature spell > ", "red"), websocket)
    name = await ws_input("What shall they be called? > ", websocket)
    library = ([LibrarySpell(chosen_spell.spell, copies=3, signature=True)])
    player = Player.make(hp=30, name=name,
                    spellbook=None,
                    inventory=[],
                    library=library,
                    signature_spell=chosen_spell)
    return player
  
  def generate_encounter(self, player, difficulty=3):
    # generate the encounter
    random.shuffle(player.pursuing_enemysets)
    encounter_enemysets = player.pursuing_enemysets[0:difficulty]
    for enemyset in encounter_enemysets:
      enemyset.obscured = False
    player.pursuing_enemysets = player.pursuing_enemysets[difficulty:] 
    encounter = Encounter([EnemyWave(encounter_enemysets)], player,
                          basic_items=self.current_region.basic_items,
                          special_items=self.current_region.special_items)
    return encounter

  # Game Phases

  async def handle_command(self, cmd, encounter):
    cmd_tokens = cmd.split(" ")
    try:
      if cmd == "die":
        await self.player_death(encounter.player)
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
        play_sound("inventory.mp3")
        return
      elif cmd in ["ritual", "rituals", "rit"]:
        await ws_print(encounter.player.render_rituals(), encounter.player.websocket)
        return
      elif cmd in ["intent", "intents", "int"]:
        self.show_intents = not self.show_intents
        return
      elif cmd == "face?":
        encounter.player.switch_face(event=False)
        return
      elif cmd == "page?":
        encounter.player.spellbook.switch_page()
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
    play_sound("passage-discovery.mp3")
    await ws_print(colored(f"You explored a total of {player.explored} times.", "green"), player.websocket)
    player.explored = STARTING_EXPLORED
    self.save()

  async def player_death(self, player):
    if player.conditions["undying"] > 0:
      player.hp = 3
      player.conditions["undying"] -= 1
      return
    player.inventory = []
    player.material = 0
    # death admin
    play_sound("player-death.mp3")
    await ws_print(player.render(), player.websocket)
    await ws_input("Gained 30xp...", player.websocket)
    player.experience += 30
    await self.discovery_phase(player)
    player.wounds += 1
    player.stranded = True
    
    await self.end_run(player)
    random.choice(self.map.region_drafts).stranded_characters.append(player)
    self.save()
    raise GameOver()

  async def end_run(self, player):
    self.map.end_run()
    player.archive_library_spells(copies_threshold=10)
    await player.memorize()
    await player.learn_rituals()
    player.websocket = None
    self.save()

  async def choose_character(self, websocket):
    available_characters = []
    for fname in os.listdir("saves/characters"):
      with open(f"saves/characters/{fname}", "rb") as f:
        character = dill.load(f)
        if not character.stranded:
          available_characters.append(character)
    await ws_print(numbered_list([c.name for c in available_characters]), websocket)
    character_choice = await ws_input("Choose a character ('new' to make a new character) > ", websocket)
    if character_choice == "new":
      player = await self.generate_new_character(self.map.region_drafts[0].spell_pool, websocket)
    else:
      character_file = f"saves/characters/{character_choice}.pkl"
      with open(character_file, "rb") as f:
        player = dill.load(f)
    player.init()
    return player
  
  async def choose_map(self, websocket):
    existing_map_names = [fname.split(".")[0] for fname in os.listdir("saves/maps")]
    await ws_print(numbered_list(existing_map_names), websocket)
    map_choice = await ws_input("Choose a map for your run (A new name will create a new map) > ", websocket)
    if map_choice in existing_map_names:
      with open(f"saves/maps/{map_choice}.pkl", "rb") as f:
        map = dill.load(f)
    else:
      map = Map(name=map_choice)
    map.init()
    return map

  async def play_setup(self, player_id=None, websocket=None):
    map = await self.choose_map(websocket)
    self.map = map
    player = await self.choose_character(websocket)
    # self.player = player
    party_members[player_id] = player
    player.id = player_id
    player.websocket = websocket
    self.run_length = 4
    return player, map

  async def play_encounter(self, player, encounter):
    await encounter.init_with_player(player)
    await encounter_draft(player, num_pages=2, page_capacity=3)
    player.archive_library_spells()
    await self.encounter_phase(encounter)

  async def play(self, player_id, websocket=None):
    player, map = await self.play_setup(player_id=player_id, websocket=websocket)
    self.started = True
    for i, region_draft in enumerate(self.map.region_drafts[:self.run_length]):
      self.current_region_idx = i
      region_shop = self.map.region_shops[i]

      await ws_input(colored(f"You will fight {region_draft.difficulty} enemy sets next combat!", "red"), websocket)
      await region_draft.play(player)
      await region_shop.play(player)
      encounter = self.generate_encounter(player, difficulty=region_draft.difficulty)
      await self.play_encounter(player, encounter)

      # Persistent enemy sets
      stronger_enemyset = random.choice(encounter.enemy_sets)
      persistent_enemysets = [stronger_enemyset] + [es for es in encounter.enemy_sets if es.persistent]
      player.pursuing_enemysets += persistent_enemysets
      for enemyset in persistent_enemysets:
        enemyset.level_up()
        await ws_input(colored(f"{enemyset.name} still follows you, stronger...", "red"), websocket)
      for enemyset in [es for es in encounter.enemy_sets if es not in persistent_enemysets]:
        enemyset.level = 0

      await self.discovery_phase(player)

    await self.end_run(player)


# helpers



