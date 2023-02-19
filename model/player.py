from collections import defaultdict
from model.combat_entity import CombatEntity
from utils import colorize, numbered_list

class Player(CombatEntity):
  def __init__(self, hp, name, spellbook, inventory, library):
    super().__init__(hp, name)
    self.spellbook = spellbook
    self.library = library
    self.inventory = inventory
    self.loot = defaultdict(lambda: 0)
    self.time = 4
    self.facing = "front"
    self.rerolls = 0
    self.explored = 2
    self.capacity = 4

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
  
  def render_inventory(self):
    render_str = "-------- INVENTORY --------\n"
    render_str += numbered_list(self.inventory)
    return render_str
  
  def render_library(self):
    render_str = "-------- PLAYER LIBRARY --------\n"
    render_str += numbered_list(self.library)
    return render_str
    


