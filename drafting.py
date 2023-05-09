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
      print(player.render_library())

def reroll_draft_player_library(player, spell_pool):
  rerolls = 3
  render_spell_draft(player)
  while rerolls > 0:
    choice_idx = choose_idx(player.library, f"reroll ({rerolls}) > ")
    if choice_idx is None:
      break
    elif player.library[choice_idx].signature:
      print("You can't reroll a signature spell!")
    else:
      player.library[choice_idx] = generate_library_spells(1, spell_pool=spell_pool)[0]
      rerolls -= 1
      render_spell_draft(player)

def destination_draft(player, destination_node):
  first_spell = SpellbookSpell(destination_node.safehouse.library[0].spell)
  second_spell = SpellbookSpell(destination_node.safehouse.library[1].spell)
  player.spellbook.pages = [SpellbookPage([first_spell]), SpellbookPage([second_spell])]
  edit_page_from_inventory(player, 1)
  edit_page_from_inventory(player, 2)
  # TODO get a random echo spell filled in on each page


def edit_page_from_inventory(player, page_number):
  active_page = player.spellbook.pages[page_number - 1]
  while len(active_page.spells) < 3:
    render_spell_draft(player)
    library_spell = choose_obj(player.library, f"add spell to page {page_number} > ")
    if library_spell is None:
      break
    if library_spell.copies_remaining <= 0:
      print(colored("This spell is out of copies.", "red"))
      continue
    active_page.spells.append(SpellbookSpell(library_spell.spell))
    library_spell.copies_remaining -= 1

def safehouse_library_draft(player, safehouse, copies=3):
  print(player.render_library())
  print(safehouse.render())
  if len(player.library) > player.library_capacity:
    input(colored("You no space left in your library...", "red"))
    return
  copied_spell = choose_obj(safehouse.library, colored("copy a spell to your library > ", "blue"))
  if copied_spell:
    player.library.append(LibrarySpell(copied_spell.spell, copies=copies))
    print(f"Copied: {copied_spell.render()}")
  else:
    print("No spell copied.")