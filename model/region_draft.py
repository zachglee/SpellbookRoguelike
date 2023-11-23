from copy import deepcopy
import random
from typing import List, Tuple
from termcolor import colored

from model.encounter import EnemySet
from model.spellbook import LibrarySpell, Spell
from utils import choose_obj, numbered_list, wait_for_teammates, ws_print

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
      upside_type = "material" if i == 0 else "spell"
      self.draft_picks.append(self.generate_draft_pick_options(self.n_options, upside=upside_type))

  def generate_material_pick_option(self):
    if self.enemyset_pool_idx >= len(self.enemyset_pool):
      return None

    enemyset = deepcopy(self.enemyset_pool[self.enemyset_pool_idx])

    self.enemyset_pool_idx += 1

    material = random.randint(2, 8)
    return (enemyset, material)

  def generate_spell_pick_option(self):
    if self.enemyset_pool_idx >= len(self.enemyset_pool):
      return None
    if self.spell_pool_idx >= len(self.spell_pool):
      return None

    enemyset = deepcopy(self.enemyset_pool[self.enemyset_pool_idx])
    spell = self.spell_pool[self.spell_pool_idx]

    self.enemyset_pool_idx += 1
    self.spell_pool_idx += 1

    return (enemyset, spell)
  
  def generate_draft_pick_options(self, n_options, upside="spell"):
    picks = []
    for i in range(n_options):
      if upside == "spell":
        pick = self.generate_spell_pick_option()
      elif upside == "material":
        pick = self.generate_material_pick_option()

      if pick is None:
        break
      picks.append(pick)
    return picks
  
  async def draft_pick(self, pick_options: List[Tuple[EnemySet, Spell]], websocket=None):
    choice = None
    while choice is None or (not choice[0].pickable):
      # print pick options
      await ws_print(numbered_list(pick_options), websocket)
      # choose pick
      choice = await choose_obj(pick_options, "pick one > ", websocket)
      if not choice[0].pickable:
        await ws_print(colored("That option has already been picked.", "red"), websocket)
    choice[0].pickable = False
    return choice
  
  async def play(self, player):
    for i in range(self.n_picks):
      await ws_print(player.render_state(), player.websocket)
      await ws_print("\n", player.websocket)
      await ws_print(f"~~~ Pick {i + 1} of {self.n_picks} ~~~", player.websocket)
      pick_options = self.draft_picks[i]
      chosen_enemyset, chosen_upside = await self.draft_pick(pick_options, websocket=player.websocket)

      if isinstance(chosen_upside, Spell):
        chosen_spell = chosen_upside
        chosen_library_spell = LibrarySpell(chosen_spell, copies=2)
        player.library.append(chosen_library_spell)
      elif isinstance(chosen_upside, int):
        player.material += chosen_upside
      player.pursuing_enemysets.append(chosen_enemyset)
      
      await wait_for_teammates(player.id, f"regiondraft{i}")
    
