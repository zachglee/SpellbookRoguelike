import dill
from content.spells import spells
from content.enemies import enemy_sets
from content.rest_actions import rest_actions, rerolls
from model.encounter import Encounter
from model.player import Player
from model.combat_entity import CombatEntity
from model.spellbook import Spellbook, SpellbookPage, SpellbookSpell
from model.item import EnergyPotion
from model.spell_draft import SpellDraft
# from model.rest_site import RestSite
# from model.route import Route
from model.map import Map
from termcolor import colored
from utils import colorize, choose_obj, choose_idx, get_combat_entities
from generators import generate_spell_pool, generate_library_spells
from drafting import destination_draft, reroll_draft_player_library

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
    self.map = Map(3, 3, generate_spell_pool(), enemy_sets[:12])
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
    with open("saves/main.pkl", "wb") as f:
      dill.dump(self.map, f)

  # MAIN FUNCTIONS
  
  # setup

  def init(self, file=None):
    starting_spellbook = Spellbook(pages=[])
    library = generate_library_spells(size=4)
    inventory = [EnergyPotion("red", 1), EnergyPotion("blue", 1), EnergyPotion("gold", 1)]
    self.player = Player(hp=30, name="Player", spellbook=starting_spellbook, inventory=inventory, library=library)
    reroll_draft_player_library(self.player)
    if file:
      with open(file, "rb") as f:
        self.map = dill.load(f)
    self.map.player = self.player
    self.save()

  # Ending
  def player_death(self):
    print(self.player.render())
    print(colored("You died.", "red"))
    print("What page from your spellbook will you preserve?")
    print(self.player.spellbook.render())
    page = choose_obj(self.player.spellbook.all_pages, colored("save a page > ", "red"))
    for spell in page.spells:
      spell.charges = 2
    # self.current_route.library.append(page)
    self.save()
    raise GameOver()

  # Drafting

  # def boss_draft_phase(self):
  #   self.spell_draft = SpellDraft(self.player, self.current_route.spell_pool)
  #   self.player.spellbook.archive += self.player.spellbook.pages
  #   self.player.spellbook.pages = []
  #   for _ in range(3):
  #     self.spell_draft.archive_draft_spellbook_page()

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

  def discovery_phase(self):
    pass # TODO find something to fill this in with
    # if random.random() < (self.player.explored * (1/MAX_EXPLORE)):
    #   self.current_route.safehouse.n_crafts = 3
    #   self.current_route.safehouse.player = self.player
    #   # crafting phase
    #   while self.current_route.safehouse.n_crafts > 0:
    #     print(self.current_route.safehouse.render())
    #     item = self.current_route.safehouse.craft(self.player)
    #     if item is None:
    #       break
    #     self.current_route.safehouse.inventory.append(item)
    #     self.current_route.safehouse.n_crafts -= 1

    #   # taking phase
    #   while len(self.player.inventory) < self.player.capacity:
    #     print(self.current_route.safehouse.render())
    #     item = self.current_route.safehouse.take()
    #     if item is None:
    #       break
    #     self.player.inventory.append(item)
    #     print(self.player.render_inventory())
    # else:
    #   print(colored("Found nothing this time...", "blue"))
    # self.player.explored = STARTING_EXPLORED
      

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
  
  # def play_route(self):
  #   self.init_encounter(self.current_route.normal_encounters.pop(0))
  #   if self.current_route.library:
  #     self.route_draft_phase()
  #   else:
  #     self.normal_draft_phase()
  #   self.normal_draft_phase()
  #   self.encounter_phase()
  #   self.discovery_phase()
  #   self.player.spellbook.archive.append(self.player.spellbook.pages.pop(0))

  #   for i in range (1):
  #     self.init_encounter(self.current_route.normal_encounters.pop(0))
  #     self.normal_draft_phase()
  #     self.encounter_phase()
  #     self.discovery_phase()
  #     self.player.spellbook.archive.append(self.player.spellbook.pages.pop(0))

  #   print(colored("!!!!!!!! THIS IS A BOSS ENCOUNTER !!!!!!!!", "red"))
  #   self.init_encounter(self.current_route.boss_encounters.pop(0))
  #   self.boss_draft_phase()
  #   self.encounter_phase()
  #   self.discovery_phase()

  def play(self):
    encounter = self.map.choose_route()
    self.init_encounter(encounter)
    destination_draft(self.player, self.map.destination_node)
    self.encounter_phase()

    # self.play_route()
    # self.finish_route()
    
    # self.play_route()
    # self.finish_route()

    self.save()

    print("YOU WIN!")

gs = GameState()
gs.init()
# gs.init("saves/main.pkl")
gs.play()