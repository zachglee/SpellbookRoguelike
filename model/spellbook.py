from termcolor import colored

class SpellbookSpell:
  def __init__(self, spell):
    self.spell = spell
    self.charges = 2
    self.max_charges = 3
    self.echoing = None
    self.exhausted = False
  
  def recharge(self):
    self.charges = min(self.charges + 1, self.max_charges)

  def render(self):
    rendered_str = self.spell.replace("Red", colored("Red", "red"))
    rendered_str = rendered_str.replace("Gold", colored("Gold", "yellow"))
    rendered_str = rendered_str.replace("Blue", colored("Blue", "blue"))
    rendered_str = rendered_str.replace("Green", colored("Green", "green"))
    rendered_str = rendered_str.replace("Purple", colored("Purple", "magenta"))
    rendered_str = rendered_str.replace("Consumer", colored("Consumer", "magenta"))
    rendered_str = rendered_str.replace("Producer", colored("Producer", "green"))
    rendered_str = rendered_str.replace("Converter", colored("Converter", "cyan"))

    echoing_prefix = colored('~' * self.echoing, 'blue') if self.echoing else ''

    if "Passive" in self.spell:
      charges_prefix = "*"
    else:
      charges_prefix = f"({self.charges}/{self.max_charges})"

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
    return "\n".join(f"{i + 1} - {spell.render()}" for i, spell in enumerate(self.spells))

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
  def current_page(self):
    return self.pages[self.current_page_idx]

  def switch_page(self):
    self.current_page_idx = (self.current_page_idx + 1) % len(self.pages)

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
