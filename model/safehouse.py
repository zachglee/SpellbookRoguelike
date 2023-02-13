from utils import choose_idx, choose_obj, energy_colors
from model.item import EnergyPotion, SpellPotion

class Safehouse:
  def __init__(self, player):
    self.inventory = []
  
  def craft(self, player):
    while True:
      try:
        cmd = input("craft an item > ")
        if cmd in energy_colors:
          return EnergyPotion(cmd, 1)
        elif cmd == "spell":
          print(player.spellbook.render())
          spell = choose_obj(player.spellbook.spells)
          spell.charges -= 1
          return SpellPotion(spell.spell)
        elif cmd == "done":
          return None
      except (ValueError, TypeError, IndexError) as e:
        print(e)

  def take(self):
    take_item = self.inventory.pop(choose_idx(self.inventory, "take an item > "))
    return take_item

  def render(self):
    render_str = "-------- Safehouse Inventory --------\n"
    return render_str + "\n".join(f"- {item.render()}" for item in self.inventory)