from utils import colorize
from model.spellbook import SpellbookSpell

class Item:
  def __init__(self, charges, description):
    self.description = description
    self.charges = charges

  def use(self, encounter):
    pass

  def render(self):
    return self.description

class SpellPotion(Item):
  def __init__(self, spell):
    self.spell = spell
    self.charges = 1

  def use(self, encounter):
    spellbook_spell = SpellbookSpell(self.spell)
    spellbook_spell.echoing = 3
    encounter.player.spellbook.current_page.spells.append(spellbook_spell)
    self.charges -= 1

  def render(self):
    return colorize(f"Spell Potion: {self.spell}")

class EnergyPotion(Item):
  def __init__(self, energy_color, energy_amount):
    self.energy_color = energy_color
    self.energy_amount = energy_amount

  def use(self, encounter):
    encounter.player.conditions[self.energy_color] + self.energy_amount
    self.charges -= 1

  def render(self):
    return colorize(f"{self.energy_color.title()} Potion: Gain {self.energy_amount} {self.energy_color} energy.")