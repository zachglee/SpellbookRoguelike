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
  # mode = await choose_str(["new", "archive"], "Create new page or use page from archive? > ", player.websocket)
  if len(player.library) > 1:
    mode = "new"
  else:
    mode = "archive"

  if mode is None:
    return SpellbookPage([])
  if mode == "new":
    await edit_page_from_library(player, page_number, page_capacity=page_capacity)
  # NOTE: I think I'm getting rid of this in favor of making entire spellbooks
  # elif mode == "archive":
  #   # print all archived pages
  #   available_archived_pages = [page for page in player.archived_pages if not page.spent]
  #   await ws_print(numbered_list(available_archived_pages, use_headers=True), player.websocket)
  #   from_archive_page = await choose_obj(available_archived_pages, "Which page do you want to use? > ", player.websocket)
  #   # from_archive_page.spent = True # Now that arvhive mode is only for boss, let's not punish you so hard
  #   player.spellbook.pages[page_number - 1] = deepcopy(from_archive_page)


async def edit_page_from_library(player, page_number, page_capacity=3) -> SpellbookPage:
  active_page = player.spellbook.pages[page_number - 1]
  while len(active_page.spells) < page_capacity:
    await render_spell_draft(player, editing_page_idx=page_number-1, websocket=player.websocket)
    capacity_str = f"({len(active_page.spells) + 1} of {page_capacity})"
    if len(active_page.spells) + 1 == page_capacity:
      capacity_str = colored(capacity_str, "red")
    else:
      capacity_str = colored(capacity_str, "green")
    library_spell = await choose_obj(player.library, f"add spell to page {page_number} {capacity_str} > ", player.websocket)
    if library_spell is None:
      break
    if library_spell.copies_remaining <= 0:
      await ws_print(colored("This spell is out of copies.", "red"), player.websocket)
      continue
    active_page.spells.append(SpellbookSpell(library_spell.spell))
    library_spell.copies_remaining -= 1
    await ws_play_sound("write-spell.mp3", player.websocket)

async def haven_library_draft(player, game_state):
  haven = game_state.haven
  for ls in haven.library:
    ls.copies_remaining = ls.max_copies_remaining

  chosen_spells = []
  while True:
    await ws_print(haven.render(), player.websocket)
    await ws_print(player.render_library(), player.websocket)
    choice = await choose_obj(haven.library, "Choose a spell to add to library > ", player.websocket)

    if choice is None:
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

  await game_state.wait_for_teammates(player.id, f"havenlibrarydraft")
    
  
  # Do admin to adjust spell costs
  increase_cost_spells = random.sample(chosen_spells, 3) if len(chosen_spells) > 3 else chosen_spells
  for spell in increase_cost_spells:
    spell.material_cost += 3
  unchosen_spells = [ls for ls in haven.library if ls not in chosen_spells]
  total_discounts = 0
  while total_discounts < 9:
    spell_to_discount = random.choice(unchosen_spells)
    if spell_to_discount.material_cost > 0:
      spell_to_discount.material_cost -= 1
      total_discounts += 1

  await ws_print(haven.render(), player.websocket)