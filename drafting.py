from copy import deepcopy
import random
from model.grimoire import Grimoire
from termcolor import colored
from model.spellbook import Spellbook, SpellbookPage, SpellbookSpell
from utils import choose_obj, numbered_list, ws_input, ws_print
from sound_utils import play_sound

async def render_spell_draft(player, editing_page_idx, websocket=None):
    await ws_print("-------- Current Spellbook --------", websocket)
    await ws_print(player.spellbook.render(editing_page_idx=editing_page_idx), websocket)
    if player.library:
      await ws_print(player.render_library(), websocket)

async def encounter_draft(player, num_pages=2, page_capacity=3):
  play_sound("build-spellbook.mp3")
  player.spellbook.pages = [SpellbookPage([]) for i in range(num_pages)]
  for i in range(num_pages):
    await add_page(player, i+1, page_capacity=3)
  # remove spent spells from library
  player.library = [ls for ls in player.library if ls.copies_remaining > 0 or ls.signature]

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
    play_sound("write-spell.mp3")


async def build_grimoire(player, num_pages=2):
  spellbook = Spellbook([SpellbookPage([]) for i in range(num_pages)])
  for i in range(num_pages):
    await ws_print(spellbook.render(), player.websocket)
    await ws_print(player.render_archive(), player.websocket)
    from_archive_page = await choose_obj(player.archived_pages, f"Add a page to your grimoire ({i+1} of {num_pages}) > ", player.websocket)
    if from_archive_page is None:
      continue
    spellbook.pages[i] = from_archive_page
    player.archived_pages.remove(from_archive_page)
  
  leveled_rituals = [ritual for ritual in player.rituals if ritual.level > 0]
  await ws_print(numbered_list(leveled_rituals), player.websocket)
  ritual = await choose_obj(leveled_rituals, "Choose 1 ritual to add to your grimoire > ", player.websocket)

  name = await ws_input("Name your grimoire > ", player.websocket)

  return Grimoire(name, player.name, spellbook, deepcopy(ritual))
