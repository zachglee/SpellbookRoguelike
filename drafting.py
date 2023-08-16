import random
from termcolor import colored
from model.spellbook import SpellbookPage, SpellbookSpell, LibrarySpell
from utils import choose_obj, numbered_list, choose_idx
from sound_utils import play_sound
from generators import generate_library_spells

def render_spell_draft(player, editing_page_idx):
    print("-------- Current Spellbook --------")
    print(player.spellbook.render(editing_page_idx=editing_page_idx))
    if player.library:
      print(player.render_library())

def draft_player_library(player, spell_pool, randoms=1, picks=2, choices_per_pick=2):
  # Get random spells from pool
  random_spells = generate_library_spells(randoms, spell_pool=spell_pool, copies=2)
  player.library += random_spells
  print(player.render_library())
  # Get picks from pool
  all_choices = generate_library_spells(picks * choices_per_pick, spell_pool=spell_pool, copies=1)
  for i in range(picks):
    # Choose 1 of 2 spells
    choices = all_choices[i * choices_per_pick : (i + 1) * choices_per_pick]
    print("---\n" + numbered_list(choices))
    choice = choose_obj(choices, "Which spell have you been studying > ")
    if choice:
      player.library.append(choice)

def destination_draft(player, destination_node):
  play_sound("build-spellbook.mp3")
  first_spell = SpellbookSpell(destination_node.safehouse.library[0].spell)
  second_spell = SpellbookSpell(destination_node.safehouse.library[1].spell)
  player.spellbook.pages = [SpellbookPage([first_spell]), SpellbookPage([second_spell])]
  for i in range(destination_node.num_pages):
    edit_page_from_inventory(player, i+1, page_capacity=destination_node.page_capacity)


def edit_page_from_inventory(player, page_number, page_capacity=3):
  active_page = player.spellbook.pages[page_number - 1]
  while len(active_page.spells) < page_capacity:
    render_spell_draft(player, editing_page_idx=page_number-1)
    capacity_str = f"({len(active_page.spells) + 1} of {page_capacity})"
    if len(active_page.spells) + 1 == page_capacity:
      capacity_str = colored(capacity_str, "red")
    else:
      capacity_str = colored(capacity_str, "green")
    library_spell = choose_obj(player.library, f"add spell to page {page_number} {capacity_str} > ")
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
  # TODO remove if unproblematic
  # choices = [random.choice(safehouse.library),
  #            random.choice(generate_library_spells(2, spell_pool=spell_pool))]
  choices = safehouse.library
  print("---\n" + numbered_list(choices))
  copied_spell = choose_obj(choices, colored("copy a spell to your library > ", "blue"))
  if copied_spell:
    library_spell = LibrarySpell(copied_spell.spell, copies=copies)
    library_spell.copies_remaining = copies
    player.library.append(library_spell)

    print(f"Copied: {copied_spell.render()}")
    play_sound("copy-spell.mp3")
  else:
    print("No spell copied.")