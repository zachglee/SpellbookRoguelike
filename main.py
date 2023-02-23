import dill
from copy import deepcopy
from content.spells import spells
from content.enemies import enemy_sets
from model.encounter import Encounter
from model.player import Player
from model.combat_entity import CombatEntity
from model.spellbook import Spellbook, SpellbookPage, SpellbookSpell
from model.item import EnergyPotion
from model.spell_draft import SpellDraft
from model.map import Map
from termcolor import colored
from utils import colorize, choose_obj, choose_idx, get_combat_entities, choose_binary
from generators import generate_spell_pool, generate_library_spells
from drafting import destination_draft, reroll_draft_player_library, safehouse_library_draft

import random

STARTING_EXPLORED = 2
MAX_EXPLORE = 6

class GameOver(Exception):
  pass


# --------

class GameState:
  def __init__(self):
    self.player = None
    random.shuffle(enemy_sets)
    self.map = Map(3, 3, generate_spell_pool(), enemy_sets[:10])
    self.encounter = None
    self.spell_draft = None

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

  # save management
  def save(self):
    with open("saves/map.pkl", "wb") as f:
      dill.dump(self.map, f)
    with open("saves/player.pkl", "wb") as f:
      dill.dump(self.player, f)

  # MAIN FUNCTIONS
  
  # setup

  def init(self, map_file=None, player_file=None):
    if map_file:
      with open(map_file, "rb") as f:
        self.map = dill.load(f)
    self.map.current_node = random.choice(self.map.nodes[0])
    print(self.map.render())
    input("Press enter to continue...")

    if player_file:
      with open(player_file, "rb") as f:
        self.player = dill.load(f)
    else:
      self.player = Player(hp=30, name="Player",
                           spellbook=None,
                           inventory=[],
                           library=[],
                           signature_spell=generate_library_spells(1)[0])
    self.player.init()
    self.map.player = self.player
    self.save()

  # Ending
  def player_death(self):
    print(self.player.render())
    print(colored("You died. Lose half your explore.", "red"))
    input("Press enter to continue...")
    self.player.explored = int(self.player.explored / 2)
    self.discovery_phase()
    self.save()
    raise GameOver()

  # Resting

  def take_rest_action(self, rest_action):
    # check cost
    # post_cost_loot = {k: v - rest_action.cost[k] for k, v in self.player.loot}
    if any((self.player.loot[k] - v) < 0 for k, v in rest_action.cost.items()):
      print(colored("You don't have the resources to take this action.", "red"))
      return
    rest_action.effect(self)
    for k, v in rest_action.cost.items():
      self.player.loot[k] -= v

  # Discovery

  def discovery_phase(self):
    while self.player.explored > 0:
      if random.random() < (self.player.explored * (1/MAX_EXPLORE)):
        self.map.destination_node.passages.append("pass")
        self.player.explored -= MAX_EXPLORE
        print(colored("You found a passage!", "green"))
        input(f"Press enter to continue exploring ({self.player.explored}/{MAX_EXPLORE}) ...")
      else:
        print(colored("Found nothing this time...", "blue"))
        break
    self.player.explored = STARTING_EXPLORED
      
  # Navigation

  def navigation_phase(self):
    bag_of_passages = deepcopy(self.map.destination_node.passages)
    passages_drawn = []
    passes = 0
    passes_required = 2
    for i in range(5):
      print(self.player.render())
      drawn_passage = bag_of_passages.pop(random.randint(0, len(bag_of_passages)-1))
      passages_drawn.append(drawn_passage)
      input("You find a passage. It leads to...")
      if drawn_passage == "pass":
        passes += 1
        print(colored(f"Deeper into the maze! ({passes}/{passes_required} progress).", "green"))
        if passes > passes_required:
          input(colored("You come out the other side!", "cyan"))
          return True
      elif drawn_passage == "fail":
        print(colored(f"A trap! You take 1 damage. ({passes}/{passes_required} progress)", "red"))
        self.player.hp -= 1
      input(f"You press onwards... ({4 - i} turns remaining)")
    input(colored("You have failed to find the way through.", "red"))
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
          elif cmd == "site":
            print(self.rest_site.render())
          elif cmd_tokens[0] == "time":
            magnitude = int(cmd_tokens[1])
            self.time_cost(magnitude)
          elif cmd in ["loot", "loot?"]:
            print(encounter.player.render_loot())
          elif cmd in ["inventory", "inv", "i"]:
            print(self.player.render_inventory())
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
            target = self.player.spellbook.current_page.spells[int(cmd_tokens[1]) - 1]
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

  def play_route(self):
    while True:
      encounter = self.map.choose_route(self.player)
      if isinstance(encounter, Encounter):  
        self.init_encounter(encounter)
        destination_draft(self.player, self.map.destination_node)
        self.encounter_phase()
        self.discovery_phase()
        break
      elif encounter == "navigate":
        success = self.navigation_phase()
        if success:
          break
    self.map.current_node = self.map.destination_node
    safehouse_library_draft(self.player, self.map.current_node.safehouse)

  def play(self):

    for i in range(4):
      self.play_route()

    self.save()

    print("YOU WIN!")

gs = GameState()
# gs.init()
gs.init(map_file="saves/map.pkl", player_file="saves/player.pkl")
gs.play()