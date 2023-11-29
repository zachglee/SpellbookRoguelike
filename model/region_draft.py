from copy import deepcopy
import random
from typing import List, Tuple
from termcolor import colored

from model.enemy import EnemySet
from model.spellbook import LibrarySpell, Spell
from utils import choose_obj, numbered_list, wait_for_teammates, ws_print

class DraftPickOption:
  def __init__(self, enemyset, spell, material):
    self.enemyset = enemyset
    self.spell = spell
    self.material = material
    self.pickable = True
  
  def render(self, show_rules_text=False):
    enemyset_str = self.enemyset.render(show_rules_text=show_rules_text)
    spell_str = self.spell.render()
    material_str = colored(f"{self.material}⛁", "yellow")
    return f"{material_str} | {enemyset_str} | {spell_str}"

class RegionDraft:
  def __init__(self, difficulty, factions, spell_pool, n_options=3, n_picks=3):
    self.difficulty = difficulty
    self.factions = factions
    self.enemyset_pool = sum([faction.enemy_sets for faction in factions], []) * 2
    self.spell_pool = spell_pool
    self.n_options = n_options
    self.n_picks = n_picks

    self.enemyset_pool_idx = 0
    self.spell_pool_idx = 0
    random.shuffle(self.enemyset_pool)
    random.shuffle(self.spell_pool)

    self.draft_picks = []

  @property
  def basic_items(self):
    return sum([faction.basic_items for faction in self.factions], [])
  
  @property
  def special_items(self):
    return sum([faction.special_items for faction in self.factions], [])

  def init(self):
    self.enemyset_pool_idx = 0
    self.spell_pool_idx = 0
    random.shuffle(self.enemyset_pool)
    random.shuffle(self.spell_pool)
    self.draft_picks = []
    for i in range(self.n_picks):
      self.draft_picks.append(self.generate_draft_pick_options(self.n_options))

  def generate_draft_pick_option(self) -> DraftPickOption:
    if self.enemyset_pool_idx >= len(self.enemyset_pool):
      return None
    if self.spell_pool_idx >= len(self.spell_pool):
      return None

    enemyset = deepcopy(self.enemyset_pool[self.enemyset_pool_idx])
    spell = self.spell_pool[self.spell_pool_idx]
    material = random.randint(1, 6)

    self.enemyset_pool_idx += 1
    self.spell_pool_idx += 1

    return DraftPickOption(enemyset, spell, material)
  
  def generate_draft_pick_options(self, n_options):
    picks = []
    for i in range(n_options):
      pick = self.generate_draft_pick_option()

      if pick is None:
        break
      picks.append(pick)
    return picks
  
  async def draft_pick(self, pick_options: List[Tuple[EnemySet, Spell, int]], websocket=None):
    show_rules_text = False
    choice = None
    while choice is None or isinstance(choice, str) or (not choice.pickable):
      # print pick options
      await ws_print(numbered_list(pick_options, show_rules_text=show_rules_text), websocket)
      # choose pick
      choice = await choose_obj(pick_options, "pick one > ", websocket)
      if choice == "rules":
        show_rules_text = not show_rules_text
        print(f"--------------------- NOW RULES ARE {show_rules_text} ---------------------")
        continue
      if not choice.pickable:
        await ws_print(colored("That option has already been picked.", "red"), websocket)
    choice.pickable = False

    return choice
  
  async def play(self, player):
    for i in range(self.n_picks):
      await ws_print(player.render_state(), player.websocket)
      await ws_print("\n", player.websocket)
      await ws_print(f"~~~ Pick {i + 1} of {self.n_picks} ~~~", player.websocket)
      pick_options = self.draft_picks[i]
      pick_option = await self.draft_pick(pick_options, websocket=player.websocket)
      if pick_option.spell:
        chosen_library_spell = LibrarySpell(pick_option.spell, copies=2)
        player.library.append(chosen_library_spell)
      if pick_option.material:
        player.material += pick_option.material
      player.pursuing_enemysets.append(pick_option.enemyset)
      
      await wait_for_teammates(player.id, f"regiondraft{i}")
    
