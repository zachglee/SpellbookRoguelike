import random
from termcolor import colored
from utils import choose_idx, choose_obj, numbered_list
from model.spellbook import SpellbookPage, SpellbookSpell

class SpellDraft():
  def __init__(self, player, universe):
    self.player = player
    self.universe = universe
  
  def render_spell_draft(self, archive=False):
    print("-------- Current Spellbook --------")
    print(self.player.spellbook.render())
    if archive:
      print(self.player.spellbook.render_archive())
    if self.player.inventory:
      print(f"\n-------- Current {colored('Inventory', 'cyan')} --------")
      print(numbered_list(self.player.inventory))

  def generate_spells(self, n):
    return [SpellbookSpell(random.choice(self.universe)) for _ in range(n)]


  def reroll_draft_spellbook_page(self):
    self.player.rerolls += 1
    new_page = SpellbookPage(self.generate_spells(4))
    self.player.spellbook.pages.append(new_page)
    self.render_spell_draft()
    while self.player.rerolls > 0:
      choice_idx = choose_idx(new_page.spells, f"reroll ({self.player.rerolls}) > ")
      if choice_idx is not None:
        new_page.spells[choice_idx] = self.generate_spells(1)[0]
        self.player.rerolls -= 1
        self.render_spell_draft()
      else:
        break

  def archive_draft_spellbook_page(self):
    print("-------- Current Spellbook --------")
    print(self.player.spellbook.render())
    print("-------- Archive --------")
    print(self.player.spellbook.render_archive())
    drafted_idx = choose_idx(self.player.spellbook.archive, "draft a page > ")
    new_page = self.player.spellbook.archive.pop(drafted_idx)
    self.player.spellbook.pages.append(new_page)

    
