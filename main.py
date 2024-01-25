import random
import dill
import os
from drafting import encounter_draft
from model.encounter import Encounter, EnemyWave
from model.map import BossMap, Map
from model.player import Player
from model.spellbook import LibrarySpell
from sound_utils import play_sound
from termcolor import colored
from generators import generate_faction_sets, generate_library_spells, generate_shop, generate_spell_pools
from model.region_draft import BossRegionDraft, RegionDraft
from content.enemy_factions import factions
from utils import party_members, choose_obj, choose_str, command_reference, get_combat_entities, help_reference, numbered_list, ws_input, ws_print

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
  def __init__(self, n_regions=4):
    self.map = None
    self.current_region_idx = 0
    self.player = None

    #
    self.show_intents = False
    self.run_length = n_regions
    self.started = False

    #
    # self.websocket = websocket

  # Properties

  @property
  def current_region(self):
    return self.map.region_drafts[self.current_region_idx]

  # Admin

  def save(self):
    self.map.save()
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
    # player.material = 0
    # death admin
    play_sound("player-death.mp3")
    await ws_print(player.render(), player.websocket)
    await ws_input("Gained 100xp...", player.websocket)
    player.experience += 100
    await self.discovery_phase(player)
    player.wounds += 1
    player.location = 0
    # player.stranded = True
    
    await self.end_run(player)
    # random.choice(self.map.region_drafts).stranded_characters.append(player)
    self.save()
    raise GameOver()

  async def end_run(self, player):
    self.map.end_run()
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
      # NOTE: Trying out making your signature spell be truly random
      # player = await self.generate_new_character(self.map.region_drafts[0].spell_pool, websocket)
      player = await self.generate_new_character(generate_spell_pools()[0], websocket)
    else:
      character_file = f"saves/characters/{character_choice}.pkl"
      with open(character_file, "rb") as f:
        player = dill.load(f)
    player.init()
    return player
  
  async def choose_map(self, player, websocket):
    existing_maps = load_maps_from_files()
    await ws_print(numbered_list(existing_maps), websocket)
    map_choice = await choose_obj(existing_maps, "Choose a map for your run (or type 'done' to start a new map) > ", websocket)
    if map_choice:
      map = map_choice
      if player.location != map.difficulty:
        traversing_maps = [existing_maps[i] for i in range(player.location, map.difficulty)]
        if all(m.passages > 0 for m in traversing_maps):
          player.location = map.difficulty
          for m in traversing_maps:
            m.passages -= 1
        else:
          await ws_print(colored("Not enough passages to get there!", "red"), websocket)
          return await self.choose_map(player, websocket)
    else:
      map = Map(name=None, n_regions=self.run_length)
      await ws_print(f"This new land is called... {colored(map.name, 'magenta')}", websocket)

    return map

  async def play_setup(self, player_id=None, websocket=None):
    player = await self.choose_character(websocket)
    map = await self.choose_map(player, websocket)
    self.map = map
    map.init(player)
    # self.player = player
    party_members[player_id] = player
    player.id = player_id
    player.websocket = websocket
    self.run_length = 4
    return player, map

  async def play_encounter(self, player, encounter, num_pages=2, page_capacity=3):
    await encounter.init_with_player(player)
    await encounter_draft(player, num_pages=num_pages, page_capacity=page_capacity)
    await self.encounter_phase(encounter)

  async def play(self, player_id, websocket=None):
    player, map = await self.play_setup(player_id=player_id, websocket=websocket)
    self.started = True
    for i, region_draft in enumerate(self.map.region_drafts[:self.run_length]):
      self.current_region_idx = i
      region_shop = self.map.region_shops[i]

      await ws_input(colored(f"You will fight {region_draft.combat_size} enemy sets next combat!", "red"), websocket)
      await region_draft.play(player)
      await region_shop.play(player)
      is_boss_encounter = isinstance(region_draft, BossRegionDraft)
      encounter = self.generate_encounter(player, combat_size=region_draft.combat_size,
                                          boss=is_boss_encounter)
      await self.play_encounter(player, encounter, num_pages=3 if is_boss_encounter else 2)

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

    # Generate a new map!
    num_keys = len([item for item in player.inventory if item.name == "Ancient Key"])
    player.experience += 50 * num_keys
    await ws_print(colored(f"You gained {50 * num_keys} experience from keys!", "green"), websocket)
    if self.map.explored == False and num_keys > 0:
      self.map.explored = True
      new_map = Map(name=None, n_regions=self.run_length, difficulty=self.map.difficulty + 1)
      new_map.save()
      await ws_input(f"You've discovered a new land... {colored(new_map.name, 'magenta')}", websocket)
    if num_keys >= 1:
      self.map.passages += 1
    # TO BE WORKSHOPPED
    # elif self.map.explored and num_keys == 3:
    #   # NOTE: Turn your grimoire into a real spellbook that is claimable by someone who also makes it to here.
    #   # There's only one copy of it and it gives you fully made pages to do stuff with. Collecting
    #   # a few of these spellbooks + your own will likely be necessary to make it through the eventual
    #   # endgame boss guantlet of 6-enemy combats, (9-12 levels between them) three of them in a row
    #   pass

    await self.end_run(player)


# helpers



