import random
import dill
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
from utils import choose_obj, choose_str, command_reference, get_combat_entities, help_reference, numbered_list

STARTING_EXPLORED = 1

class GameStateV2:
  def __init__(self, n_regions=4):
    self.map = Map(n_regions=n_regions)
    self.current_region_idx = 0
    self.player = None

    #
    self.show_intents = False
    self.run_length = None

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

  def generate_new_character(self, spell_pool):
    print("Starting a new character...")
    signature_spell_options = generate_library_spells(2, spell_pool=spell_pool)
    print(numbered_list(signature_spell_options))
    chosen_spell = choose_obj(signature_spell_options, colored("Choose signature spell > ", "red"))
    name = input("What shall they be called? > ")
    library = ([LibrarySpell(chosen_spell.spell, copies=3, signature=True)])
    player = Player(hp=30, name=name,
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

  def handle_command(self, cmd, encounter):
    cmd_tokens = cmd.split(" ")
    try:
      if cmd == "die":
        self.player_death()
        return
      elif cmd == "debug":
        targets = get_combat_entities(self, cmd_tokens[1])
        for target in targets:
          print(target.__dict__)
        return
      elif cmd == "help":
        command_reference()
      elif cmd in ["inventory", "inv", "i"]:
        print(encounter.player.render_inventory())
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
        help_reference(subject)
        return
    except (KeyError, IndexError, ValueError, TypeError) as e:
      print(e)

    # If not a UI command, see if it can be handled as an encounter command
    encounter.handle_command(cmd)

  def run_encounter_round(self, encounter):
    while True:
      encounter.render_combat(show_intents=self.show_intents)
      cmd = input("> ")
      if cmd == "done":
        encounter.end_player_turn()
        break
      self.handle_command(cmd, encounter)

  def encounter_phase(self, encounter):
    while not encounter.overcome:
      self.run_encounter_round(encounter)
    encounter.render_combat()
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

  def choose_character(self):
    character_choice = input("Choose a character ('new' to make a new character) > ")
    if character_choice == "new":
      player = self.generate_new_character(self.map.region_drafts[0].spell_pool)
    else:
      character_file = f"saves/{character_choice}.pkl"
      with open(character_file, "rb") as f:
        player = dill.load(f)
    player.init()
    self.player = player
  
  def choose_map(self, map_file):
    if map_file:
      with open(map_file, "rb") as f:
        self.map = dill.load(f)
      self.map.init()

  def play_setup(self, map_file=None):
    self.choose_map(map_file)
    self.choose_character()
    self.run_length = int(input("How many regions are you playing for? > "))

  def play_encounter(self, encounter):
    encounter.init_with_player(self.player)
    encounter_draft(self.player, encounter, num_pages=2, page_capacity=3)
    self.player.archive_library_spells()
    self.encounter_phase(encounter)

  def play(self, map_file=None):
    self.play_setup()
    for i, region_draft in enumerate(self.map.region_drafts[:self.run_length]):
      self.current_region_idx = i
      region_shop = self.map.region_shops[i]

      region_draft.play(self.player)
      region_shop.play(self.player)
      encounter = self.generate_encounter(self.player, difficulty=2+region_draft.difficulty)

      self.play_encounter(encounter)

      # Persistent enemy sets
      persistent_enemyset = random.choice(encounter.enemy_sets)
      persistent_enemyset.level_up()
      self.player.pursuing_enemysets.append(persistent_enemyset)
      print(colored(f"{persistent_enemyset.name} still follows you, stronger...", "red"))

      self.discovery_phase()

    # Now need to play the final combat with your backlog enemies?
    # NOTE: still untested
    encounter = self.generate_encounter(self.player, difficulty=4)
    self.play_encounter(encounter)


# helpers

# main
game_state = GameStateV2()
# game_state.play()
game_state.play(map_file="saves/map.pkl")



