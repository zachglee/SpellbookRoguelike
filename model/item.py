from utils import colorize
from model.spellbook import SpellbookSpell

class Item:
  def __init__(self, charges, description):
    self.description = description
    self.charges = charges
    self.max_charges = charges
    self.time_cost = 1
    self.material_cost = None
    self.belonged_to = None

  def use(self, encounter):
    pass

  def render(self):
    return self.description
  
class CustomItem(Item):
  def __init__(self, name, charges, description, use_commands,
               generate_commands_pre=lambda e, t: [], time_cost=1, material_cost=None, rare=False, personal=False):
    super().__init__(charges, description)
    self.name = name
    self.use_commands = use_commands
    self.time_cost = time_cost
    self.generate_commands_pre = generate_commands_pre
    self.material_cost = material_cost
    self.rare = rare
    self.personal = personal

  def use(self, encounter):
    # generate commands pre-execution
    generated_commands_pre = self.generate_commands_pre(encounter, None)
    raw_commands = self.use_commands + generated_commands_pre

    for command in raw_commands:
      encounter.handle_command(command)
    self.charges -= 1

  def render(self):
    belonged_to_str = f"{self.belonged_to}'s " if self.belonged_to else ""
    return colorize(f"{belonged_to_str}{self.name} ({self.charges}): {self.description}")

class SpellPotion(Item):
  def __init__(self, spell):
    self.spell = spell
    self.charges = 1
    self.time_cost = 1

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
    self.time_cost = 1
    self.personal = False
    self.rare = False
    self.name = f"{self.energy_color.title()} Potion"

  def use(self, encounter):
    encounter.player.conditions[self.energy_color] += self.energy_amount
    self.charges -= 1

  def render(self):
    return colorize(f"{self.energy_color.title()} Potion ({self.charges}): Gain {self.energy_amount} {self.energy_color} energy.")
