
from termcolor import colored
from model.spellbook import Spellbook
from model.ritual import Ritual


class Grimoire:
  def __init__(self, name, author, spellbook: Spellbook, ritual: Ritual) -> None:
    self.name = name
    self.author = author
    self.spellbook = spellbook
    self.ritual = ritual

    self.uses = 1
  
  def render(self):
    header = f"~~~~ {colored(self.name, 'magenta')} by {colored(self.author, 'green')} ~~~~"
    ritual_str = self.ritual.render() if self.ritual else "[No Ritual]"
    spellbook_str = self.spellbook.render()
    return "\n".join([header, ritual_str, spellbook_str])
  
  def render_preview(self):
    return f"{colored(self.name, 'magenta')} by {colored(self.author, 'green')}"