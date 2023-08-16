import os
from termcolor import colored
from utils import numbered_list, get_combat_entities, energy_color_map, energy_pip_symbol
from sound_utils import play_sound

class Spell:
  def __init__(self, rules_text, color, type, conversion_color=None,
               raw_commands=None, targets=None,
               generate_commands_pre=lambda e, t: [], generate_commands_post=lambda e, t: [],
               triggers_on=lambda encounter, event: False):
    self.rules_text = rules_text
    self.color = color
    self.type = type
    self.conversion_color = conversion_color
    self.raw_commands = raw_commands or []
    self.sound_file = None
    self.targets = targets or []
    self.generate_commands_pre = generate_commands_pre
    self.generate_commands_post = generate_commands_post
    self.triggers_on = triggers_on

    if self.type == "Producer":
      self.raw_commands.append(f"{color} p 1")
    if self.type == "Converter" and conversion_color is not None:
      self.raw_commands.append(f"{conversion_color} p 1")
    if self.type == "Consumer":
      file_stem = f"{self.color}-consumer-cast"
      self.sound_file = f"{file_stem}.mp3" if os.path.isfile(f"assets/sounds/{file_stem}.mp3") else f"{file_stem}.wav"

  def cast(self, encounter, cost_energy=True, cost_charges=True, trigger_output=None):
    if cost_energy:
      if self.type in ["Converter", "Consumer"]:
        # TODO: eventually enforce that you must have the correct energy
        encounter.player.conditions[self.color] -= 1
    
    # choose targets
    chosen_targets = {}
    for target_placeholder in self.targets:
      if target_placeholder in ["_"]:
        # FIXME: Add error handling for invalid targets
        target_ref = input(f"Choose a target for {target_placeholder} > ")
      else:
        target_ref = target_placeholder
      target_entities = get_combat_entities(encounter, target_ref)
      if len(target_entities) > 1:
        raise ValueError("Targeting more than one entity is not yet supported.")
      else:
        target_entities = target_entities[0]
      chosen_targets[target_placeholder] = (target_ref, target_entities) 

    # generate commands pre-execution
    generated_commands_pre = self.generate_commands_pre(encounter, chosen_targets)
    cast_commands = self.raw_commands + generated_commands_pre

    # main execution
    for cmd in cast_commands:
      processed_command = cmd
      for placeholder, (target, _) in chosen_targets.items():
        processed_command = processed_command.replace(placeholder, target)
      processed_command = processed_command.replace("^", str(trigger_output))
      encounter.handle_command(processed_command)

    # generate and execute commands post main execution (for effects like 'if this kills')
    generated_commands_post = self.generate_commands_post(encounter, chosen_targets)
    for cmd in generated_commands_post:
      encounter.handle_command(cmd)

    if sound_file := self.sound_file:
      play_sound(sound_file, channel=3)

  @property
  def description(self):
    color_pip = colored(energy_pip_symbol, energy_color_map[self.color.lower()])
    if self.type == "Consumer":
      return f"({color_pip}): {self.rules_text}"
    elif self.type == "Producer":
      producer_color_marker = colored("^", energy_color_map[self.color.lower()])
      return f"{producer_color_marker} {self.rules_text}"
    elif self.type == "Converter":
      convert_to_pip = colored(energy_pip_symbol, energy_color_map[self.conversion_color.lower()])
      return f"{color_pip}➜{convert_to_pip}: {self.rules_text}"
    elif self.type == "Passive":
      passive_marker = colored("#", energy_color_map[self.color.lower()])
      return f"{passive_marker} {self.rules_text}"

  def preview(self, length=24):
    return self.description[:length] + ("..." if len(self.description) > length else "")

  def __repr__(self):
    return self.description

class LibrarySpell:
  def __init__(self, spell: Spell, copies=3, signature=False):
    self.spell = spell
    self.signature = signature
    self.copies_remaining = copies
    self.max_copies_remaining = copies
  
  def render(self):
    rendered_str = self.spell.description.replace("Red", colored("Red", "red"))
    rendered_str = rendered_str.replace("Gold", colored("Gold", "yellow"))
    rendered_str = rendered_str.replace("Blue", colored("Blue", "blue"))
    rendered_str = rendered_str.replace("Green", colored("Green", "green"))
    rendered_str = rendered_str.replace("Purple", colored("Purple", "magenta"))
    rendered_str = rendered_str.replace("Consumer", colored("Consumer", "magenta"))
    rendered_str = rendered_str.replace("Producer", colored("Producer", "green"))
    rendered_str = rendered_str.replace("Converter", colored("Converter", "cyan"))
    rendered_str = rendered_str.replace("Passive", colored("Passive", "yellow"))
    copies_remaining_part = f"[{self.copies_remaining}/{self.max_copies_remaining}]"
    if self.signature:
      copies_remaining_part = colored(copies_remaining_part, "magenta")
    return f"{copies_remaining_part} {rendered_str}"

class SpellbookSpell:
  def __init__(self, spell: Spell):
    self.spell = spell
    self.charges = 2
    self.max_charges = 3
    self.echoing = None
    self.exhausted = False

  def recharge(self):
    self.charges = min(self.charges + 1, self.max_charges)

  def cast(self, encounter, cost_energy=True, cost_charges=True):
    if cost_charges:
      self.charges -= 1
    self.exhausted = True
    self.spell.cast(encounter, cost_energy=cost_energy, cost_charges=cost_charges)

  def render(self):
    rendered_str = self.spell.description.replace("Red", colored("Red", "red"))
    rendered_str = rendered_str.replace("Gold", colored("Gold", "yellow"))
    rendered_str = rendered_str.replace("Blue", colored("Blue", "blue"))
    rendered_str = rendered_str.replace("Green", colored("Green", "green"))
    rendered_str = rendered_str.replace("Purple", colored("Purple", "magenta"))
    rendered_str = rendered_str.replace("Consumer", colored("Consumer", "magenta"))
    rendered_str = rendered_str.replace("Producer", colored("Producer", "green"))
    rendered_str = rendered_str.replace("Converter", colored("Converter", "cyan"))

    if self.spell.type == "Passive":
      charges_prefix = ""
    else:
      charges_prefix = f"({self.charges}/{self.max_charges})"
    if self.exhausted: charges_prefix = colored(f"~{charges_prefix}", "red")

    return f"{charges_prefix} {rendered_str}"

class SpellbookPage:
  def __init__(self, spells):
    self.spells = spells
    self.copy_count = 0
    self.notes = None

  def render(self):
    return numbered_list(self.spells)

class Spellbook:
  def __init__(self, pages):
    self.pages = pages
    self.current_page_idx = 0
    self.archive = []

  @property
  def spells(self):
    spells = []
    for page in self.pages:
      spells += page.spells
    return spells

  @property
  def all_pages(self):
    return self.pages + self.archive

  @property
  def current_page(self):
    return self.pages[self.current_page_idx]

  def switch_page(self):
    self.current_page_idx = (self.current_page_idx + 1) % len(self.pages)
    play_sound("page-flip-1.mp3")

  def render(self, editing_page_idx=None):
    rendered = ""
    for i, page in enumerate(self.pages):
      header = f"Page {i + 1}:"
      if editing_page_idx is not None and i == editing_page_idx:
        header = header + colored(" [EDITING]", "magenta")
      rendered += f"{header}\n" + page.render() + "\n"
    return rendered
  
  def render_current_page(self):
    return f"Current Page ({self.current_page_idx + 1}):\n" + self.current_page.render()

