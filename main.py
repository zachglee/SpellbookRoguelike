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
from utils import choose_obj, choose_str, command_reference, get_combat_entities, help_reference, numbered_list, ws_input, ws_print

STARTING_EXPLORED = 1

class GameOver(Exception):
  pass

class GameStateV2:
  def __init__(self, n_regions=4, websocket=None):
    self.map = Map(n_regions=n_regions)
    self.current_region_idx = 0
    self.player = None

    #
    self.show_intents = False
    self.run_length = None

    #
    self.websocket = websocket

  # Properties

  @property
  def current_region(self):
    return self.map.region_drafts[self.current_region_idx]

  # Admin

  def save(self):
    with open("saves/map.pkl", "wb") as f:
      dill.dump(self.map, f)
    with open(f"saves/{self.player.name}.pkl", "wb") as f:
      dill.dump(self.player, f)

  # Generators

  async def generate_new_character(self, spell_pool):
    await ws_print("Starting a new character...", self.websocket)
    signature_spell_options = generate_library_spells(2, spell_pool=spell_pool)
    await ws_print(numbered_list(signature_spell_options), self.websocket)
    chosen_spell = await choose_obj(signature_spell_options, colored("Choose signature spell > ", "red"), self.websocket)
    name = await ws_input("What shall they be called? > ", self.websocket)
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
    player.pursuing_enemysets = player.pursuing_enemysets[difficulty:] 
    encounter = Encounter([EnemyWave(encounter_enemysets)], player,
                          basic_items=self.current_region.basic_items,
                          special_items=self.current_region.special_items)
    return encounter

  # Game Phases

  async def handle_command(self, cmd, encounter, websocket=None):
    cmd_tokens = cmd.split(" ")
    try:
      if cmd == "die":
        self.player_death()
        return
      elif cmd == "debug":
        targets = get_combat_entities(self, cmd_tokens[1])
        for target in targets:
          await ws_print(target.__dict__, websocket)
        return
      elif cmd == "help":
        await command_reference(websocket=websocket)
      elif cmd in ["inventory", "inv", "i"]:
        await ws_print(encounter.player.render_inventory(), websocket)
        play_sound("inventory.mp3")
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
        await help_reference(subject, websocket=websocket)
        return
    except (KeyError, IndexError, ValueError, TypeError) as e:
      await ws_print(e, websocket)

    # If not a UI command, see if it can be handled as an encounter command
    await encounter.handle_command(cmd, websocket=websocket)

  async def run_encounter_round(self, encounter, websocket=None):
    while True:
      await encounter.render_combat(show_intents=self.show_intents, websocket=websocket)
      cmd = await ws_input("> ", websocket)
      if cmd == "done":
        encounter.end_player_turn()
        break
      await self.handle_command(cmd, encounter, websocket=websocket)

  async def encounter_phase(self, encounter):
    while not encounter.overcome:
      await self.run_encounter_round(encounter)
    await encounter.render_combat(websocket=self.websocket)
    encounter.end_encounter()
    self.save()

  def discovery_phase(self):
    play_sound("passage-discovery.mp3")
    explore_difficulty = 4
    discoveries = 0
    while self.player.explored > 0:
      if random.random() < (self.player.explored * (1/explore_difficulty)):
        self.player.explored -= explore_difficulty
        self.player.experience += explore_difficulty
        print(colored(f"Gained {explore_difficulty}xp.", "yellow"))
        self.player.gain_material(explore_difficulty)
        discoveries += 1
        input(f"Press enter to continue exploring ({self.player.explored}/{explore_difficulty}) ...")
      else:
        print(colored("Found nothing this time...", "blue"))
        break
    self.player.explored = STARTING_EXPLORED
    self.save()

  def player_death(self):
    if self.player.conditions["undying"] > 0:
      self.player.hp = 3
      self.player.conditions["undying"] -= 1
      return
    # player drops all their items in current region
    # for item in self.player.inventory:
    #   item.belonged_to = self.player.name
    # self.map.current_region.dropped_items += self.player.inventory
    self.player.inventory = []
    # death admin
    play_sound("player-death.mp3")
    print(self.player.render())
    input("Gained 30xp...")
    self.player.experience += 30
    input("Press enter to continue...")
    self.discovery_phase()
    self.player.wounds += 1
    
    # self.map.inactive_characters[self.player.name] = self.player
    self.end_run()
    self.save()
    raise GameOver()

  def end_run(self):
    self.map.end_run()
    self.player.archive_library_spells(copies_threshold=10)
    self.player.check_level_up()
    self.save()

  async def choose_character(self):
    character_choice = await ws_input("Choose a character ('new' to make a new character) > ", self.websocket)
    if character_choice == "new":
      player = await self.generate_new_character(self.map.region_drafts[0].spell_pool)
    else:
      character_file = f"saves/{character_choice}.pkl"
      with open(character_file, "rb") as f:
        player = dill.load(f)
    player.init()
    self.player = player
  
  def choose_map(self, map_file):
    if map_file and os.path.exists(map_file):
      with open(map_file, "rb") as f:
        self.map = dill.load(f)
    else:
      self.map = Map()
    self.map.init()

  async def play_setup(self, map_file=None):
    self.choose_map(map_file)
    await self.choose_character()
    self.run_length = 4

  async def play_encounter(self, encounter, websocket=None):
    encounter.init_with_player(self.player)
    await encounter_draft(self.player, num_pages=2, page_capacity=3, websocket=websocket)
    self.player.archive_library_spells()
    await self.encounter_phase(encounter, websocket=websocket)

  async def play(self, map_file=None):
    await self.play_setup(map_file=map_file)
    for i, region_draft in enumerate(self.map.region_drafts[:self.run_length]):
      self.current_region_idx = i
      region_shop = self.map.region_shops[i]

      await region_draft.play(self.player, self.websocket)
      await region_shop.play(self.player, self.websocket)
      encounter = self.generate_encounter(self.player, difficulty=2+region_draft.difficulty)
      await self.play_encounter(encounter, self.websocket)

      return encounter

      # Persistent enemy sets
      persistent_enemyset = random.choice(encounter.enemy_sets)
      persistent_enemyset.level_up()
      self.player.pursuing_enemysets.append(persistent_enemyset)
      await ws_print(colored(f"{persistent_enemyset.name} still follows you, stronger...", "red"), self.websocket)
      for enemyset in [es for es in encounter.enemy_sets if es is not persistent_enemyset]:
        enemyset.level = 0

      self.discovery_phase()

    # Now need to play the final combat with your backlog enemies?
    # NOTE: still untested
    # encounter = self.generate_encounter(self.player, difficulty=4)
    # self.play_encounter(encounter)
    self.end_run()


# helpers

# main
game_state = GameStateV2()
game_state.play()
# game_state.play(map_file="saves/map.pkl")



