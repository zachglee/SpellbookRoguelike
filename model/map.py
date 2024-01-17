
from generators import generate_crafting_shop, generate_faction_sets, generate_shop, generate_spell_pools
from model.region_draft import BossRegionDraft, RegionDraft
from content.items import minor_energy_potions, health_potions
from content.enemy_factions import factions
from pydantic import BaseModel

class Map:
  def __init__(self, name, n_regions=4):
    self.name = name
    self.region_drafts = []

    spell_pools = generate_spell_pools(n_pools=n_regions)
    faction_sets = generate_faction_sets(n_sets=n_regions, set_size=2, overlap=1, faction_pool=factions)
    self.region_drafts = [RegionDraft(difficulty, faction_set, spell_pool)
                          for difficulty, spell_pool, faction_set in
                          zip([2, 3, 4, 5], spell_pools, faction_sets)]
    self.region_shops = [generate_shop(5, ((region_draft.basic_items + region_draft.special_items +
                                           minor_energy_potions)*2) + health_potions)
                        for region_draft in self.region_drafts]
    self.runs = 0

  def init(self, player): # player arg used in BossMap, kept here for consistent interface
    # init shops
    self.region_shops = [generate_shop(5, ((region_draft.basic_items + region_draft.special_items +
                                           minor_energy_potions)*2) + health_potions)
                        for region_draft in self.region_drafts]
    for region_draft in self.region_drafts:
      region_draft.init()

  def end_run(self):
    self.runs += 1

class BossMap:
  def __init__(self, name, enemy_set_pool, length=2, difficulty=6):
    self.name = name
    self.region_drafts = []
    for i in range(length):
      region_enemy_sets = enemy_set_pool[i * difficulty:(i+1) * difficulty]
      self.region_drafts.append(BossRegionDraft(difficulty, region_enemy_sets))
    self.region_shops = []
    self.runs = 0

  def init(self, player):
    # init shops
    self.region_shops = [generate_crafting_shop(6, player) for _ in self.region_drafts]
    for region_draft in self.region_drafts:
      region_draft.init()

  def end_run(self):
    self.runs += 1