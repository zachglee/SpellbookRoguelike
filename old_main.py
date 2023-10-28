import dill
from copy import deepcopy
from content.spells import spells
from content.enemies import enemy_sets
from generators import generate_library_spells
from model.encounter import Encounter
from model.spellbook import LibrarySpell
from model.old_map import Map
from termcolor import colored
from utils import colorize, choose_obj, choose_binary, command_reference, get_combat_entities, help_reference, numbered_list
from drafting import destination_draft, safehouse_library_draft
from sound_utils import play_sound

import random

STARTING_EXPLORED = 1
# MAX_EXPLORE = 4
# PASSAGE_EXPERIENCE = 4

class GameOver(Exception):
  pass

# --------

class GameState:
  def __init__(self):
    self.player = None
    self.map = Map(n_regions=3)
    self.encounter = None
    self.show_intents = False

  # save management
  def save(self):
    with open("saves/map.pkl", "wb") as f:
      dill.dump(self.map, f)

    with open(f"saves/{self.player.name}.pkl", "wb") as f:
      dill.dump(self.player, f)

  # MAIN FUNCTIONS
  
  # setup

  def init(self, map_file=None, character_file=None):
    if map_file:
      with open(map_file, "rb") as f:
        self.map = dill.load(f)

    loaded_character = None
    if character_file:
      with open(character_file, "rb") as f:
        loaded_character = dill.load(f)

    player = self.map.init(character=loaded_character)
    self.player = player
    self.save()

  # Ending
  def player_death(self):
    if self.player.conditions["undying"] > 0:
      self.player.hp = 3
      self.player.conditions["undying"] -= 1
      return
    # player drops all their items in current region
    for item in self.player.inventory:
      item.belonged_to = self.player.name
    self.map.current_region.dropped_items += self.player.inventory
    self.player.inventory = []
    # death admin
    play_sound("player-death.mp3")
    print(self.player.render())
    input("Gained 30xp...")
    self.player.experience += 30
    input("Press enter to continue...")
    self.discovery_phase()
    self.player.wounds += 1
    self.player.check_level_up()
    # # retain one spell
    # retain_choices = [spell for spell in self.player.library if not spell.signature]
    # print(numbered_list([spell for spell in retain_choices]))
    # retained_spell = choose_obj(self.player.library, "Choose a spell to retain: ")
    # retained_spell.copies_remaining = 2
    # self.player.library = [spell for spell in self.player.library if spell.signature
    #                        or spell is retained_spell]
    self.map.inactive_characters[self.player.name] = self.player
    self.end_run()
    self.save()
    raise GameOver()

  # Discovery

  def explorer_discovery(self):
    explore_difficulty = self.map.current_region.explore_difficulty
    if not self.map.current_region.destination_node.boss:
      self.map.current_region.destination_node.passages.append("pass")
      print(colored(f"You found a passage, and gained {explore_difficulty}xp!", "green"))

  def builder_discovery(self):
    explore_difficulty = self.map.current_region.explore_difficulty
    print(colored(f"Gained {explore_difficulty}xp.", "yellow"))
    self.player.gain_material(explore_difficulty)

  def scholar_discovery(self):
    explore_difficulty = self.map.current_region.explore_difficulty
    print(colored(f"You found a new spell, and gained {explore_difficulty}xp!", "cyan"))

  def discovery_phase(self):
    play_sound("passage-discovery.mp3")
    explore_difficulty = self.map.current_region.explore_difficulty
    discoveries = 0
    while self.player.explored > 0:
      if random.random() < (self.player.explored * (1/explore_difficulty)):
        self.player.explored -= explore_difficulty
        self.player.experience += explore_difficulty
        if self.player.character_class == "Explorer":
          self.explorer_discovery()
        elif self.player.character_class == "Builder":
          self.builder_discovery()
        elif self.player.character_class == "Scholar":
          self.scholar_discovery()
        discoveries += 1
        input(f"Press enter to continue exploring ({self.player.explored}/{explore_difficulty}) ...")
      else:
        print(colored("Found nothing this time...", "blue"))
        break
    # special scholar case
    if self.player.character_class == "Scholar":
      print(self.player.render_library())
      num_choices = min(4, discoveries)
      spell_choices = generate_library_spells(num_choices, spell_pool=self.map.current_region.spell_pool, copies=1)
      print("---\n" + numbered_list(spell_choices))
      choice = choose_obj(spell_choices, "Which spell have you been studying > ")
      if choice:
        self.player.library.append(choice)
        if discoveries >= 4:
          self.map.current_region.destination_node.safehouse.library.append(deepcopy(choice))
    self.player.explored = STARTING_EXPLORED
    self.save()
      
  # Navigation

  def navigation_phase(self):
    play_sound("onwards.mp3")
    destination_node = self.map.current_region.destination_node
    if "pass" in destination_node.passages:
      destination_node.passages.remove("pass")
      print(colored(f"Navigated successfully! Used up one passage, now {destination_node.pass_passages} remain...", "green"))
      return True
    else:
      return False

  # Encounters

  def init_encounter(self, encounter):
    self.encounter = encounter
    self.encounter.player = self.player
    self.player.conditions[self.encounter.ambient_energy] += 1
    activable_rituals = [ritual for ritual in self.player.rituals if ritual.activable]
    if activable_rituals:
      print(numbered_list(activable_rituals))
      chosen_ritual = choose_obj(activable_rituals, "Choose a ritual to activate: ")
      if chosen_ritual:
        encounter.rituals = [chosen_ritual]
        chosen_ritual.progress -= chosen_ritual.required_progress

  def handle_command(self, cmd):
    encounter = self.encounter
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
      elif cmd == "map":
        self.map.inspect()
        return
      elif cmd in ["inventory", "inv", "i"]:
        print(self.player.render_inventory())
        play_sound("inventory.mp3")
        return
      elif cmd in ["intent", "intents", "int"]:
        self.show_intents = not self.show_intents
        return
      elif cmd in ["ritual"]:
        print(self.map.render_active_ritual())
        print(self.player.render_rituals())
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

  def run_encounter_round(self):
    while True:
      self.encounter.render_combat(show_intents=self.show_intents)
      cmd = input("> ")
      if cmd == "done":
        self.encounter.end_player_turn()
        break
      self.handle_command(cmd)


  def encounter_phase(self):
    encounter = self.encounter
    # TODO: call a page choosing helper here
    while not encounter.overcome:
      self.run_encounter_round()
    self.encounter.render_combat()
    self.encounter.end_encounter()
    self.map.current_region.dropped_items += encounter.dropped_items
    self.save()

  # NOT CURRENTLY IN USE
  def heat_phase(self, node):
    # Take heat damage
    pass_damage = node.heat
    self.player.hp -= pass_damage
    if pass_damage:
      input(colored(f"The hostility of this place leaves its mark. You take {pass_damage} damage.", "red"))
    # do heat admin
    node.heat += 1
    node_layer = self.map.current_region.nodes[node.position[0]]
    non_destination_nodes = [n for n in node_layer if n != node]
    for n in [random.choice(non_destination_nodes) for _ in range(2)]:
      n.heat = max(0, n.heat - 1)
    print(colored(f"The heat of this node has increased to {node.heat}.", "red"))

  def play_route(self):
    while True:
      if self.map.current_region.current_node.position[0] == len(self.map.current_region.nodes) - 1:
        # if we're at the end of the region, progress to the next region
        if self.map.current_region_idx + 1 >= len(self.map.regions):
          return True
        self.map.current_region_idx += 1
        self.map.current_region.current_node = self.map.current_region.nodes[0][self.player.current_column]
        self.destination_node = None
      encounter = self.map.current_region.choose_route(self.player)
      if isinstance(encounter, Encounter):  
        self.init_encounter(encounter)
        destination_draft(self.player, self.map.current_region.destination_node)
        self.encounter_phase()
        self.discovery_phase()

        break
      elif encounter == "navigate":
        success = self.navigation_phase()
        if success:
          break
    # TODO REMOVE THIS AND THE heat_phase() func eventually if we don't bring it back
    # self.heat_phase(self.map.current_region.destination_node)
    # update the destination
    self.map.current_region.current_node = self.map.current_region.destination_node
    if not self.map.current_region.current_node.boss:
      self.player.current_column = self.map.current_region.current_node.position[1]
    if encounter != "navigate": # Fight case
      # self.player.material += self.map.current_region.current_node.reward_material
      print(colored(f"You gained {self.map.current_region.current_node.reward_material} material!", "yellow"))
      self.player.inventory += deepcopy(self.map.current_region.current_node.reward_items)
      print(colored(f"You gained the following items!", "green"))
      print(numbered_list(self.map.current_region.current_node.reward_items))
      safehouse_library_draft(self.player, self.map.current_region.current_node.safehouse,
                              copies=2, spell_pool=self.map.current_region.spell_pool)
    else: # Navigate case
      # progress rituals due to ambient energy
      for ritual in self.player.rituals:
        if ritual.energy_color == self.map.current_region.current_node.ambient_energy:
          ritual.progress += 1
        print(f"{ritual.name} progressed!")
        input(ritual.render())
        break
      safehouse_library_draft(self.player, self.map.current_region.current_node.safehouse,
                              copies=2, spell_pool=self.map.current_region.spell_pool)
    if not self.map.current_region.current_node.boss and self.player.character_class == "Builder":
        self.map.current_region.current_node.safehouse.build_phase(self.player)
    self.map.current_region.current_node.prompt_flavor(self.player, "fight" if isinstance(encounter, Encounter) else "navigate")
    # Help out characters resting at this safehouse
    safehouse = self.map.current_region.current_node.safehouse
    for character in safehouse.resting_characters:
      character.heal(5)
      print(self.player.render_library())
      print(f"{character.name} has requested: \"{character.request}\"")
      spell_to_give = choose_obj(self.player.library, f"Give a spell to {character.name}? > ")
      if spell_to_give:
        character.library.append(LibrarySpell(spell_to_give.spell, copies=1))
      print(self.player.render_inventory())
      item_to_give = choose_obj(self.player.inventory, f"Give an item to {character.name}? > ")
      if item_to_give:
        character.inventory.append(item_to_give)
        self.player.inventory.remove(item_to_give)
      self.player.experience += 20
    safehouse.inventory_draft_phase(self.player)
    # self.player.library = [ls for ls in self.player.library if ls.copies_remaining > 0 or ls.signature]
    self.player.archive_library_spells()
    self.save()

    # Choose to press onwards or rest
    if safehouse.restable:
      onwards = choose_binary("Press onwards?", choices=["onwards", "rest"])
    else:
      input("You press onwards...")
      onwards = True

    if onwards:
      print("Onwards...")
      play_sound("onwards.mp3")
      return True
    else:
      print("Resting...")
      return False

  def rest_phase(self):
    # take wounds and damage from corruption
    if self.map.current_region.corruption > 0:
      corruption_damage = self.map.current_region.corruption + self.player.wounds
      self.player.hp -= corruption_damage
      input(colored("The corruption of this place leaves its mark. "
                    f"You take {corruption_damage} damage.", "red"))

    safehouse = self.map.current_region.current_node.safehouse
    safehouse.resting_characters.append(self.player)
    self.player.heal(safehouse.rest_heal_amount)
    self.player.check_level_up()

    self.player.request = input("Broadcast a message to fellow Delvers? >")
    self.save()

  def prompt_log(self):
    self.map.render_log()
    log_entry = input(colored("Leave a log entry for your fellow players > ", "magenta"))
    self.map.log_entries.append((log_entry, self.player.name))
    self.save()

  def end_run(self):
    self.map.end_run()
    self.player.archive_library_spells(copies_threshold=10)
    self.prompt_log()
    self.save()

  def play(self):
    while self.map.current_region_idx < len(self.map.regions):
      onwards = self.play_route()
      if not onwards:
        self.rest_phase()
        self.end_run()
        return

    print("--- END ---")
    self.end_run()

gs = GameState()
# gs.init()
gs.init(map_file="saves/map.pkl")
# gs.init(map_file="saves/map.pkl", character_file="saves/Kite.pkl")
gs.play()