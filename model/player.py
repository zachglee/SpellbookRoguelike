from typing import Any, Optional
from drafting import draft_player_library
from model.ritual import Ritual
from termcolor import colored
import random
from copy import deepcopy
from collections import defaultdict
from model.combat_entity import CombatEntity
from model.spellbook import LibrarySpell, Spellbook
from model.item import Item
from utils import choose_binary, choose_str, colorize, numbered_list, choose_obj, energy_colors, ws_input, ws_print
from sound_utils import play_sound
from model.event import Event

class Player(CombatEntity):

  # Combat stuff
  spellbook: Optional[Spellbook]
  inventory: list[Item]
  rituals: list[Ritual] = []
  time: int = 4
  facing: str = "front"
  explored: int = 1

  # Meta state
  signature_spell: LibrarySpell
  library: list[LibrarySpell]
  archive: list[LibrarySpell] = []
  seen_spells: list[LibrarySpell] = []
  starting_inventory: list[Item] = []
  material: int = 0
  secrets_dict: dict[str, int] = defaultdict(int)

  inventory_capacity: int = 12
  library_capacity: int = 10

  level: int = 0
  experience: int = 0
  wounds: int = 0
  seen_items: list[Item] = []
  pursuing_enemysets: list[list[str]] = []
  memorizations_pending: int = 0
  personal_item: Item = None
  request: str = None
  stranded: bool = False

  done: bool = False
  id: Optional[str] = None
  websocket: Any = None

  class Config:
    arbitrary_types_allowed = True

  @classmethod
  def make(cls, hp, name, spellbook, inventory, library,
           signature_spell=None, starting_inventory=None):
    starting_inventory = starting_inventory or []
    player = Player(hp=hp, max_hp=hp, name=name, spellbook=spellbook, inventory=inventory, library=library,
                  signature_spell=signature_spell, starting_inventory=starting_inventory)
    return player

  # --------

  def total_energy(self, colors=energy_colors):
    player_energy = sum(self.conditions[color] for color in colors)
    return player_energy

  @property
  def next_exp_milestone(self):
    next_level = self.level + 1
    total_exp_required = 20 + sum([i * 20 for i in range(1, next_level + 1)])
    return total_exp_required
  
  @property
  def level_progress_str(self):
    return f"{self.experience}/{self.next_exp_milestone}"
  
  @property
  def rituals_dict(self):
    """Returns a dictionary of faction names to ritual objects."""
    return {ritual.faction: ritual for ritual in self.rituals if ritual.faction}
    
  def spend_time(self, cost=1):
    if (self.time - cost) >= 0:
      self.time -= cost
    else:
      raise ValueError(colored("Not enough time!", "red"))

  def memorize_spell(self, spell):
    duplicate_spells = [ls for ls in self.library if ls.spell.rules_text == spell.spell.rules_text]
    if duplicate_spells:
      spell = duplicate_spells[0]

    if spell.signature:
      spell.max_copies_remaining += 1
    else:
      spell.signature = True
      spell.max_copies_remaining = 1
      self.library.append(spell)

  async def memorize_archived_spell(self):
    await ws_print(self.render_library(), self.websocket)
    choices = random.sample(self.archive, min(len(self.archive), 6))
    await ws_print("---", self.websocket)
    await ws_print(numbered_list(choices), self.websocket)
    chosen_spell = deepcopy(choose_obj(choices, colored("Choose an archived spell to memorize > ", "cyan"), self.websocket))
    self.memorize_spell(chosen_spell)

  async def memorize_seen_spell(self):
    await ws_print(self.render_library(), self.websocket)
    choices = random.sample(self.seen_spells, min(len(self.seen_spells), 9))
    await ws_print("---", self.websocket)
    await ws_print(numbered_list(choices), self.websocket)
    chosen_spell = deepcopy(await choose_obj(choices, colored("Choose a seen spell to memorize > ", "cyan"), self.websocket))
    self.memorize_spell(chosen_spell)

  async def level_up(self):
    self.level += 1
    self.max_hp += 1
    self.hp += 1
    if self.level > 0 and self.level % 2 == 0:
      self.memorizations_pending += 1
    await ws_input(colored(f"You leveled up! You are now level {self.level} and your max hp is {self.max_hp}", "green"), self.websocket)

  async def check_level_up(self):
    while self.experience >= self.next_exp_milestone:
      await self.level_up()

  async def memorize(self):
    while self.memorizations_pending > 0:
      # await self.memorize_archived_spell()
      await self.memorize_seen_spell()
      self.memorizations_pending -= 1

  def prompt_personal_destination(self):
    region_idx, layer_idx, node_idx = self.personal_destination
    print(colored(f"Region {region_idx}, Node ({layer_idx}, {node_idx}) is of signifigance to you.", "magenta"))
    input(colored("What do you hope to find there? > ", "magenta"))

  async def gain_material(self, amount):
    self.material += amount
    await ws_print(colored(f"You gained {amount} material! Now you have {self.material}.", "yellow"), self.websocket)

  async def gain_secrets(self, faction, amount):
    self.secrets_dict[faction] += amount
    await ws_print(colored(f"You discovered {amount} secrets of faction {faction}. Now you have {self.secrets_dict[faction]}.", "magenta"), self.websocket)

  def init(self):
    self.pursuing_enemysets = []

    starting_spellbook = Spellbook(pages=[])
    self.library = [ls for ls in self.library if ls.signature]

    # recharge signature spells to max
    for library_spell in self.library:
      if library_spell.signature:
        library_spell.copies_remaining = max(library_spell.max_copies_remaining, library_spell.copies_remaining)

    for ritual in self.rituals:
      ritual.progress = 0

    inventory = deepcopy(self.starting_inventory)
    inventory += [Item.make(f"{self.name}'s Ring", 1, "+2 time.", use_commands=["time -2"], personal=True),
                  Item.make(f"{self.name}'s Dagger", 1, "Deal 3 damage to immediate.", use_commands=["damage i 3"], personal=True)]
    self.hp = self.max_hp
    self.clear_conditions()
    self.facing = "front"
    self.spellbook = starting_spellbook
    self.inventory = inventory
    self.request = None
    self.material = 0

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
    render_str = f"-------- INVENTORY ({len(self.inventory)}/{self.inventory_capacity}) {material_str} --------\n"
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
    
