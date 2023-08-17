from termcolor import colored
import random
from utils import choose_binary, choose_idx, choose_obj, energy_colors, numbered_list
from model.item import EnergyPotion, SpellPotion
from model.spellbook import LibrarySpell

class Safehouse:
  def __init__(self, library):
    self.library = library
    self.resting_characters = []
    self.inventory = []
    self.level = 0

    # progression
    self.restable = False
    self.rest_heal_amount = 0
    self.rest_recharge_amount = 0
    self.inventory_capacity = 0
  
  @staticmethod
  def generate_safehouse(spell_pool):
    random.shuffle(spell_pool)
    library = spell_pool[:3]
    return Safehouse(library)

  def level_up(self):
    self.level += 1
    if self.level == 1:
      self.restable = True
      self.rest_heal_amount = 2
      print(colored("You can now rest at this safehouse!", "green"))
    elif self.level == 2:
      self.rest_heal_amount = 3
      print(colored(f"You will now heal {self.rest_heal_amount}hp when you rest here!", "green"))
    elif self.level == 3:
      self.inventory_capacity = 1
      print(colored(f"You can now store 1 item in this safehouse!", "green"))
    elif self.level == 4:
      self.rest_recharge_amount = 1
      print(colored(f"You will now recharge 1 spell copy when you rest here!", "green"))
    elif self.level == 5:
      self.rest_heal_amount = 5
      print(colored(f"You will now heal {self.rest_heal_amount}hp when you rest here!", "green"))
    elif self.level == 6:
      self.inventory_capacity = 2
      print(colored(f"You can now store 2 items in this safehouse!", "green"))
    elif self.level == 7:
      self.rest_recharge_amount = 2
      print(colored(f"You will now recharge 2 spell copies when you rest here!", "green"))
  
  def inventory_draft_phase(self, player):
    if self.inventory_capacity <= 0:
      return
    while (cmd := input("take or store > ")) != "done":
      print(player.render_inventory())
      print(self.render())
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
    print(self.render())
    level_cost = 8 + (2 * self.level)
    print(f"This safehouse is level {self.level}. You have {player.material} material.")
    increase_level = choose_binary(colored(f"Would you like to level up this safehouse? (Costs {level_cost})", "yellow"))
    if increase_level:
      if player.material >= level_cost:
        player.material -= level_cost
        self.level_up()
        print(colored(f"Level increased to {self.level}!", "green"))
      else:
        print(colored("Not enough material!", "red"))

  def render(self):
    render_str = f"-------- SAFEHOUSE Lv.{self.level}) --------\n"
    render_str += "Library:\n"
    render_str += numbered_list(self.library)
    render_str += "\n"
    render_str += "Inventory:\n"
    render_str += numbered_list(self.inventory)
    return render_str
