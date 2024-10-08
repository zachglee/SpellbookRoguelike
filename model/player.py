from typing import Any, Optional
from generators import generate_library_spells, generate_recipe
from model.recipe import Recipe
from model.ritual import Ritual
from termcolor import colored
import random
import dill
from copy import deepcopy
from collections import defaultdict
from model.combat_entity import CombatEntity
from model.spellbook import LibrarySpell, Spell, Spellbook, SpellbookPage
from model.item import Item
from utils import choose_binary, choose_str, colorize, numbered_list, choose_obj, energy_colors, render_secrets_dict, ws_input, ws_print
from sound_utils import play_sound, ws_play_sound
from model.event import Event
from content.enemy_factions import faction_rituals_dict
from content.items import minor_energy_potions

class Player(CombatEntity):

  # Combat stuff
  spellbook: Optional[Spellbook]
  inventory: list[Item]
  rituals: list[Ritual] = []
  time: int = 4
  facing: str = "front"
  explored: int = 0
  revive_cost: Optional[int] = None

  # Meta state
  personal_spells: list[LibrarySpell] = []
  library: list[LibrarySpell]
  known_rituals: list[Ritual] = []

  archived_pages: list[SpellbookPage] = []
  remaining_blank_archive_pages: int = 0
  archive: list[LibrarySpell] = [] # archive of drafted spells
  seen_spells: list[LibrarySpell] = []
  starting_inventory: list[Item] = []
  recipes: list[Recipe] = []
  material: int = 10
  secrets_dict: dict[str, int] = defaultdict(int)

  inventory_capacity: int = 10
  library_capacity: int = 10

  level: int = 0
  experience: int = 0
  age: int = 0 # TODO remove, along with .effective_age later
  supplies: int = 6
  retirement_age: int = 3
  location: int = 0
  wounds: int = 0
  request: str = None
  stranded: bool = False
  seen_items: list[Item] = []
  pursuing_enemysets: list[list[str]] = []

  spell_discoveries_pending: int = 0

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

  def save(self):
    websocket_tmp = self.websocket
    self.websocket = None # websocket can't be pickled, so temporarily remove it
    with open(f"saves/characters/{self.name}.pkl", "wb") as f:
      dill.dump(self, f)
    self.websocket = websocket_tmp

  def total_energy(self, colors=energy_colors):
    player_energy = sum(self.conditions[color] for color in colors)
    return player_energy

  @property
  def next_exp_milestone(self):
    next_level = self.level + 1
    total_exp_required = 30 + sum([i * 30 for i in range(1, next_level + 1)])
    return total_exp_required
  
  @property
  def level_progress_str(self):
    return f"{self.experience}/{self.next_exp_milestone}"
  
  @property
  def rituals_dict(self):
    """Returns a dictionary of faction names to ritual objects."""
    return {ritual.faction: ritual for ritual in self.rituals if ritual.faction}
  
  @property
  def active_ritual_list(self):
    return [ritual for ritual in self.rituals if ritual.progress > 0]
  
  @property
  def inventory_weight(self):
    return sum([item.weight for item in self.inventory])
  
  @property
  def total_ritual_levels(self):
    return sum([ritual.level for ritual in self.rituals])
  
  @property
  def effective_age(self):
    return self.age + self.wounds
    
  def spend_time(self, cost=1):
    if (self.time - cost) >= 0:
      self.time -= cost
    else:
      raise ValueError(colored("Not enough time!", "red"))

  # def memorize_spell(self, spell: Spell):
  #   duplicate_spells = [ls for ls in self.library if ls.spell.rules_text == spell.rules_text and ls.signature]
  #   in_library_spell = duplicate_spells[0] if duplicate_spells else None

  #   if in_library_spell:
  #     in_library_spell.max_copies_remaining += 1
  #     in_library_spell.signature = True
  #   else:
  #     new_library_spell = LibrarySpell(spell, copies=1, signature=True)
  #     self.library.append(new_library_spell)

  # async def memorize_seen_spell(self):
  #   # TODO turn an existing library spell into signature?
  #   await ws_print(self.render_library(), self.websocket)
  #   memorization_spell_pool = self.seen_spells + [ls.spell for ls in self.archive]
  #   choices = random.sample(memorization_spell_pool, min(len(self.seen_spells), 6))
  #   await ws_print("---", self.websocket)
  #   await ws_print(numbered_list(choices), self.websocket)
  #   chosen_spell = deepcopy(await choose_obj(choices, colored("Choose a seen spell to memorize > ", "cyan"), self.websocket))
  #   self.memorize_spell(chosen_spell)

  async def level_up(self):
    self.level += 1
    self.max_hp += 1
    self.hp += 1
    if self.level > 0 and self.level % 3 == 0:
      self.spell_discoveries_pending += 1
    await ws_input(colored(f"You leveled up! You are now level {self.level} and your max hp is {self.max_hp}", "green"), self.websocket)

  async def check_level_up(self):
    while self.experience >= self.next_exp_milestone:
      await self.level_up()

  async def learn_rituals(self):
    while self.ritual_learnings_pending > 0:
      await ws_print(numbered_list(self.rituals), self.websocket)
      ritual = await choose_obj(self.rituals, "Choose a ritual to work on > ", self.websocket)
      if ritual is None:
        break
      # ritual.level += ritual.required_progress
      # ritual.progress += ritual.required_progress
      self.known_rituals.append(ritual)
      self.ritual_learnings_pending -= 1
      await ws_print(f"-------- Known Rituals --------", self.websocket)
      await ws_print(numbered_list(self.known_rituals), self.websocket)

  async def learn_recipe(self):
    item_options = (random.sample([item for item in self.seen_items if item.craftable], 3)
                    if len(self.seen_items) > 3 else self.seen_items)
    recipe_options = [generate_recipe(item) for item in item_options]
    await ws_print(numbered_list(recipe_options), self.websocket)
    chosen_recipe = await choose_obj(recipe_options, "Choose an item to learn the recipe for > ", self.websocket)
    if chosen_recipe is None:
      return
    self.recipes.append(chosen_recipe)
    await ws_print(colored(f"You've learned the recipe for {chosen_recipe.item.name}!", "green"), self.websocket)

  async def discover_spells(self):
    while self.spell_discoveries_pending > 0:
      spell_choices = [ls.spell for ls in generate_library_spells(3)]
      await ws_print("\n" + numbered_list(spell_choices), self.websocket)
      spell = await choose_obj(spell_choices, "Choose a spell you've personally discovered > ", self.websocket)
      if spell is None:
        break
      self.personal_spells.append(LibrarySpell(spell, copies=1, material_cost=5, signature=True))
      self.spell_discoveries_pending -= 1

  # async def memorize(self):
  #   while self.memorizations_pending > 0:
  #     # Mark an existing library spell as signature spell
  #     await ws_print(self.render_library(), self.websocket)
  #     chosen_spell = await choose_obj(self.library, "Choose a spell to memorize > ", self.websocket)
  #     if chosen_spell is None:
  #       break
  #     chosen_spell.signature = True
  #     # await self.memorize_seen_spell() # FOR NOW BYPASSING THIS
  #     self.memorizations_pending -= 1

  def prompt_personal_destination(self):
    region_idx, layer_idx, node_idx = self.personal_destination
    print(colored(f"Region {region_idx}, Node ({layer_idx}, {node_idx}) is of signifigance to you.", "magenta"))
    input(colored("What do you hope to find there? > ", "magenta"))

  async def gain_material(self, amount):
    self.material += amount
    await ws_print(colored(f"You gained {amount} material! Now you have {self.material}.", "yellow"), self.websocket)

  async def gain_secrets(self, faction, amount):
    self.secrets_dict[faction] += amount
    if faction not in self.rituals_dict:
      self.rituals.append(faction_rituals_dict[faction])
    await ws_print(colored(f"You discovered {amount} secrets of faction {faction}. Now you have {self.secrets_dict[faction]}.", "magenta"), self.websocket)

  def init(self):
    self.pursuing_enemysets = []

    starting_spellbook = Spellbook(pages=[])
    self.library = []

    # recharge signature spells to max
    for library_spell in self.library:
      if library_spell.signature:
        library_spell.copies_remaining = max(library_spell.max_copies_remaining, library_spell.copies_remaining)

    # NOTE: We're trying buying ritual progress with secrets in pre-embark phase instead
    # for ritual in self.rituals:
    #   ritual.progress = ritual.level

    inventory = deepcopy(self.starting_inventory)
    inventory += (
      [Item.make(f"{self.name}'s Ring", 1, "+2 time.", use_commands=["time -2"], personal=True),
      Item.make(f"{self.name}'s Dagger", 1, "Deal 3 damage to immediate.", use_commands=["damage i 3"], personal=True)])
      # + [deepcopy(random.choice(minor_energy_potions))])
    self.hp = self.max_hp
    self.clear_conditions()
    self.facing = "front"
    self.spellbook = starting_spellbook
    self.inventory = inventory
    self.request = None
    self.seen_spells = []
    # self.material = 0
    self.secrets_dict = defaultdict(int)
    # self.remaining_blank_archive_pages += 1

  def get_immediate(self, encounter, offset=0):
    """Returns the closest enemy on the side the player is facing,
    or None if there are no enemies on that side."""
    if self.facing == "front":
      immediate = encounter.front[offset:offset+1]
    if self.facing == "back":
      immediate = encounter.back[offset:offset+1]
    return immediate[0] if immediate else None

  async def switch_face(self, event=True):
    if self.facing == "front":
      self.facing = "back"
    elif self.facing == "back":
      self.facing = "front"
    else:
      raise ValueError(f"Facing is: {self.facing}")
    await ws_play_sound("face.mp3", self.websocket)
    if event:
      self.events.append(Event(["face"]))
      self.face_count += 1


  def render(self):
    entity_str = super().render()
    time_str = '.' * self.time
    triggers_str = colored("!" * len(self.event_triggers), "green")
    return entity_str.replace(self.name, f"[{self.level_progress_str}"
                                         f"{colored(',' * self.wounds, 'red')}] "
                                         f"{self.name} ({time_str}{triggers_str})")
  
  def render_rituals(self):
    render_str = "-------- PLAYER RITUALS --------\n"
    render_str += numbered_list(self.active_ritual_list)
    return render_str
  
  def render_inventory(self):
    material_str = colored(f"{self.material}⛁", "yellow")
    render_str = f"-------- INVENTORY ({self.inventory_weight}/{self.inventory_capacity}) {material_str} --------\n"
    render_str += numbered_list(self.inventory)
    return render_str
  
  def render_library(self):
    material_str = colored(f"{self.material}⛁", "yellow")
    render_str = f"-------- PLAYER LIBRARY ({material_str}) --------\n"
    render_str += numbered_list(self.library, in_player_library=True)
    return render_str

  def render_pursuing_enemysets(self):
    render_str = colored("-------- THESE ENEMIES PURSUE YOU --------\n", "red")
    render_str += numbered_list(self.pursuing_enemysets)
    return render_str

  def render_state(self):
    return "\n".join([self.render_rituals(), self.render_inventory(), self.render_pursuing_enemysets(), self.render_library(), self.render()])
    
