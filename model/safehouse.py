from termcolor import colored
import random
from utils import choose_binary, choose_idx, choose_obj, choose_str, energy_colors, numbered_list
from model.item import EnergyPotion, SpellPotion
from model.spellbook import LibrarySpell

class Safehouse:
  def __init__(self, library):
    self.library = library
    self.resting_characters = []
    self.inventory = []
    self.heal_level = 0
    self.inventory_level = 0

    # progression

    self.restable = False
    self.rest_heal_amount = 0
    self.rest_recharge_amount = 0
    self.inventory_capacity = 0
  
  @property
  def level(self):
    return self.heal_level + self.inventory_level

  @staticmethod
  def generate_safehouse(spell_pool):
    random.shuffle(spell_pool)
    library = spell_pool[:3]
    return Safehouse(library)

  def level_up_heal(self):
    self.heal_level += 1
    self.rest_heal_amount += 1
    if self.heal_level == 1:
      self.restable = True

  def level_up_inventory(self):
    self.inventory_level += 1
    self.inventory_capacity += 1
    if self.inventory_level == 1:
      self.restable = True

  def level_up(self):
    level_type = choose_str(["heal", "inventory"], "choose which feature to level up > ")
    if level_type == "heal":
      self.level_up_heal()
    elif level_type == "inventory":
      self.level_up_inventory()
  
  def inventory_draft_phase(self, player):
    if self.inventory_capacity <= 0:
      return
    print(player.render_inventory())
    print(self.render())
    while (cmd := input("take or store > ")) != "done":
      cmd_tokens = cmd.split(" ")
      if cmd_tokens[0] == "take" and len(player.inventory) < player.inventory_capacity:
        taken = choose_obj(self.inventory, "Take which item from safehouse inventory? > ")
        if taken:
          player.inventory.append(taken)
          self.inventory.remove(taken)
      if cmd_tokens[0] == "store" and len(self.inventory) < self.inventory_capacity:
        stored = choose_obj(player.inventory, "Store which item in safehouse inventory? > ")
        if stored:
          player.inventory.remove(stored)
          self.inventory.append(stored)
      print(player.render_inventory())
      print(self.render())

  def build_phase(self, player):
    while True:
      print(self.render())
      level_cost = 10 + (4 * self.level)
      print(f"This safehouse is level {self.level}. You have {player.material} material.")
      increase_level = choose_binary(colored(f"Would you like to level up this safehouse? (Costs {level_cost})", "yellow"))
      if increase_level:
        if player.material >= level_cost:
          player.material -= level_cost
          self.level_up()
          print(colored(f"Level increased to {self.level}!", "green"))
        else:
          print(colored("Not enough material!", "red"))
      else:
        break

  def render(self):
    render_str = f"-------- SAFEHOUSE Lv.{self.level}) --------\n"
    render_str += "Library:\n"
    render_str += numbered_list(self.library)
    render_str += "\n"
    render_str += "Inventory:\n"
    render_str += numbered_list(self.inventory)
    return render_str
