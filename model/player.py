from termcolor import colored
from copy import deepcopy
from collections import defaultdict
from model.combat_entity import CombatEntity
from model.spellbook import Spellbook, LibrarySpell
from model.item import EnergyPotion, SpellPotion
from utils import colorize, numbered_list, choose_obj
from generators import generate_library_spells
from drafting import reroll_draft_player_library

class Player(CombatEntity):
  def __init__(self, hp, name, spellbook, inventory, library, signature_spell=None, starting_inventory=None):
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
    self.library = library
    self.starting_inventory = starting_inventory or []
    self.request = None

    # 
    self.capacity = 5
    self.level = 0
    self.experience = 0
    self.character_class = "alchemist"
    self.defeats = 0

  @property
  def next_exp_milestone(self):
    next_level = self.level + 1
    total_exp_required = sum([i * 80 for i in range(1, next_level + 1)])
    return total_exp_required
  
  @property
  def level_progress_str(self):
    return f"{self.experience}/{self.next_exp_milestone}"

  def check_level_up(self):
    while self.experience >= self.next_exp_milestone:
      self.level += 1
      self.max_hp += 1
      self.hp += 1
      print(colored(f"You leveled up! You are now level {self.level} and your max hp is {self.max_hp}", "green"))
      if self.level % 3 == 1:
        energy_options = ["red", "blue", "gold"]
        print("\n".join(f"{i + 1} - {energy}" for i, energy in enumerate(energy_options)))
        chosen_energy = choose_obj(energy_options, colored("Choose an energy type tap into > ", "cyan"))
        self.starting_inventory.append(EnergyPotion(chosen_energy, 1))
        self.inventory.append(EnergyPotion(chosen_energy, 1))
      elif self.level % 3 == 2:
        print(self.render_library())
        chosen_spell = choose_obj(self.library, colored("Choose a spell to memorize > ", "cyan"))
        self.starting_inventory.append(SpellPotion(chosen_spell.spell))
        self.inventory.append(SpellPotion(chosen_spell.spell))
      elif self.level % 3 == 0:
        print(colored("ALCHEMIST CLASS FEATURE!", "green"))


  def init(self, spell_pool):
    starting_spellbook = Spellbook(pages=[])
    library = [LibrarySpell(self.signature_spell.spell, signature=True)] + generate_library_spells(size=3, spell_pool=spell_pool)
    inventory = deepcopy(self.starting_inventory)
    self.hp = self.max_hp
    self.clear_conditions()
    self.facing = "front"
    self.spellbook = starting_spellbook
    self.inventory = inventory
    self.library = library
    self.request = None
    reroll_draft_player_library(self, spell_pool)


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
                                         f"{colored(',' * self.defeats, 'red')}] "
                                         f"{self.name} ({'.' * self.time})")

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
    


