import random
from termcolor import colored
from model.spellbook import SpellbookPage, SpellbookSpell, LibrarySpell
from utils import choose_obj, numbered_list, choose_idx, ws_input, ws_print
from sound_utils import play_sound
from generators import generate_library_spells

async def render_spell_draft(player, editing_page_idx, websocket=None):
    await ws_print("-------- Current Spellbook --------", websocket)
    await ws_print(player.spellbook.render(editing_page_idx=editing_page_idx), websocket)
    if player.library:
      await ws_print(player.render_library(), websocket)

def draft_player_library(player, spell_pool, randoms=1, picks=2, options_per_pick=2):
  # Get random spells from pool
  random_spells = generate_library_spells(randoms, spell_pool=spell_pool, copies=2)
  player.library += random_spells
  print(player.render_library())
  # Get picks from pool
  all_choices = generate_library_spells(picks * options_per_pick, spell_pool=spell_pool, copies=1)
  for i in range(picks):
    choices = all_choices[i * options_per_pick : (i + 1) * options_per_pick]
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

async def encounter_draft(player, num_pages=2, page_capacity=3):
  play_sound("build-spellbook.mp3")
  player.spellbook.pages = [SpellbookPage([]) for i in range(num_pages)]
  for i in range(num_pages):
    await edit_page_from_inventory(player, i+1, page_capacity=page_capacity, websocket=player.websocket)

async def edit_page_from_inventory(player, page_number, page_capacity=3, websocket=None):
  active_page = player.spellbook.pages[page_number - 1]
  while len(active_page.spells) < page_capacity:
    await render_spell_draft(player, editing_page_idx=page_number-1, websocket=websocket)
    capacity_str = f"({len(active_page.spells) + 1} of {page_capacity})"
    if len(active_page.spells) + 1 == page_capacity:
      capacity_str = colored(capacity_str, "red")
    else:
      capacity_str = colored(capacity_str, "green")
    library_spell = await choose_obj(player.library, f"add spell to page {page_number} {capacity_str} > ", websocket)
    if library_spell is None:
      break
    if library_spell.copies_remaining <= 0:
      await ws_print(colored("This spell is out of copies.", "red"), websocket)
      continue
    active_page.spells.append(SpellbookSpell(library_spell.spell))
    library_spell.copies_remaining -= 1
    play_sound("write-spell.mp3")
