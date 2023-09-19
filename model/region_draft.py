import random
from typing import List, Tuple

from model.encounter import EnemySet
from model.spellbook import LibrarySpell, Spell
from utils import choose_obj, numbered_list

class RegionDraft:
  def __init__(self, difficulty, factions, spell_pool, n_options=2, n_picks=3):
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

  def generate_material_pick_option(self):
    if self.enemyset_pool_idx >= len(self.enemyset_pool):
      return None

    enemyset = self.enemyset_pool[self.enemyset_pool_idx]

    self.enemyset_pool_idx += 1

    material = random.randint(1, 8) 
    return (enemyset, material)

  def generate_spell_pick_option(self):
    if self.enemyset_pool_idx >= len(self.enemyset_pool):
      return None
    if self.spell_pool_idx >= len(self.spell_pool):
      return None

    enemyset = self.enemyset_pool[self.enemyset_pool_idx]
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
  
  def draft_pick(self, pick_options: List[Tuple[EnemySet, Spell]]):
    # print pick options
    print(numbered_list(pick_options))
    # choose pick
    return choose_obj(pick_options, "pick one > ")
  
  def play(self, player):
    for i in range(self.n_picks):
      print(player.render_state())
      print()
      print(f"~~~ Pick {i + 1} of {self.n_picks} ~~~")
      upside_type = "material" if i == 0 else "spell"
      pick_options = self.generate_draft_pick_options(self.n_options, upside=upside_type)
      chosen_enemyset, chosen_upside = self.draft_pick(pick_options)

      if isinstance(chosen_upside, Spell):
        chosen_spell = chosen_upside
        chosen_library_spell = LibrarySpell(chosen_spell, copies=2)
        player.library.append(chosen_library_spell)
      elif isinstance(chosen_upside, int):
        player.material += chosen_upside
      player.pursuing_enemysets.append(chosen_enemyset)
    
