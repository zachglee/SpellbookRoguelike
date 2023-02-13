import dill
from content.spells import spells
from content.enemies import enemy_sets
from content.rest_actions import rest_actions, rerolls
from model.encounter import Encounter
from model.player import Player
from model.combat_entity import CombatEntity
from model.spellbook import Spellbook, SpellbookPage, SpellbookSpell
from model.spell_draft import SpellDraft
from model.rest_site import RestSite
from model.route import Route
from termcolor import colored
from utils import colorize, choose_obj, choose_idx, get_combat_entities
from generators import generate_routes

import random

MAX_EXPLORE = 5

class GameOver(Exception):
  pass


# --------

class GameState:
  def __init__(self):
    self.player = None
    self.routes = []
    self.current_route_idx = 0
    self.encounter = None
    self.spell_draft = None

  # helpers

  @property
  def current_route(self):
    return self.routes[self.current_route_idx]

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
      
  # save management
  def save(self):
    with open("saves/main.pkl", "wb") as f:
      dill.dump(self.routes, f)

  # MAIN FUNCTIONS
  
  # setup

  def init(self, file=None):
    starting_spellbook = Spellbook(pages=[])
    self.player = Player(hp=30, name="Player", spellbook=starting_spellbook, inventory=[])
    self.player.rerolls = 5
    if file:
      with open(file, "rb") as f:
        self.routes = dill.load(f)
    else:
      self.routes = generate_routes(3)
    # regenerate all the encounters from each route's enemy set pool
    for route in self.routes:
      route.generate_encounters()
    for page in route.library:
      for spell in page.spells:
        spell.charges = 2
    self.save()

  # Ending
  def player_death(self):
    print(self.player.render())
    print(colored("You died.", "red"))
    print("What page from your spellbook will you preserve?")
    print(self.player.spellbook.render())
    page = choose_obj(self.player.spellbook.pages + self.player.spellbook.archive, colored("save a page > ", "red"))
    for spell in page.spells:
      spell.charges = 2
    self.current_route.library.append(page)
    self.save()
    raise GameOver()

  # Drafting

  def route_draft_phase(self):
    self.current_route.library = [page for page in self.current_route.library if page.copy_count <= 4]
    print(f"-------- Route Library --------")
    for i, page in enumerate(self.current_route.library):
      print(f"Page {i + 1} (copied {page.copy_count} times):")
      print(page.render())
    drafted_page_idx = choose_idx(self.current_route.library, "draft a page > ")
    drafted_page = self.current_route.library[drafted_page_idx]
    self.player.spellbook.pages.append(drafted_page)
    # reduce max hp based on how many times this page was copied
    max_hp_costs = [0, 1, 3, 6, 10]
    self.player.max_hp -= max_hp_costs[page.copy_count]
    self.player.hp -= max_hp_costs[page.copy_count]


  def normal_draft_phase(self):
    self.spell_draft = SpellDraft(self.player, self.current_route.spell_pool)
    self.spell_draft.reroll_draft_spellbook_page()

  def boss_draft_phase(self):
    self.spell_draft = SpellDraft(self.player, self.current_route.spell_pool)
    self.player.spellbook.archive += self.player.spellbook.pages
    self.player.spellbook.pages = []
    for _ in range(3):
      self.spell_draft.archive_draft_spellbook_page()

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

  # DEPRECATED NOW since we no longer have formal rest sites
  def rest_phase(self):
    self.current_route.rest_site.player = self.player
    print(self.current_route.rest_site.render())
    while True:
      rest_action = self.current_route.rest_site.pick_rest_action()
      if rest_action is None:
        break
      self.take_rest_action(rest_action)
      print(self.current_route.rest_site.render())

  def discovery_phase(self):
    if random.random() < (self.player.explored * (1/MAX_EXPLORE)):
      # crafting phase
      n_crafts = 3
      while n_crafts > 0:
        item = self.current_route.safehouse.craft(self.player)
        if item is None:
          break
        self.player.inventory.append(item)
        n_crafts -= 1

      # taking phase
      while True:
        print(self.current_route.safehouse.render())
        item = self.current_route.safehouse.take()
        self.player.inventory.append(item)
    else:
      print(colored("Found nothing this time...", "blue"))
    self.player.explored = 1
      

  # Encounters

  def use_item(self):
    item_idx = choose_idx(self.player.inventory)
    item = self.player.inventory[item_idx]
    item.use(self.encounter)
    self.player.inventory = [item for item in self.player.inventory if item.charges <= 0]

  def init_encounter(self, encounter):
    self.encounter = encounter
    self.encounter.player = self.player
    ambient_energy = random.choice(["red", "blue", "gold"])
    self.player.conditions[ambient_energy] += 1
    print(colorize(f"!!!!!!!! Ambient Energy: {ambient_energy.title()} !!!!!!!!"))
    preview_enemy_set = random.choice(self.encounter.enemy_sets)
    print(f"!!!!!!!! Preview: {preview_enemy_set.name} !!!!!!!!")

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
          elif cmd == "site":
            print(self.rest_site.render())
          elif cmd_tokens[0] == "time":
            magnitude = int(cmd_tokens[1])
            self.time_cost(magnitude)
          elif cmd in ["loot", "loot?"]:
            print(encounter.player.render_loot())
          elif cmd == "echo":
            self.time_cost()
            spell = self.current_route.get_echo()
            if spell:
              print(colored("~~~ Echoes of a mage long dead ~~~", "blue"))
              spell.echoing = 2
              self.player.spellbook.current_page.spells.append(spell)
            else:
              print(colored("No echoes...", "blue"))
          elif cmd == "inventory":
            print(f"-------- INVENTORY --------")
            "\n".join(f"{i} - {item.render()}" for i, item in enumerate(self.player.inventory))
          elif cmd == "use":
            self.use_item()
          elif cmd == "explore":
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
    self.init_encounter(self.current_route.normal_encounters.pop(0))
    if self.current_route.library:
      self.route_draft_phase()
    else:
      self.normal_draft_phase()
    self.normal_draft_phase()
    self.encounter_phase()
    self.discovery_phase()
    self.player.spellbook.archive.append(self.player.spellbook.pages.pop(0))

    for i in range (1):
      self.init_encounter(self.current_route.normal_encounters.pop(0))
      self.normal_draft_phase()
      self.encounter_phase()
      self.discovery_phase()
      self.player.spellbook.archive.append(self.player.spellbook.pages.pop(0))

    self.init_encounter(self.current_route.boss_encounters.pop(0))
    self.boss_draft_phase()
    self.encounter_phase()
    self.discovery_phase()

  def finish_route(self):
    self.current_route.rest_site.library.append(Spellbook(self.player.spellbook.pages))
    self.player.spellbook.pages = []
    self.current_route_idx += 1
    # self.current_route.library += self.player.spellbook.archive

  def play(self):

    self.play_route()
    self.finish_route()
    
    self.play_route()
    self.finish_route()

    print("YOU WIN!")

gs = GameState()
# gs.init()
gs.init("saves/main.pkl")
gs.play()