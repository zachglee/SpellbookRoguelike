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
from utils import colorize, choose_obj, choose_idx, get_combat_entities, choose_binary, numbered_list
from drafting import destination_draft, safehouse_library_draft

import random

STARTING_EXPLORED = 2
MAX_EXPLORE = 4

class GameOver(Exception):
  pass


# --------

class GameState:
  def __init__(self):
    self.player = None
    self.map = Map(n_regions=3)
    self.encounter = None

  # helpers

  def time_cost(self, cost=1):
    if (self.player.time - cost) >= 0:
      self.player.time -= cost
    else:
      raise ValueError(colored("Not enough time!", "red"))


  def cast(self, spell, cost_energy=True, cost_charges=True):
    if cost_charges:
      spell.charges -= 1
    if spell.spell[0:13] == "Producer: +1 ":
      color = spell.spell[13:].split(",")[0].lower()
      self.player.conditions[color] += 1
    elif cost_energy:
      if spell.spell[0:12] == "Consumer: 1 ":
        color = spell.spell[12:].split(":")[0].lower()
        self.player.conditions[color] -= 1
      elif spell.spell[0:11] == "Converter: ":
        conversion_tokens = spell.spell[11:].split(" ")[0:5]
        color_from = conversion_tokens[1].lower()
        color_to = conversion_tokens[4][:-1].lower()
        self.player.conditions[color_from] -= 1
        self.player.conditions[color_to] += 1

  def banish(self, target):
    idx = target.position(self.encounter)
    if target in self.encounter.back:
      banished = self.encounter.back.pop(idx)
      banished.spawned = False
    if target in self.encounter.front:
      banished = self.encounter.front.pop(idx)
      banished.spawned = False
    target.reset_conditions()

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
    print(self.player.render())
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
    while self.player.explored > 0:
      if random.random() < (self.player.explored * (1/MAX_EXPLORE)):
        self.map.current_region.destination_node.passages.append("pass")
        self.player.explored -= MAX_EXPLORE
        self.player.experience += 3
        print(colored("You found a passage and gained 3xp!", "green"))
        input(f"Press enter to continue exploring ({self.player.explored}/{MAX_EXPLORE}) ...")
      else:
        print(colored("Found nothing this time...", "blue"))
        break
    self.player.explored = STARTING_EXPLORED
    self.save()
      
  # Navigation

  def navigation_phase(self):
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
          self.map.current_region.destination_node.passages.append("fail") # make it harder for next time
          input(colored("You come out the other side!", "cyan"))
          return True
      elif drawn_passage == "fail":
        print(colored(f"A trap! You take 1 damage. ({passes}/{passes_required} progress)", "red"))
        print(colored(f"You gained 1xp.", "green"))
        self.player.hp -= (1 + self.map.current_region.corruption)
        self.player.experience += 1
      input(f"You press onwards... ({4 - i} turns remaining)")
    input(colored("You have failed to find the way through.", "red"))
    self.save()
    return False

  # Encounters

  def use_item(self, idx=None):
    if idx:
      item_idx = idx - 1
    else:
      item_idx = choose_idx(self.player.inventory, "use item > ")
    item = self.player.inventory[item_idx]
    item.use(self.encounter)
    self.player.inventory = [item for item in self.player.inventory if item.charges > 0]

  def init_encounter(self, encounter):
    self.encounter = encounter
    self.encounter.player = self.player
    self.player.conditions[self.encounter.ambient_energy] += 1
    activable_rituals = [ritual for ritual in self.player.rituals if ritual.activable]
    encounter.rituals += activable_rituals
    for ritual in activable_rituals:
      ritual.progress = 0

  def run_encounter_round(self):
    encounter = self.encounter
    while True:
        encounter.render_combat()
        cmd = input("> ")
        cmd_tokens = cmd.split(" ")
        try:
          if cmd == "done":
            encounter.end_player_turn()
            break
          elif cmd == "die":
            self.player_death()
          elif cmd == "win":
            encounter.turn = 10
          elif cmd == "map":
            self.map.inspect()
          elif cmd_tokens[0] == "experience":
            magnitude = int(cmd_tokens[1])
            self.player.experience += magnitude
          elif cmd_tokens[0] == "time":
            magnitude = int(cmd_tokens[1])
            self.time_cost(magnitude)
          elif cmd in ["res", "resources"]:
            print(encounter.player.render_resources())
          elif cmd in ["inventory", "inv", "i"]:
            print(self.player.render_inventory())
          elif cmd in ["ritual"]:
            print(self.map.render_active_ritual())
          elif cmd == "use":
            self.time_cost()
            self.use_item()
          elif cmd in ["explore", "x"]:
            self.time_cost()
            self.player.explored += 1
            print(colored(f"Something lies within these passages... (explored {self.player.explored}/{MAX_EXPLORE})", "blue"))
          elif cmd == "face":
            self.time_cost()
            encounter.player.switch_face()
          elif cmd == "face?":
            encounter.player.switch_face()
          elif cmd == "page":
            self.time_cost()
            encounter.player.spellbook.switch_page()
          elif cmd == "page?":
            encounter.player.spellbook.switch_page()
          elif cmd_tokens[0] == "recharge":
            if cmd_tokens[1] == "r":
              spell_idx = random.choice(range(len(self.player.spellbook.current_page.spells)))
            else:
              spell_idx = int(cmd_tokens[1]) - 1
            target = self.player.spellbook.current_page.spells[spell_idx]
            target.recharge()
          elif cmd_tokens[0] in ["cast", "ecast", "ccast"]:
            target = self.player.spellbook.current_page.spells[int(cmd_tokens[1]) - 1]
            self.time_cost()
            self.cast(target,
                      cost_energy=not cmd_tokens[0] == "ccast",
                      cost_charges=not cmd_tokens[0] == "ecast")
          elif cmd_tokens[0] == "fcast":
            target = self.player.spellbook.current_page.spells[int(cmd_tokens[1]) - 1]
            self.cast(target, cost_energy=False, cost_charges=False)
          elif cmd_tokens[0] == "call":
            magnitude = int(cmd_tokens[1])
            non_imminent_spawns = [es for es in self.encounter.enemy_spawns
                                   if es.turn > self.encounter.turn + 1]
            if non_imminent_spawns:
              sorted(non_imminent_spawns, key=lambda es: es.turn)[0].turn -= magnitude
          elif cmd_tokens[0] == "banish":
            targets = get_combat_entities(encounter, cmd_tokens[1])
            for target in targets:
              self.banish(target)
          elif cmd_tokens[0] == "damage" or cmd_tokens[0] == "d":
            targets = get_combat_entities(encounter, cmd_tokens[1])
            magnitude = int(cmd_tokens[2])
            for target in targets:
              self.player.attack(target, magnitude)
          elif cmd_tokens[0] == "suffer" or cmd_tokens[0] == "s":
            targets = get_combat_entities(encounter, cmd_tokens[1])
            magnitude = int(cmd_tokens[2])
            for target in targets:
              target.hp -= magnitude
          elif cmd_tokens[0] == "heal":
            targets = get_combat_entities(encounter, cmd_tokens[1])
            magnitude = int(cmd_tokens[2])
            for target in targets:
              target.hp += magnitude
          else:
            condition = cmd_tokens[0]
            targets = get_combat_entities(encounter, cmd_tokens[1])
            magnitude = int(cmd_tokens[2])
            for target in targets:
              target.conditions[condition] = (target.conditions[condition] or 0) + magnitude
              if condition == "enduring" and target.conditions["enduring"] == 0:
                target.conditions["enduring"] = None
              if condition == "durable" and target.conditions["durable"] == 0:
                target.conditions["durable"] = None
        except (KeyError, IndexError, ValueError, TypeError) as e:
          print(e)

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
      safehouse_library_draft(self.player, self.map.current_region.current_node.safehouse)
    self.save()
    onwards = choose_binary("Press onwards or rest?", choices=["onwards", "rest"])
    if onwards:
      print("Onwards...")
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
    self.player.hp += 3
    print("Healed 3 hp...")

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
        # Help out characters resting at this safehouse
        safehouse = self.map.current_region.current_node.safehouse
        for character in safehouse.resting_characters:
          character.hp += 6
          input(f"Healed {character.name} for 6 HP")
          print(self.player.render_library())
          print(f"{character.name} has requested: \"{character.request}\"")
          spell_to_give = choose_obj(self.player.library, f"Give a spell to {character.name}? > ")
          if spell_to_give is None:
            continue
          spell_to_give.copies_remaining -= 1
          character.library.append(LibrarySpell(spell_to_give.spell, copies=2))
        self.player.library = [ls for ls in self.player.library if ls.copies_remaining > 0 or ls.signature]
        self.save()
        if not onwards:
          self.rest_phase()
          self.end_run()
          return
      self.map.current_region_idx += 1

    print("--- END ---")
    self.end_run()

gs = GameState()
# gs.init()
gs.init(map_file="saves/map.pkl")
# gs.init(map_file="saves/map.pkl", character_file="saves/Barnabus.pkl")
gs.play()