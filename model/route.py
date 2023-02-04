import random
from model.encounter import Encounter

class Route:
  def __init__(self, enemy_sets, rest_site):
    self.enemy_sets = enemy_sets
    self.normal_encounters = [
      Encounter(self.enemy_sets[i:i+3], None)
      for i in range(0, len(enemy_sets), 3)
    ]
    self.boss_encounter = Encounter([random.choice(self.enemy_sets) for _ in range(4)], None)
    self.rest_site = rest_site
