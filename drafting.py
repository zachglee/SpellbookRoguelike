import random
from termcolor import colored
from model.spellbook import SpellbookPage, SpellbookSpell, LibrarySpell
from utils import choose_obj, numbered_list, choose_idx
from sound_utils import play_sound
from generators import generate_library_spells

def render_spell_draft(player, archive=False):
    print("-------- Current Spellbook --------")
    print(player.spellbook.render())
    if archive:
      print(player.spellbook.render_archive())
    if player.library:
      print(player.render_library())

def draft_player_library(player, spell_pool):
  # Get 2 more random spells
  other_spells = generate_library_spells(1, spell_pool=spell_pool)
  player.library += other_spells
  print(player.render_library())
  for i in range(6):
    # Choose 1 of 2 spells
    choices = generate_library_spells(2, spell_pool=spell_pool)
    print("---\n" + numbered_list(choices))
    choice = choose_obj(choices, "Which spell have you been studying > ")
    if choice:
      player.library.append(choice)

def destination_draft(player, destination_node):
  play_sound("build-spellbook.mp3")
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
    play_sound("write-spell.mp3")

def safehouse_library_draft(player, safehouse, copies=3, spell_pool=[]):
  print(player.render_library())
  if len(player.library) >= player.library_capacity:
    input(colored("You have no space left in your library...", "red"))
    return
  choices = [random.choice(safehouse.library),
             random.choice(generate_library_spells(2, spell_pool=spell_pool))]
  print("---\n" + numbered_list(choices))
  copied_spell = choose_obj(choices, colored("copy a spell to your library > ", "blue"))
  if copied_spell:
    library_spell = LibrarySpell(copied_spell.spell, copies=3)
    library_spell.copies_remaining = copies
    player.library.append(library_spell)

    print(f"Copied: {copied_spell.render()}")
    play_sound("copy-spell.mp3")
  else:
    print("No spell copied.")