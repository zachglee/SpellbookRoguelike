from termcolor import colored
import random
from utils import choose_idx, choose_obj, energy_colors, numbered_list
from model.item import EnergyPotion, SpellPotion
from model.spellbook import LibrarySpell

class Safehouse:
  def __init__(self, library):
    self.library = library
    self.player = None
    self.resting_characters = []
  
  @staticmethod
  def generate_safehouse(spell_pool):
    random.shuffle(spell_pool)
    library = spell_pool[:3]
    return Safehouse(library)

  def render(self):
    render_str = "-------- SAFEHOUSE --------\n"
    render_str += numbered_list(self.library)
    return render_str
