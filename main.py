import dill
from copy import deepcopy
from content.spells import spells
from content.enemies import enemy_sets
from model.encounter import Encounter
from model.player import Player
from model.combat_entity import CombatEntity
from model.spellbook import Spellbook, SpellbookPage, SpellbookSpell, LibrarySpell
from model.item import EnergyPotion
from model.map import Map
from termcolor import colored
from utils import colorize, choose_obj, choose_binary, command_reference, get_combat_entities, help_reference
from drafting import destination_draft, safehouse_library_draft
from sound_utils import play_sound

import random

STARTING_EXPLORED = 1
MAX_EXPLORE = 3
PASSAGE_EXPERIENCE = 3

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
    play_sound("player-death.mp3")
    print(self.player.render())
    input("Gained 30xp...")
    self.player.experience += 30
    input("Press enter to continue...")
    self.discovery_phase()
    self.player.wounds += 1
    self.player.check_level_up()
    # reset character back to starting layer
    self.map.regions[0].nodes[0][0].safehouse.resting_characters.append(self.player)
    self.end_run()
    self.save()
    raise GameOver()

  # Discovery

  def discovery_phase(self):
    play_sound("passage-discovery.mp3")
    while self.player.explored > 0:
      if random.random() < (self.player.explored * (1/MAX_EXPLORE)):
        self.player.explored -= MAX_EXPLORE
        self.player.experience += PASSAGE_EXPERIENCE
        if self.map.current_region.destination_node.boss:
          print(colored(f"You found a rest site and gained {PASSAGE_EXPERIENCE}xp and 1hp!", "green"))
          self.player.heal(1)
        else:
          self.map.current_region.destination_node.passages.append("pass")
          print(colored(f"You found a passage and gained {PASSAGE_EXPERIENCE}xp!", "green"))
        input(f"Press enter to continue exploring ({self.player.explored}/{MAX_EXPLORE}) ...")
      else:
        print(colored("Found nothing this time...", "blue"))
        break
    self.player.explored = STARTING_EXPLORED
    self.save()
      
  # Navigation

  def navigation_phase(self):
    play_sound("onwards.mp3")
    bag_of_passages = deepcopy(self.map.current_region.destination_node.passages)
    random.shuffle(bag_of_passages)
    passages_drawn = []
    passes = 0
    passes_required = 2
    for i in range(5):
      print(self.player.render())
      if len(bag_of_passages) == 0:
        break
      drawn_passage = bag_of_passages.pop(random.randint(0, len(bag_of_passages)-1))
      passages_drawn.append(drawn_passage)
      input("You find a passage. It leads to...")
      if drawn_passage == "pass":
        passes += 1
        print(colored(f"Deeper into the maze! ({passes}/{passes_required} progress).", "green"))
        if passes >= passes_required:
          input(colored("You come out the other side!", "cyan"))
          return True
      elif drawn_passage == "fail":
        fail_damage = (1 + self.map.current_region.corruption)
        print(colored(f"A trap! You take {fail_damage} damage. ({passes}/{passes_required} progress)", "red"))
        print(colored(f"You gained 2xp.", "green"))
        self.player.hp -= fail_damage
        self.player.experience += 2
      input(f"You press onwards... ({4 - i} turns remaining)")
    input(colored("You have failed to find the way through.", "red"))
    self.save()
    return False

  # Encounters

  def init_encounter(self, encounter):
    self.encounter = encounter
    self.encounter.player = self.player
    self.player.conditions[self.encounter.ambient_energy] += 1
    activable_rituals = [ritual for ritual in self.player.rituals if ritual.activable]
    encounter.rituals += activable_rituals
    for ritual in activable_rituals:
      ritual.progress = 0

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
        encounter.player.switch_face()
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
    while not encounter.overcome:
      self.run_encounter_round()
    self.encounter.render_combat()
    self.encounter.end_encounter()
    self.save()


  def play_route(self):
    while True:
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
    self.map.current_region.current_node = self.map.current_region.destination_node
    if encounter != "navigate":
      safehouse_library_draft(self.player, self.map.current_region.current_node.safehouse,
                              copies=3, spell_pool=self.map.current_region.spell_pool)
    else:
      safehouse_library_draft(self.player, self.map.current_region.current_node.safehouse,
                              copies=1, spell_pool=self.map.current_region.spell_pool)
    # Help out characters resting at this safehouse
    safehouse = self.map.current_region.current_node.safehouse
    for character in safehouse.resting_characters:
      character.heal(8)
      print(self.player.render_inventory())
      print(self.player.render_library())
      print(f"{character.name} has requested: \"{character.request}\"")
      spell_to_give = choose_obj(self.player.library, f"Give a spell to {character.name}? > ")
      if spell_to_give:
        character.library.append(LibrarySpell(spell_to_give.spell, copies=1))
      item_to_give = choose_obj(self.player.inventory, f"Give an item to {character.name}? > ")
      if item_to_give:
        character.inventory.append(item_to_give)
      self.player.experience += 20
    self.player.library = [ls for ls in self.player.library if ls.copies_remaining > 0 or ls.signature]
    self.save()
    # Choose to press onwards or rest
    onwards = choose_binary("Press onwards or rest?", choices=["onwards", "rest"])
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
    self.player.heal(2)
    self.player.check_level_up()

    self.player.request = input("Broadcast a message to fellow Delvers? >")
    safehouse.resting_characters.append(self.player)
    self.save()

  def end_run(self):
    self.map.end_run()
    self.save()

  def play(self):
    for i in range(len(self.map.regions)):
      while self.map.current_region.current_node.position[0] < len(self.map.current_region.nodes) - 1:
        onwards = self.play_route()
        if not onwards:
          self.rest_phase()
          self.end_run()
          return
      self.map.current_region_idx += 1

    print("--- END ---")
    self.end_run()

gs = GameState()
gs.init()
# gs.init(map_file="saves/map.pkl")
# gs.init(map_file="saves/map.pkl", character_file="saves/Kite.pkl")
gs.play()