from termcolor import colored
import random
from copy import deepcopy
from collections import defaultdict
from model.combat_entity import CombatEntity
from model.spellbook import Spellbook
from model.item import EnergyPotion, MeleeWeapon
from utils import choose_binary, colorize, numbered_list, choose_obj, energy_colors
from sound_utils import play_sound
from content.rituals import rituals
from content.items import starting_weapons
from content.enemy_factions import all_special_items
from model.event import Event

class Player(CombatEntity):
  def __init__(self, hp, name, spellbook, inventory, library,
               signature_spell=None, signature_color=None, starting_inventory=None,
               aspiration=None, starting_weapon=None):
    super().__init__(hp, name)
    self.spellbook = spellbook
    self.inventory = inventory
    self.resources = defaultdict(lambda: 0)
    self.rituals = []
    self.time = 4
    self.facing = "front"
    self.explored = 1

    #
    self.signature_spell = signature_spell
    self.signature_color = signature_color
    self.library = library
    self.starting_inventory = starting_inventory or []
    self.starting_inventory.append(EnergyPotion(self.signature_color, 1))
    if starting_weapon:
      self.starting_inventory.append(starting_weapon)
    self.request = None

    # 
    self.capacity = 5
    self.library_capacity = 10
    self.level = 0
    self.experience = 0
    self.aspiration = aspiration
    self.wounds = 0
    self.seen_items = []

  def total_energy(self, colors=energy_colors):
    player_energy = sum(self.conditions[color] for color in colors)
    return player_energy

  @property
  def next_exp_milestone(self):
    next_level = self.level + 1
    total_exp_required = 50 + sum([i * 30 for i in range(1, next_level + 1)])
    return total_exp_required
  
  @property
  def level_progress_str(self):
    return f"{self.experience}/{self.next_exp_milestone}"

  def spend_time(self, cost=1):
    if (self.time - cost) >= 0:
      self.time -= cost
    else:
      raise ValueError(colored("Not enough time!", "red"))

  def memorize_spell(self):
    print(self.render_library())
    chosen_spell = choose_obj(self.library, colored("Choose a spell to memorize > ", "cyan"))
    if chosen_spell.signature:
      chosen_spell.max_copies_remaining += 1
    else:
      chosen_spell.signature = True
      chosen_spell.max_copies_remaining = 1

  def learn_ritual(self):
    random.shuffle(rituals)
    ritual_choices = rituals[0:3]
    print(numbered_list(ritual_choices))
    chosen_ritual = choose_obj(ritual_choices, colored("Choose a ritual to learn > ", "cyan"))
    self.rituals.append(deepcopy(chosen_ritual))

  def gain_signature_item(self):
    seen_rare_items = [item for item in self.seen_items if item.rare]
    random.shuffle(seen_rare_items)
    signature_item_choices = seen_rare_items[0:3]
    if len(signature_item_choices) == 0:
      signature_item_choices = [random.choice(all_special_items)]
    print(numbered_list(signature_item_choices))
    chosen_item = choose_obj(signature_item_choices, colored("Choose a signature item > ", "cyan"))
    self.inventory.append(deepcopy(chosen_item))
    self.starting_inventory.append(deepcopy(chosen_item))

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
        self.learn_ritual()
      elif self.level == 4:
        self.memorize_spell()
      elif self.level == 5:
        energy_options = ["red", "blue", "gold"]
        print("\n".join(f"{i + 1} - {energy}" for i, energy in enumerate(energy_options)))
        chosen_energy = choose_obj(energy_options, colored("Choose an energy type to tap into > ", "cyan"))
        self.starting_inventory.append(EnergyPotion(chosen_energy, 1))
        self.inventory.append(EnergyPotion(chosen_energy, 1))
      elif self.level == 6:
        self.memorize_spell()
      elif self.level == 7:
        self.learn_ritual()
      elif self.level == 8:
        self.memorize_spell()
      elif self.level == 9:
        self.gain_signature_item()


  def init(self, spell_pool):
    print(numbered_list(starting_weapons))
    chosen_weapon = choose_obj(starting_weapons, "which weapon will you take > ")
    play_sound("inventory.mp3")

    starting_spellbook = Spellbook(pages=[])
    
    # recharge signature spells to max and get 1 more charge
    # for a random non-signature spell
    for library_spell in self.library:
      if library_spell.signature:
        library_spell.copies_remaining = max(library_spell.max_copies_remaining, library_spell.copies_remaining)

    for ritual in self.rituals:
      ritual.progress = 0

    inventory = deepcopy(self.starting_inventory)
    inventory.append(deepcopy(chosen_weapon))
    self.hp = self.max_hp
    self.clear_conditions()
    self.facing = "front"
    self.spellbook = starting_spellbook
    self.inventory = inventory
    self.request = None

  def get_immediate(self, encounter, offset=0):
    """Returns the closest enemy on the side the player is facing,
    or None if there are no enemies on that side."""
    if self.facing == "front":
      immediate = encounter.front[offset:offset+1]
    if self.facing == "back":
      immediate = encounter.back[offset:offset+1]
    return immediate[0] if immediate else None

  def switch_face(self, event=True):
    if self.facing == "front":
      self.facing = "back"
    elif self.facing == "back":
      self.facing = "front"
    else:
      raise ValueError(f"Facing is: {self.facing}")
    play_sound("face.mp3")
    if event:
      self.events.append(Event(["face"]))
      self.face_count += 1

  def render(self):
    entity_str = super().render()
    return entity_str.replace(self.name, f"[{self.level_progress_str}"
                                         f"{colored(',' * self.wounds, 'red')}] "
                                         f"{self.name} ({'.' * self.time})")

  def render_resources(self):
    resource_strs = [f"- {k}: {v}" for k, v in self.resources.items()]
    resources_str = "\n".join(resource_strs)
    return colorize(resources_str)
  
  def render_rituals(self):
    render_str = "-------- PLAYER RITUALS --------\n"
    render_str += numbered_list(self.rituals)
    return render_str
  
  def render_inventory(self):
    render_str = "-------- INVENTORY --------\n"
    render_str += numbered_list(self.inventory)
    return render_str
  
  def render_library(self):
    render_str = "-------- PLAYER LIBRARY --------\n"
    render_str += numbered_list(self.library)
    return render_str
  
  def inspect(self):
    print(self.render_inventory())
    print(self.render_library())
    print(self.render())
    proceed = choose_binary("Proceed with this character?")
    return proceed
    


