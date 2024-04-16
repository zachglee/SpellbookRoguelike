from copy import deepcopy
import random
from termcolor import colored
from model.spellbook import SpellbookPage, SpellbookSpell
from utils import choose_obj, ws_print
from sound_utils import ws_play_sound

async def render_spell_draft(player, editing_page_idx, websocket=None):
    await ws_print("-------- Current Spellbook --------", websocket)
    await ws_print(player.spellbook.render(editing_page_idx=editing_page_idx), websocket)
    if player.library:
      await ws_print(player.render_library(), websocket)

async def encounter_draft(player, num_pages=3, page_capacity=3):
  await ws_play_sound("build-spellbook.mp3", player.websocket)
  player.spellbook.pages = [SpellbookPage([]) for i in range(num_pages)]
  for ls in player.library:
    ls.copies_remaining = ls.max_copies_remaining
  for i in range(num_pages):
    await add_page(player, i+1, page_capacity=page_capacity)
  # remove spent spells from library
  # NOTE: keep spells when they go to 0 charges, because your library is persistent across
  # combats now
  # player.library = [ls for ls in player.library if ls.copies_remaining > 0 or ls.signature]
  player.spellbook.pages = [page for page in player.spellbook.pages if page.spells]

async def add_page(player, page_number, page_capacity=3):
  await edit_page_from_library(player, page_number, page_capacity=page_capacity)


async def edit_page_from_library(player, page_number, page_capacity=3) -> SpellbookPage:
  active_page = player.spellbook.pages[page_number - 1]
  while len(active_page.spells) < page_capacity:
    await render_spell_draft(player, editing_page_idx=page_number-1, websocket=player.websocket)
    capacity_str = f"({len(active_page.spells) + 1} of {page_capacity})"
    if len(active_page.spells) + 1 == page_capacity:
      capacity_str = colored(capacity_str, "red")
    else:
      capacity_str = colored(capacity_str, "green")
    library_spell = await choose_obj(player.library, f"add spell to page {page_number} {capacity_str} (!reset to undo) > ", player.websocket)
    if library_spell is None:
      break
    if library_spell == "reset":
      for ss in active_page.spells:
        original_library_spell = next((ls for ls in player.library if ls.spell == ss.spell), None)
        if original_library_spell:
          original_library_spell.copies_remaining += 1
      active_page.spells = []
      continue
    if library_spell.copies_remaining <= 0:
      await ws_print(colored("This spell is out of copies.", "red"), player.websocket)
      continue
    active_page.spells.append(SpellbookSpell(library_spell.spell))
    library_spell.copies_remaining -= 1
    await ws_play_sound("write-spell.mp3", player.websocket)

async def haven_library_draft(player, game_state):
  haven = game_state.haven

  chosen_spells = []
  while True:
    await ws_print(haven.render(), player.websocket)
    await ws_print(player.render_library(), player.websocket)
    choice = await choose_obj(haven.library, "Choose a spell to add to library > ", player.websocket)

    if choice is None and len(chosen_spells) > 0:
      break

    if choice.copies_remaining <= 0:
      await ws_print(colored("This spell is out of copies.", "red"), player.websocket)
      continue

    if player.material < choice.material_cost:
      await ws_print(colored("Not enough material!", "red"), player.websocket)
      continue

    player.library.append(deepcopy(choice))
    chosen_spells.append(choice)
    player.material -= choice.material_cost
    choice.copies_remaining -= 1
  
  # Do admin to adjust spell costs
  increase_cost_spells = random.sample(chosen_spells, 3) if len(chosen_spells) > 3 else chosen_spells
  for spell in increase_cost_spells:
    spell.material_cost += 3
  no_recharge_spell = random.choice(chosen_spells)
  unchosen_spells = [ls for ls in haven.library if ls not in chosen_spells]
  total_discounts = 0
  while total_discounts < 6:
    spell_to_discount = random.choice(unchosen_spells)
    if spell_to_discount.material_cost > 0:
      spell_to_discount.material_cost -= 1
      total_discounts += 1

  for ls in haven.library:
    if ls is not no_recharge_spell:
      ls.copies_remaining = ls.max_copies_remaining

  await ws_print(haven.render(), player.websocket)