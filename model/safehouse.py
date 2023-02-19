from termcolor import colored
import random
from utils import choose_idx, choose_obj, energy_colors, numbered_list
from model.item import EnergyPotion, SpellPotion
from model.spellbook import LibrarySpell

class Safehouse:
  def __init__(self, library):
    self.library = library
    self.player = None
  
  @staticmethod
  def generate_safehouse(spell_pool):
    random.shuffle(spell_pool)
    library = spell_pool[:3]
    return Safehouse(library)

  def render(self):
    render_str = "-------- SAFEHOUSE --------\n"
    render_str += numbered_list(self.library)
    return render_str

# class Safehouse:
#   def __init__(self):
#     self.inventory = []
#     self.player = None
#     self.n_crafts = 3
  
#   def craft(self, player):
#     while True:
#       try:
#         cmd = input(colored("craft an item > ", "yellow"))
#         if cmd in energy_colors:
#           craft_cost = {f"{cmd.title()} Essence": 2}
#           crafted_item = EnergyPotion(cmd, 1)
#         elif cmd == "spell":
#           print(player.spellbook.render())
#           spell = choose_obj(player.spellbook.spells, colored("spell to bottle > ", "blue"))
#           if spell.charges <= 0: raise ValueError("Spell has no more charges.")
#           craft_cost = {"Bounties": 0}
#           crafted_item = SpellPotion(spell.spell)
#         elif cmd == "done":
#           return None
#         else:
#           raise ValueError("Invalid command input")
#         # check if the player has the resources
#         if any((self.player.loot[k] - v) < 0 for k, v in craft_cost.items()):
#           print(colored("You don't have the resources to craft this item.", "red"))
#         else:
#           if isinstance(crafted_item, SpellPotion): spell.charges -= 1
#           for k, v in craft_cost.items():
#             self.player.loot[k] -= v
#           print(f"Crafted: {crafted_item.render()}")
#           return crafted_item
#       except (ValueError, TypeError, IndexError) as e:
#         print(e)

#   def take(self):
#     take_idx = choose_idx(self.inventory, colored("take an item > ", "red"))
#     if take_idx is None:
#       return None
#     take_item = self.inventory.pop(take_idx)
#     return take_item

#   def render(self):
#     render_str = f"-------- Safehouse Inventory ({self.n_crafts} crafts) --------\n"
#     render_str += numbered_list(self.inventory)
#     render_str += "\n-------- Player Loot --------\n"
#     render_str += self.player.render_loot()
#     return render_str
