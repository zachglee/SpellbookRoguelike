
from collections import defaultdict
import random
import dill
from termcolor import colored
from generators import generate_faction_sets, generate_shop, generate_spell_pools
from model.region_draft import RegionDraft
from content.items import minor_energy_potions, health_potions
from content.enemy_factions import factions

class Map:
  def __init__(self, name, n_regions=3, difficulty=0, region_drafts=None, num_escapes=1):
    self.name = name
    self.difficulty = difficulty
    self.completed_difficulties = defaultdict(int) # Mapping of int difficulty to how many times completed4
    self.num_escapes = num_escapes

    if region_drafts is None:
      self.region_drafts = []
      spell_pools = generate_spell_pools(n_pools=n_regions)
      random.shuffle(factions)
      faction_sets = generate_faction_sets(n_sets=n_regions, set_size=2, overlap=1, faction_pool=factions[:3])
      self.region_drafts = [
        RegionDraft(combat_size, faction_set, spell_pool, n_enemy_picks=n_enemy_picks, n_spell_picks=n_spell_picks, difficulty=self.difficulty)
        for combat_size, n_enemy_picks, n_spell_picks, spell_pool, faction_set in
        zip([3, 4, 5], [3, 2, 2], [0, 0, 0], spell_pools, faction_sets)
      ]
    else:
      self.region_drafts = region_drafts

    if self.name is None:
      faction1, faction2 = tuple(self.region_drafts[0].factions[0:2])
      adjective = random.choice(faction1.map_name_adjectives)
      noun = random.choice(faction2.map_name_nouns)
      self.name = f"{adjective} {noun}"

    self.region_shops = [generate_shop(5, ((region_draft.basic_items + region_draft.special_items +
                                           minor_energy_potions)*2) + health_potions)
                        for region_draft in self.region_drafts]
    self.explored = False
    self.runs = 0

  @property
  def factions(self):
    return sum([region_draft.factions for region_draft in self.region_drafts], [])

  def save(self):
    with open(f"saves/maps/{self.name}.pkl", "wb") as f:
      dill.dump(self, f)

  def init(self):
    # init shops
    self.region_shops = [generate_shop(5, ((region_draft.basic_items + region_draft.special_items +
                                           minor_energy_potions)*2) + health_potions,
                                           key=True)
                        for region_draft in self.region_drafts]
    for region_draft in self.region_drafts:
      region_draft.difficulty = self.difficulty
      region_draft.init()

  def end_run(self):
    self.runs += 1

  def render(self):
    faction_symbol_part = "".join(faction.symbol for faction in self.region_drafts[0].factions)
    name_part = colored(f"{self.name} ({faction_symbol_part})", "magenta")
    difficulty_part = colored(f"d.{self.difficulty}", "red")
    return f"{name_part} | {difficulty_part}"
