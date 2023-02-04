from content.spells import spells
from content.enemies import enemy_sets
from content.rest_actions import rest_actions
from model.encounter import Encounter
from model.player import Player
from model.combat_entity import CombatEntity
from model.spellbook import Spellbook, SpellbookPage, SpellbookSpell
from model.spell_draft import SpellDraft
from model.rest_site import RestSite
from model.route import Route
from termcolor import colored
from utils import colorize

import random

# utilities and helpers

def get_combat_entities(enc, target_string) -> CombatEntity:
  if target_string == "p":
    return [enc.player]
  elif target_string == "f":
    return enc.front
  elif target_string == "b":
    return enc.back
  elif target_string[0] == "b":
    target_pos = int(target_string[1])
    return [enc.back[target_pos - 1]]
  elif target_string[0] == "f":
    target_pos = int(target_string[1])
    return [enc.front[target_pos - 1]]

# --------

class GameState:
  def __init__(self):
    # starting_inventory = [SpellbookSpell(random.choice(spells)) for _ in range(1)]
    # starting_page = SpellbookPage([SpellbookSpell(random.choice(spells)) for _ in range(4)])
    starting_spellbook = Spellbook(pages=[])
    self.player = Player(hp=30, name="Player", spellbook=starting_spellbook, inventory=[])
    
    random.shuffle(rest_actions)
    rest_site_actions = rest_actions[:4]
    rest_site = RestSite(rest_site_actions, None)
    self.route = Route([random.choice(enemy_sets) for _ in range(9)], rest_site)
    self.encounter = None
    self.spell_draft = None

  # helpers

  def time_cost(self, cost=1):
    if (self.player.time - cost) >= 0:
      self.player.time -= cost
    else:
      raise ValueError(colored("Not enough time!", "red"))


  def cast(self, spell):
    spell.charges -= 1
    if spell.spell[0:13] == "Producer: +1 ":
      color = spell.spell[13:].split(",")[0].lower()
      self.player.conditions[color] += 1
    elif spell.spell[0:12] == "Consumer: 1 ":
      color = spell.spell[12:].split(":")[0].lower()
      self.player.conditions[color] -= 1
    elif spell.spell[0:11] == "Converter: ":
      conversion_tokens = spell.spell[11:].split(" ")[0:5]
      color_from = conversion_tokens[1].lower()
      color_to = conversion_tokens[4][:-1].lower()
      self.player.conditions[color_from] -= 1
      self.player.conditions[color_to] += 1
      

  # MAIN FUNCTIONS
  
  # Drafting

  def normal_draft_phase(self):
    self.spell_draft = SpellDraft(self.player, spells)
    # self.spell_draft.draft_to_inventory(1)
    # self.spell_draft.draft_spellbook_page()
    self.spell_draft.reroll_draft_spellbook_page()

  def boss_draft_phase(self):
    self.spell_draft = SpellDraft(self.player, spells)
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

  def rest_phase(self):
    self.route.rest_site.player = self.player
    print(self.route.rest_site.render())
    while True:
      rest_action = self.route.rest_site.pick_rest_action()
      if rest_action is None:
        break
      self.take_rest_action(rest_action)
      print(self.route.rest_site.render())
      

  # Encounters

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
          elif cmd == "site":
            print(self.rest_site.render())
          elif cmd == "loot?":
            print(self.player.render_loot())
          elif cmd_tokens[0] == "time":
            magnitude = int(cmd_tokens[1])
            self.time_cost(magnitude)
          elif cmd in ["loot"]:
            print(encounter.player.render_loot())
          elif cmd == "explore":
            self.time_cost(magnitude)
            encounter.player.loot["Secrets"] += 1
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
          elif cmd_tokens[0] == "cast":
            target = self.player.spellbook.current_page.spells[int(cmd_tokens[1]) - 1]
            self.time_cost()
            self.cast(target)
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
              target.assign_damage(magnitude)
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
              target.conditions[condition] += magnitude
        except (KeyError, IndexError, ValueError, TypeError) as e:
          print(e)

  def encounter_phase(self):
    encounter = self.encounter
    while not encounter.overcome:
      self.run_encounter_round()
    self.encounter.render_combat()

    self.encounter.end_encounter()
    self.player.spellbook.archive.append(self.player.spellbook.pages.pop(0))
    
  def play(self):
    self.init_encounter(self.route.normal_encounters.pop(0))
    self.normal_draft_phase()
    self.normal_draft_phase()
    self.encounter_phase()

    self.init_encounter(self.route.normal_encounters.pop(0))
    self.normal_draft_phase()
    self.encounter_phase()

    # self.init_encounter(self.route.normal_encounters.pop(0))
    # self.normal_draft_phase()
    # self.encounter_phase()

    # TODO(zlee): implement rest site phase
    # - draft a recipe to start work on
    # - spend loot on existing recipes
    self.rest_phase()

    self.init_encounter(self.route.boss_encounter)
    self.boss_draft_phase()
    self.encounter_phase()

    print("YOU WIN!")

gs = GameState()
gs.play()