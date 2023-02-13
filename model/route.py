import random
from model.encounter import Encounter
from model.safehouse import Safehouse

class Route:
  def __init__(self, enemy_sets, rest_site, spell_pool):
    self.enemy_sets = enemy_sets
    self.rest_site = rest_site
    self.spell_echoes = []
    self.library = []
    self.spell_pool = spell_pool
    self.safehouse = Safehouse()

  def generate_encounters(self):
    random.shuffle(self.enemy_sets)
    self.normal_encounters = [
      Encounter(self.enemy_sets[i:i+3], None)
      for i in range(0, len(self.enemy_sets), 3)
    ]
    random.shuffle(self.enemy_sets)
    self.boss_encounters = [
      Encounter(self.enemy_sets[0:4], None),
      Encounter(self.enemy_sets[4:8], None),
    ]

  def get_echo(self):
    valid_choices = [spell for spell in self.spell_echoes if spell.charges > 0 and not spell.echoing]
    if valid_choices:
      return random.choice(valid_choices)
    else:
      return None

