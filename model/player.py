from termcolor import colored
import random
from copy import deepcopy
from collections import defaultdict
from model.combat_entity import CombatEntity
from model.spellbook import Spellbook, LibrarySpell
from model.item import EnergyPotion, SpellPotion
from utils import colorize, numbered_list, choose_obj
from generators import generate_library_spells
from drafting import reroll_draft_player_library

class Player(CombatEntity):
  def __init__(self, hp, name, spellbook, inventory, library,
               signature_spell=None, signature_color=None, starting_inventory=None,
               aspiration=None):
    super().__init__(hp, name)
    self.spellbook = spellbook
    self.inventory = inventory
    # self.loot = defaultdict(lambda: 0)
    self.resources = defaultdict(lambda: 0)
    self.time = 4
    self.facing = "front"
    self.explored = 1

    #
    self.signature_spell = signature_spell
    self.signature_color = signature_color
    self.library = library
    self.starting_inventory = starting_inventory or []
    self.starting_inventory.append(EnergyPotion(self.signature_color, 1))
    self.request = None

    # 
    self.capacity = 5
    self.library_capacity = 8
    self.level = 0
    self.experience = 0
    self.aspiration = aspiration
    self.wounds = 0

  @property
  def next_exp_milestone(self):
    next_level = self.level + 1
    total_exp_required = sum([i * 50 for i in range(1, next_level + 1)])
    return total_exp_required
  
  @property
  def level_progress_str(self):
    return f"{self.experience}/{self.next_exp_milestone}"

  def memorize_spell(self):
    print(self.render_library())
    chosen_spell = choose_obj(self.library, colored("Choose a spell to memorize > ", "cyan"))
    if chosen_spell.signature:
      chosen_spell.max_copies_remaining += 1
    else:
      chosen_spell.signature = True
      chosen_spell.max_copies_remaining = 1

  def check_level_up(self):
    while self.experience >= self.next_exp_milestone:
      self.level += 1
      self.max_hp += 1
      self.hp += 1
      print(colored(f"You leveled up! You are now level {self.level} and your max hp is {self.max_hp}", "green"))
      if self.level == 1:
        self.starting_inventory.append(EnergyPotion(self.signature_color, 1))
        self.inventory.append(EnergyPotion(self.signature_color, 1))
        print("You have gained another innate energy of your signature color!")
      elif self.level == 2:
        self.memorize_spell()
      elif self.level == 3:
        energy_options = ["red", "blue", "gold"]
        print("\n".join(f"{i + 1} - {energy}" for i, energy in enumerate(energy_options)))
        chosen_energy = choose_obj(energy_options, colored("Choose an energy type tap into > ", "cyan"))
        self.starting_inventory.append(EnergyPotion(chosen_energy, 1))
        self.inventory.append(EnergyPotion(chosen_energy, 1))
      elif self.level == 4:
        self.memorize_spell()
      elif self.level == 5:
        self.memorize_spell()


  def init(self, spell_pool):
    starting_spellbook = Spellbook(pages=[])
    
    # recharge signature spells to max and get 1 more charge
    # for a random non-signature spell
    for library_spell in self.library:
      if library_spell.signature:
        library_spell.copies_remaining = library_spell.max_copies_remaining
    non_max_charges_spells = [spell for spell in self.library
                              if spell.copies_remaining < spell.max_copies_remaining]
    if non_max_charges_spells:
      random.choice(non_max_charges_spells).copies_remaining += 1

    inventory = deepcopy(self.starting_inventory)
    self.hp = self.max_hp
    self.clear_conditions()
    self.facing = "front"
    self.spellbook = starting_spellbook
    self.inventory = inventory
    self.request = None


  def switch_face(self):
    if self.facing == "front":
      self.facing = "back"
    elif self.facing == "back":
      self.facing = "front"
    else:
      raise ValueError(f"Facing is: {self.facing}")

  def render(self):
    entity_str = super().render()
    return entity_str.replace(self.name, f"[{self.level_progress_str}"
                                         f"{colored(',' * self.wounds, 'red')}] "
                                         f"{self.name}, {self.aspiration} ({'.' * self.time})")

  def render_resources(self):
    resource_strs = [f"- {k}: {v}" for k, v in self.resources.items()]
    resources_str = "\n".join(resource_strs)
    return colorize(resources_str)
  
  def render_inventory(self):
    render_str = "-------- INVENTORY --------\n"
    render_str += numbered_list(self.inventory)
    return render_str
  
  def render_library(self):
    render_str = "-------- PLAYER LIBRARY --------\n"
    render_str += numbered_list(self.library)
    return render_str
    


