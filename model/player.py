from drafting import draft_player_library
from termcolor import colored
import random
from copy import deepcopy
from collections import defaultdict
from model.combat_entity import CombatEntity
from model.spellbook import Spellbook
from model.item import CustomItem, EnergyPotion
from utils import choose_binary, choose_str, colorize, numbered_list, choose_obj, energy_colors
from sound_utils import play_sound
from content.rituals import rituals
from content.items import starting_weapons
from content.enemy_factions import all_special_items, all_basic_items
from model.event import Event

class Player(CombatEntity):
  def __init__(self, hp, name, spellbook, inventory, library,
               signature_spell=None, signature_color=None, starting_inventory=None,
               aspiration=None, personal_destination=None, starting_weapon=None,
               home_column=0):
    super().__init__(hp, name)

    # Combat stuff
    self.spellbook = spellbook
    self.inventory = inventory
    self.rituals = []
    self.time = 4
    self.facing = "front"
    self.explored = 1

    # Meta state
    self.signature_spell = signature_spell
    self.signature_color = signature_color
    self.library = library
    self.archive = []
    self.starting_inventory = starting_inventory or []
    # self.starting_inventory.append(EnergyPotion(self.signature_color, 1))
    self.starting_item_pool = starting_weapons
    if starting_weapon:
      self.starting_inventory.append(starting_weapon)
    self.material = 0

    # self.character_class = choose_str(["Explorer", "Builder", "Scholar"], "Choose a character class > ")
    self.character_class = "Builder"
    if self.character_class == "Explorer":
      self.find_route_cost = 1
      self.find_route_cost_scale_amount = 1
    elif self.character_class == "Builder":
      self.find_route_cost = 2
      self.find_route_cost_scale_amount = 2
      self.material = 10
    if self.character_class == "Scholar":
      self.find_route_cost = 3
      self.find_route_cost_scale_amount = 3

    self.home_column = home_column
    self.current_column = home_column
    self.inventory_capacity = 10 # meant to be for inventory but not used right now
    self.library_capacity = 10
    self.library_draft_randoms = 1
    self.library_draft_picks = 2
    self.library_draft_options = 2

    self.level = 0
    self.experience = 0
    self.wounds = 0
    self.seen_items = []
    self.pursuing_enemysets = []

    # character role playing
    self.personal_item = None
    self.request = None
    self.aspiration_statement = ""
    self.aspiration = aspiration
    self.personal_destination = personal_destination

  def total_energy(self, colors=energy_colors):
    player_energy = sum(self.conditions[color] for color in colors)
    return player_energy

  @property
  def next_exp_milestone(self):
    next_level = self.level + 1
    total_exp_required = 40 + sum([i * 40 for i in range(1, next_level + 1)])
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
    choices = random.sample(self.archive, min(len(self.archive), 4))
    print("---")
    print(numbered_list(choices))
    chosen_spell = deepcopy(choose_obj(choices, colored("Choose a spell to memorize > ", "cyan")))

    duplicate_spells = [ls for ls in self.library if ls.spell.rules_text == chosen_spell.spell.rules_text]
    if duplicate_spells:
      chosen_spell = duplicate_spells[0]

    if chosen_spell.signature:
      chosen_spell.max_copies_remaining += 1
    else:
      chosen_spell.signature = True
      chosen_spell.max_copies_remaining = 1
      self.library.append(chosen_spell)

  def learn_ritual(self):
    random.shuffle(rituals)
    ritual_choices = rituals[0:3]
    print(numbered_list(ritual_choices))
    chosen_ritual = choose_obj(ritual_choices, colored("Choose a ritual to learn > ", "cyan"))
    self.rituals.append(deepcopy(chosen_ritual))

  def gain_starting_item(self):
    seen_basic_items = [item for item in self.seen_items
                        if not item.rare and item.name not in ["Red Potion", "Blue Potion", "Gold Potion"]]
    random.shuffle(seen_basic_items)
    starting_item_choices = seen_basic_items[0:3]
    if len(starting_item_choices) == 0:
      starting_item_choices = [random.choice(all_basic_items)]
    print(numbered_list(starting_item_choices))
    chosen_item = choose_obj(starting_item_choices, colored("Choose another starting item > ", "cyan"))
    chosen_item.charges = chosen_item.max_charges
    self.starting_item_pool.append(deepcopy(chosen_item))

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
      self.max_hp += 2
      self.hp += 2
      print(colored(f"You leveled up! You are now level {self.level} and your max hp is {self.max_hp}", "green"))
      self.memorize_spell()
      # if self.level == 1:
      #   self.starting_inventory.append(EnergyPotion(self.signature_color, 1))
      #   self.inventory.append(EnergyPotion(self.signature_color, 1))
      #   print("You have gained another innate energy of your signature color!")
      # elif self.level == 2:
      #   self.learn_ritual()
      # elif self.level == 3:
      #   self.library_draft_options += 1
      #   print(f"You will now have {self.library_draft_options} options when drafting your library.")
      # elif self.level == 4:
      #   energy_options = ["red", "blue", "gold"]
      #   print("\n".join(f"{i + 1} - {energy}" for i, energy in enumerate(energy_options)))
      #   chosen_energy = choose_obj(energy_options, colored("Choose a new energy type to tap into > ", "cyan"))
      #   self.starting_inventory.append(EnergyPotion(chosen_energy, 1))
      #   self.inventory.append(EnergyPotion(chosen_energy, 1))
      # elif self.level == 5:
      #   self.gain_starting_item()
      # elif self.level == 6:
      #   self.library_draft_picks += 1
      #   self.library_draft_randoms -= 1
      #   print(f"You will now have {self.library_draft_picks} picks when drafting your library.")
      # elif self.level == 7:
      #   self.memorize_spell()
      # elif self.level == 8:
      #   self.learn_ritual()
      # elif self.level == 9:
      #   self.library_draft_options += 1
      #   print(f"You will now have {self.library_draft_options} options when drafting your library.")
      # elif self.level == 10:
      #   self.gain_signature_item()

  def choose_personal_item(self):
    return CustomItem(f"{self.name}'s Ring", 1, "+2 time.", use_commands=["time -2"], personal=True)

  def choose_aspiration(self):
    self.aspiration_statement = input(colored(f"What does {self.name} aspire to? > ", "magenta"))

  def prompt_personal_destination(self):
    region_idx, layer_idx, node_idx = self.personal_destination
    print(colored(f"Region {region_idx}, Node ({layer_idx}, {node_idx}) is of signifigance to you.", "magenta"))
    input(colored("What do you hope to find there? > ", "magenta"))

  def gain_material(self, amount):
    self.material += amount
    print(colored(f"You gained {amount} material! Now you have {self.material}.", "yellow"))

  def init(self):
    self.pursuing_enemysets = []
    personal_item = self.choose_personal_item()

    starting_spellbook = Spellbook(pages=[])
    self.library = [ls for ls in self.library if ls.signature]

    # recharge signature spells to max
    for library_spell in self.library:
      if library_spell.signature:
        library_spell.copies_remaining = max(library_spell.max_copies_remaining, library_spell.copies_remaining)

    for ritual in self.rituals:
      ritual.progress = 0

    inventory = deepcopy(self.starting_inventory)
    inventory.append(personal_item)
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

  def archive_library_spells(self, copies_threshold=0):
    to_archive = [ls for ls in self.library if ls.copies_remaining <= copies_threshold and not ls.signature and not ls.in_archive]
    self.archive += to_archive
    self.library = [ls for ls in self.library if ls.copies_remaining > copies_threshold or ls.signature]

  def render(self):
    entity_str = super().render()
    time_str = '.' * self.time
    triggers_str = colored("!" * len(self.event_triggers), "green")
    return entity_str.replace(self.name, f"[{self.level_progress_str}"
                                         f"{colored(',' * self.wounds, 'red')}] "
                                         f"{self.name} ({time_str}{triggers_str})")
  
  def render_rituals(self):
    render_str = "-------- PLAYER RITUALS --------\n"
    render_str += numbered_list(self.rituals)
    return render_str
  
  def render_inventory(self):
    material_str = colored(f"{self.material}⛁", "yellow")
    render_str = f"-------- INVENTORY {material_str} --------\n"
    render_str += numbered_list(self.inventory)
    return render_str
  
  def render_library(self):
    render_str = "-------- PLAYER LIBRARY --------\n"
    render_str += numbered_list(self.library)
    return render_str

  def render_pursuing_enemysets(self):
    render_str = colored("-------- THESE ENEMIES PURSUE YOU --------\n", "red")
    render_str += numbered_list(self.pursuing_enemysets)
    return render_str

  def render_state(self):
    return "\n".join([self.render_rituals(), self.render_inventory(), self.render_pursuing_enemysets(), self.render_library(), self.render()])

  def inspect(self):
    print(self.render_state())
    proceed = choose_binary("Proceed with this character?")
    return proceed
    


