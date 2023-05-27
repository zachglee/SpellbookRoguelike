import os
from termcolor import colored
from utils import numbered_list
from sound_utils import play_sound

class Spell:
  def __init__(self, description, color, type, conversion_color=None, cost=None, cast_commands=None):
    self.description = description
    self.color = color
    self.type = type
    self.conversion_color = conversion_color
    self.cost = cost
    self.cast_commands = cast_commands or []
    self.sound_file = None

    if self.type == "Producer":
      self.cast_commands.append(f"{color} p 1")
    if self.type == "Converter" and conversion_color is not None:
      self.cast_commands.append(f"{conversion_color} p 1")
    if self.type == "Consumer":
      file_stem = f"{self.color}-consumer-cast"
      self.sound_file = f"{file_stem}.mp3" if os.path.isfile(f"assets/sounds/{file_stem}.mp3") else f"{file_stem}.wav"

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

  def render(self):
    rendered_str = self.spell.description.replace("Red", colored("Red", "red"))
    rendered_str = rendered_str.replace("Gold", colored("Gold", "yellow"))
    rendered_str = rendered_str.replace("Blue", colored("Blue", "blue"))
    rendered_str = rendered_str.replace("Green", colored("Green", "green"))
    rendered_str = rendered_str.replace("Purple", colored("Purple", "magenta"))
    rendered_str = rendered_str.replace("Consumer", colored("Consumer", "magenta"))
    rendered_str = rendered_str.replace("Producer", colored("Producer", "green"))
    rendered_str = rendered_str.replace("Converter", colored("Converter", "cyan"))

    echoing_prefix = colored('~' * self.echoing, 'blue') if self.echoing else ''

    if self.spell.type == "Passive":
      charges_prefix = "*"
    else:
      charges_prefix = f"({self.charges}/{self.max_charges})"
    if self.echoing: charges_prefix = colored(charges_prefix, "blue")

    return f"{echoing_prefix}{charges_prefix} {rendered_str}"

class SpellbookPage:
  def __init__(self, spells):
    self.spells = spells
    self.copy_count = 0
    self.notes = None
  
  # tick down echoing spells
  def tick_echoes(self):
    for spell in self.spells:
      if spell.echoing is not None:
        spell.echoing -= 1
    self.spells = [spell for spell in self.spells
                   if spell.echoing is None or spell.echoing > 0]

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

  def render(self):
    rendered = ""
    for i, page in enumerate(self.pages):
      rendered += f"Page {i + 1}:\n" + page.render() + "\n"
    return rendered
  
  def render_current_page(self):
    return f"Current Page ({self.current_page_idx + 1}):\n" + self.current_page.render()

  def render_archive(self):
    render_str = ""
    for i, page in enumerate(self.archive):
      render_str += f"Page {i + 1}:\n" + page.render() + "\n"
    return render_str
