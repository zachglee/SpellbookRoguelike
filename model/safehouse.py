from termcolor import colored
import random
from utils import choose_binary, choose_idx, choose_obj, energy_colors, numbered_list
from model.item import EnergyPotion, SpellPotion
from model.spellbook import LibrarySpell

class Safehouse:
  def __init__(self, library):
    self.library = library
    self.resting_characters = []
    self.power = 1
    self.buildings = []
  
  @staticmethod
  def generate_safehouse(spell_pool):
    random.shuffle(spell_pool)
    library = spell_pool[:3]
    return Safehouse(library)

  def build_phase(self, player):
    print(self.render())
    power_cost = self.power + 1
    print(f"You have {player.material} material.")
    increase_power = choose_binary(colored(f"Would you like to increase power? (Costs {power_cost})", "yellow"))
    if increase_power:
      if player.material >= power_cost:
        player.material -= power_cost
        self.power += 1
        print(colored(f"power increased to {self.power}", "green"))
      else:
        print(colored("Not enough material!", "red"))

  def render(self):
    render_str = f"-------- SAFEHOUSE (power: {self.power}) --------\n"
    render_str += numbered_list(self.library)
    return render_str
