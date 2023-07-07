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
  
class CustomItem(Item):
  def __init__(self, name, charges, description, use_commands,
               generate_commands_pre=lambda e, t: [], time_cost=1):
    super().__init__(charges, description)
    self.name = name
    self.use_commands = use_commands
    self.time_cost = time_cost
    self.generate_commands_pre = generate_commands_pre

  def use(self, encounter):
    # generate commands pre-execution
    generated_commands_pre = self.generate_commands_pre(encounter, None)
    raw_commands = self.use_commands + generated_commands_pre

    for command in raw_commands:
      encounter.handle_command(command)
    self.charges -= 1

  def render(self):
    return colorize(f"{self.name} ({self.charges}): {self.description}")

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
    encounter.player.get_immediate(encounter).conditions[self.condition] += self.magnitude
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