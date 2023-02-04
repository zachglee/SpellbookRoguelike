import random
from termcolor import colored
from model.spellbook import SpellbookPage, SpellbookSpell

class SpellDraft():
  def __init__(self, player, universe):
    self.player = player
    self.universe = universe
    self.pool = []
  
  def render_spell_draft(self, archive=False):
    print("-------- Current Spellbook --------")
    print(self.player.spellbook.render())
    if archive:
      print(self.player.spellbook.render_archive())
    if self.player.inventory:
      print(f"\n-------- Current {colored('Inventory', 'cyan')} --------")
      print("\n".join(f"- {spell.render()}" for spell in self.player.inventory))
    if self.pool:
      print(f"\n-------- Current {colored('Pool', 'magenta')} --------")
      print("\n".join(f"- {spell.render()}" for spell in self.pool))

  def generate_spells(self, n):
    return [SpellbookSpell(random.choice(self.universe)) for _ in range(n)]

  def draft_from_pool(self, prompt=f"draft from {colored('pool', 'magenta')} > ") -> SpellbookSpell:
    while True:
      choice = input(prompt)
      if choice.isnumeric():
        idx = int(choice)
        return self.pool.pop(idx - 1)

  def draft_from_inventory(self, prompt=f"draft from {colored('inventory', 'cyan')} > ") -> SpellbookSpell:
    while True:
      try:
        choice = input(prompt)
        if choice.isnumeric():
          idx = int(choice)
          return self.player.inventory.pop(idx - 1)
      except (IndexError, TypeError, ValueError) as e:
        print(e)
  
  def draft_spellbook_page(self):
    new_page = SpellbookPage([])
    self.player.spellbook.pages.append(new_page)
    while len(new_page.spells) < 3:
      self.pool = self.generate_spells(3)
      self.render_spell_draft()
      print()
      new_page.spells.append(self.draft_from_pool())
    self.render_spell_draft()
    new_page.spells.append(self.draft_from_inventory())

  def reroll_draft_spellbook_page(self, n_rerolls=3):
    new_page = SpellbookPage(self.generate_spells(4))
    self.player.spellbook.pages.append(new_page)
    self.render_spell_draft()
    while n_rerolls > 0:
      try:
        choice = input(f"reroll ({n_rerolls}) > ")
        if choice == "done":
          break
        choice_idx = int(choice) - 1
        new_page.spells[choice_idx] = self.generate_spells(1)[0]
        n_rerolls -= 1
        self.render_spell_draft()
      except (TypeError, IndexError, ValueError) as e:
        print(e)

  def archive_draft_spellbook_page(self):
    print("-------- Current Spellbook --------")
    print(self.player.spellbook.render())
    print("-------- Archive --------")
    print(self.player.spellbook.render_archive())
    while True:
      try:
        choice = input(f"draft a page > ")
        if choice == "done":
          break
        new_page = self.player.spellbook.archive.pop(int(choice) - 1)
        self.player.spellbook.pages.append(new_page)
        break
      except (ValueError, IndexError, TypeError) as e:
        print(e)


  def draft_to_inventory(self, n):
    for _ in range(n):
      self.pool = self.generate_spells(3)
      self.render_spell_draft()
      print()
      self.player.inventory.append(self.draft_from_pool(f"draft to {colored('inventory', 'cyan')} > "))
    
