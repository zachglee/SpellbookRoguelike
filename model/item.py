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
    self.charges = 1

  def use(self, encounter):
    encounter.player.conditions[self.energy_color] += self.energy_amount
    self.charges -= 1

  def render(self):
    return colorize(f"{self.energy_color.title()} Potion ({self.charges}): Gain {self.energy_amount} {self.energy_color} energy.")
  
class MeleeWeapon(Item):
  def __init__(self, name, charges, damage):
    self.name = name
    self.charges = charges
    self.damage = damage
  
  def use(self, encounter):
    encounter.player.attack(encounter.player.get_immediate(encounter), self.damage)
    self.charges -= 1

  def render(self):
    return colorize(f"{self.name} ({self.charges}): Deal {self.damage} damage.")

class ConditionMeleeWeapon(Item):
  def __init__(self, name, charges, condition, magnitude):
    self.name = name
    self.charges = charges
    self.condition = condition
    self.magnitude = magnitude

  def use(self, encounter):
    encounter.player.get_immediate().conditions[self.condition] += self.magnitude
    self.charges -= 1
  
  def render(self):
    return colorize(f"{self.name} ({self.charges}): Apply {self.magnitude} {self.condition} to immediate.")

class ConditionSelfWeapon(Item):
  def __init__(self, name, charges, condition, magnitude):
    self.name = name
    self.charges = charges
    self.condition = condition
    self.magnitude = magnitude

  def use(self, encounter):
    encounter.player.conditions[self.condition] += self.magnitude
    self.charges -= 1

  def render(self):
    return colorize(f"{self.name} ({self.charges}): Gain {self.magnitude} {self.condition}.")