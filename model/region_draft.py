from copy import deepcopy
import random
from typing import List, Optional, Tuple
from model.player import Player
from termcolor import colored

from model.enemy import EnemySet
from model.spellbook import LibrarySpell, Spell
from utils import choose_obj, numbered_list, wait_for_teammates, ws_print
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
    return f"{material_str} | {enemyset_str} | {spell_str}"

class RegionDraft:
  def __init__(self, combat_size, factions, spell_pool, n_options=3, n_spell_picks=3,
               n_enemy_picks=3, skip_reward=8, difficulty=0):
    self.combat_size = combat_size
    self.factions = factions
    self.enemyset_pool = sum([faction.enemy_sets for faction in factions], []) * 2
    self.spell_pool = spell_pool
    self.stranded_characters: List[Player] = []
    self.n_options = n_options
    self.n_spell_picks = n_spell_picks
    self.n_enemy_picks = n_enemy_picks
    self.skip_reward = skip_reward
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
    if random.random() < (0.20 + (0.20 * min(self.difficulty, 4))):
      material += 1
      if self.difficulty <= 3:
        level_distribution = [1, 1, 1, 1, 2, 2]
      elif self.difficulty == 4:
        level_distribution = [1, 1, 1, 2, 2, 3]
      elif self.difficulty == 5:
        level_distribution = [1, 1, 2, 2, 3, 3]
      elif self.difficulty == 6:
        level_distribution = [1, 2, 2, 3, 3, 3]
      
      for i in range(random.choice(level_distribution)):
        enemyset.level_up()
        material += (i+1)
    return material

  def init(self):
    self.enemyset_pool_idx = 0
    self.spell_pool_idx = 0
    random.shuffle(self.enemyset_pool)
    random.shuffle(self.spell_pool)
    self.draft_picks = []
    spell_draft_pick_options = [self.generate_draft_pick_options(self.n_options, type="spell") for _ in range(self.n_spell_picks)]
    enemy_draft_pick_options = [self.generate_draft_pick_options(self.n_options-1, type="enemy") for _ in range(self.n_enemy_picks)]
    
    for i in range(max(self.n_spell_picks, self.n_enemy_picks)):
      if spell_draft_pick_options:
        self.draft_picks.append(spell_draft_pick_options.pop(0))
      if enemy_draft_pick_options:
        self.draft_picks.append(enemy_draft_pick_options.pop(0))

    # for i in range(self.n_picks):
    #   self.draft_picks.append(self.generate_draft_pick_options(self.n_options))

  def generate_draft_pick_option(self, type="spell") -> DraftPickOption:
    if type == "enemy" and self.enemyset_pool_idx >= len(self.enemyset_pool):
      return None
    if type == "spell" and self.spell_pool_idx >= len(self.spell_pool):
      return None

    spell = None
    enemyset = None
    character = None
    material = random.randint(0, 5)

    if type == "enemy":
      enemyset = deepcopy(self.enemyset_pool[self.enemyset_pool_idx])
      if random.random() < (0.33 + self.difficulty * 0.03):
        enemyset.obscured = True
        material += 2
      material += self.level_enemyset(enemyset)
      if self.stranded_characters and random.random() < 0.6:
        character = random.choice(self.stranded_characters)
        enemyset.level_up()
        spell = character.signature_spell.spell
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
        if all(po.enemyset is None for po in pick_options): # You can only skip if this is not an enemy pick
          return DraftPickOption(None, None, self.skip_reward)
        else:
          continue

      if choice == "rules":
        show_rules_text = not show_rules_text
        continue
      if not choice.pickable:
        await ws_print(colored("That option has already been picked.", "red"), websocket)
    choice.pickable = False

    return choice
  
  async def play(self, player):
    for i in range(self.n_picks):
      await ws_print(player.render_state(), player.websocket)
      await ws_print("\n", player.websocket)
      pick_options = self.draft_picks[i]
      skip_reward_str = colored(f"{self.skip_reward}⛁", "yellow") if pick_options[0].enemyset is None else ""
      await ws_print(f"~~~ Pick {i + 1} of {self.n_picks} ({skip_reward_str} for skipping) ~~~", player.websocket)
      player.seen_spells += [pick_option.spell for pick_option in pick_options if pick_option.spell]
      pick_option = await self.draft_pick(pick_options, websocket=player.websocket)
      if pick_option.character:
        pick_option.character.stranded = False
        self.stranded_characters.remove(pick_option.character)
        pick_option.character.save()
      if pick_option.spell:
        chosen_library_spell = LibrarySpell(pick_option.spell, copies=1)
        player.library.append(chosen_library_spell)
      if pick_option.material:
        player.material += pick_option.material
      if pick_option.enemyset:
        player.pursuing_enemysets.append(pick_option.enemyset)
      
      await wait_for_teammates(player.id, f"regiondraft{i}")


# Experimental for now...
class BossRegionDraft:
  def __init__(self, combat_size, enemy_sets):
    self.combat_size = combat_size
    self.enemy_sets = enemy_sets
    for _ in range(9):
      random.choice(self.enemy_sets).level_up()

  @property
  def basic_items(self):
    return sum([faction_dict[es.faction].basic_items for es in self.enemy_sets], [])
  
  @property
  def special_items(self):
    return sum([faction_dict[es.faction].special_items for es in self.enemy_sets], [])

  def init(self):
    pass

  async def play(self, player):
    # level up enemies
    prepared_enemy_sets = []
    for enemy_set in self.enemy_sets:
      prepared_enemy_set = deepcopy(enemy_set)
      prepared_enemy_set.obscured = True
      prepared_enemy_sets.append(prepared_enemy_set)
    player.pursuing_enemysets += prepared_enemy_sets
    
