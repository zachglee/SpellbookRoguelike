from collections import defaultdict
from model.combat_entity import CombatEntity
from utils import colorize

class Player(CombatEntity):
  def __init__(self, hp, name, spellbook, inventory):
    super().__init__(hp, name)
    self.spellbook = spellbook
    self.inventory = inventory
    self.loot = defaultdict(lambda: 0)
    self.time = 4
    self.facing = "front"

  def switch_face(self):
    if self.facing == "front":
      self.facing = "back"
    elif self.facing == "back":
      self.facing = "front"
    else:
      raise ValueError(f"Facing is: {self.facing}")

  def render(self):
    entity_str = super().render()
    return entity_str.replace("Player", f"Player ({'.' * self.time})")

  def render_loot(self):
    loot_strs = [f"- {k}: {v}" for k, v in self.loot.items()]
    loot_str = "\n".join(loot_strs)
    return colorize(loot_str)
    


