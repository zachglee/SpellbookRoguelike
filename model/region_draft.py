from copy import deepcopy
import random
from typing import List, Optional, Tuple
from model.player import Player
from termcolor import colored

from model.enemy import EnemySet
from model.spellbook import LibrarySpell, Spell
from utils import choose_obj, numbered_list, ws_print
from content.enemy_factions import faction_dict

class DraftPickOption:
  def __init__(self, enemyset, spell, material, character=None):
    self.enemyset = enemyset
    self.spell = spell
    self.material = material
    self.character: Optional[Player] = character
    self.pickable = True
  
  def render(self, show_rules_text=False):
    enemyset_str = self.enemyset.render(show_rules_text=show_rules_text) if self.enemyset else ""
    spell_str = self.spell.render() if self.spell else ""
    material_str = colored(f"{self.material}⛁", "yellow")
    return f"{material_str}  {enemyset_str}{spell_str}"

class RegionDraft:
  def __init__(self, combat_size, factions, spell_pool, n_options=3, n_spell_picks=3,
               n_enemy_picks=3, difficulty=0, mandatory_enemysets=[]):
    self.combat_size = combat_size
    self.factions = factions # Faction
    self.enemyset_pool = sum([faction.enemy_sets for faction in factions], []) * 2
    self.spell_pool = spell_pool
    self.n_options = n_options
    self.n_spell_picks = n_spell_picks
    self.n_enemy_picks = n_enemy_picks
    self.mandatory_enemysets = mandatory_enemysets
    self.difficulty = difficulty

    self.enemyset_pool_idx = 0
    self.spell_pool_idx = 0
    random.shuffle(self.enemyset_pool)
    random.shuffle(self.spell_pool)

    self.draft_picks: List[List[DraftPickOption]] = []

  @property
  def basic_items(self):
    return sum([faction.basic_items for faction in self.factions], [])
  
  @property
  def special_items(self):
    return sum([faction.special_items for faction in self.factions], [])

  @property
  def n_picks(self):
    return self.n_spell_picks + self.n_enemy_picks

  def level_enemyset(self, enemyset):
    material = 0
    if random.random() < (0.0 + (0.33 * min(self.difficulty, 3))):
      level_distribution = [1, 1, 1, 2, 2, 3]
      
      for i in range(random.choice(level_distribution)):
        enemyset.level_up()
        material += (i+3)
    return material

  def init(self):
    self.enemyset_pool_idx = 0
    self.spell_pool_idx = 0
    random.shuffle(self.enemyset_pool)
    random.shuffle(self.spell_pool)
    self.draft_picks = []
    spell_draft_pick_options = [self.generate_draft_pick_options(self.n_options, type="spell") for _ in range(self.n_spell_picks)]
    enemy_draft_pick_options = [self.generate_draft_pick_options(self.n_options-1, type="enemy") for _ in range(self.n_enemy_picks)]
    
    self.draft_picks = spell_draft_pick_options + enemy_draft_pick_options


  def generate_draft_pick_option(self, type="spell") -> DraftPickOption:
    if type == "enemy" and self.enemyset_pool_idx >= len(self.enemyset_pool):
      return None
    if type == "spell" and self.spell_pool_idx >= len(self.spell_pool):
      return None

    spell = None
    enemyset = None
    character = None
    material = random.randint(1, 6)

    if type == "enemy":
      enemyset = deepcopy(self.enemyset_pool[self.enemyset_pool_idx])
      if random.random() < (0.20 + self.difficulty * 0.05):
        enemyset.obscured = True
        material += 3
      material += self.level_enemyset(enemyset)
      self.enemyset_pool_idx += 1

    if type == "spell":
      self.spell_pool_idx += 1
      spell = self.spell_pool[self.spell_pool_idx]

    return DraftPickOption(enemyset, spell, material, character=character)
  
  def generate_draft_pick_options(self, n_options, type="spell") -> List[DraftPickOption]:
    picks = []
    for i in range(n_options):
      pick = self.generate_draft_pick_option(type=type)

      if pick is None:
        break
      picks.append(pick)
    return picks
  
  async def draft_pick(self, pick_options: List[DraftPickOption], websocket=None):
    show_rules_text = False
    choice = None
    while choice is None or isinstance(choice, str) or (not choice.pickable):
      # print pick options
      await ws_print(numbered_list(pick_options, show_rules_text=show_rules_text), websocket)
      # choose pick
      choice = await choose_obj(pick_options, "pick one > ", websocket)
      if choice is None:
        continue

      if choice == "rules":
        show_rules_text = not show_rules_text
        continue
      if not choice.pickable:
        await ws_print(colored("That option has already been picked.", "red"), websocket)
    choice.pickable = False

    return choice
  
  async def play(self, player, game_state):
    player.pursuing_enemysets += deepcopy(self.mandatory_enemysets)
    for i in range(self.n_picks):
      await ws_print(player.render_state(), player.websocket)
      await ws_print("\n", player.websocket)
      pick_options = self.draft_picks[i]
      await ws_print(f"~~~ Pick {i + 1} of {self.n_picks} ~~~", player.websocket)
      player.seen_spells += [pick_option.spell for pick_option in pick_options if pick_option.spell]
      pick_option = await self.draft_pick(pick_options, websocket=player.websocket)
      if pick_option.spell:
        chosen_library_spell = LibrarySpell(pick_option.spell, copies=1)
        player.library.append(chosen_library_spell)
      if pick_option.material:
        player.material += pick_option.material
      if pick_option.enemyset:
        player.pursuing_enemysets.append(pick_option.enemyset)
      
      await game_state.wait_for_teammates(player.id, f"regiondraft{i}")
