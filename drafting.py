import random
from termcolor import colored
from model.spellbook import SpellbookPage, SpellbookSpell, LibrarySpell
from utils import choose_obj, numbered_list, choose_idx
from generators import generate_library_spells

def render_spell_draft(player, archive=False):
    print("-------- Current Spellbook --------")
    print(player.spellbook.render())
    if archive:
      print(player.spellbook.render_archive())
    if player.library:
      print(f"-------- Current {colored('Library', 'cyan')} --------")
      print(numbered_list(player.library))

def reroll_draft_player_library(player):
  rerolls = 3
  render_spell_draft(player)
  while rerolls > 0:
    choice_idx = choose_idx(player.library, f"reroll ({rerolls}) > ")
    if choice_idx is not None:
      player.library[choice_idx] = generate_library_spells(1)[0]
      rerolls -= 1
      render_spell_draft(player)
    else:
      break

def destination_draft(player, destination_node):
  first_spell = SpellbookSpell(destination_node.safehouse.library[0].spell)
  second_spell = SpellbookSpell(destination_node.safehouse.library[1].spell)
  player.spellbook.pages = [SpellbookPage([first_spell]), SpellbookPage([second_spell])]
  edit_page_from_inventory(player, 1)
  edit_page_from_inventory(player, 2)
  # TODO get a random echo spell filled in on each page


def edit_page_from_inventory(player, page_number):
  active_page = player.spellbook.pages[page_number - 1]
  available_spells = [spell for spell in player.library]
  while len(active_page.spells) < 3:
    render_spell_draft(player)
    library_spell_idx = choose_obj(available_spells, f"add spell to page {page_number} > ")
    if library_spell_idx is None:
      break
    library_spell = available_spells.pop(library_spell_idx)
    active_page.spells.append(SpellbookSpell(library_spell.spell))
    library_spell.copies_remaining -= 1
    player.library = [spell for spell in player.library if spell.copies_remaining > 0]

def safehouse_library_draft(player, safehouse):
  print(safehouse.render())
  copied_spell = choose_obj(safehouse.library, colored("copy a spell to your library > ", "blue"))
  if copied_spell:
    player.library.append(LibrarySpell(copied_spell.spell))
    copied_spell.copy_count += 1
    print(f"Copied: {copied_spell.render()}")
  else:
    print("No spell copied.")