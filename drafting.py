from copy import deepcopy
import math
import random
from termcolor import colored
from generators import all_reachable
from model.spellbook import LibrarySpell, SpellbookPage, SpellbookSpell
from utils import choose_obj, numbered_list, ws_input, ws_print
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

async def haven_rolling_draft(player, game_state):
  haven = game_state.haven
  for ls in player.personal_spells:
    ls.copies_remaining = ls.max_copies_remaining
  draft_pool = [ls for ls in haven.library if ls.copies_remaining > 0] + player.personal_spells
  if len(draft_pool) < 10 or not all_reachable(draft_pool):
    await ws_input("Refreshing the draft pool...", player.websocket)
    for ls in haven.library:
      ls.copies_remaining = ls.max_copies_remaining
    return await haven_rolling_draft(player, game_state)
  draft_window = random.sample(draft_pool, 5)
  draft_pool_remaining = [ls for ls in draft_pool if ls not in draft_window]
  rerolls_remaining = 3

  while True:
    await ws_print(haven.render_rituals(), player.websocket)
    await ws_print("-------- CURRENT DRAFT POOL --------\n" + numbered_list(draft_window), player.websocket)
    await ws_print("\n" + player.render_library(), player.websocket)
    choice = await choose_obj(draft_window, f"Choose a spell to add to library ({rerolls_remaining} rerolls) > ", player.websocket)

    if isinstance(choice, str) and choice.startswith("reroll") and rerolls_remaining > 0:
      reroll_target_idx = int(choice.split(" ")[1]) - 1
      draft_window.pop(reroll_target_idx)
      rerolls_remaining -= 1
    elif choice is None:
      break
    else:
      player.library.append(deepcopy(choice))
      draft_window.remove(choice)
      choice.copies_remaining -= 1

    if draft_pool_remaining:
      new_spell_for_window = random.choice(draft_pool_remaining)
      draft_window.append(new_spell_for_window)
      draft_pool_remaining.remove(new_spell_for_window)
    else:
      await ws_print(colored("No more spells remaining in the draft pool.", "red"), player.websocket)

async def haven_library_draft(player, game_state):
  haven = game_state.haven

  chosen_spells = []
  while True:
    drafting_library = haven.library + player.personal_spells
    await ws_print(haven.render(player=player), player.websocket)
    await ws_print(player.render_library(), player.websocket)
    choice = await choose_obj(drafting_library, "Choose a spell to add to library > ", player.websocket)

    if choice is None and len(chosen_spells) > 0:
      break

    if choice.copies_remaining <= 0:
      await ws_print(colored("This spell is out of copies.", "red"), player.websocket)
      continue

    # if player.material < choice.material_cost:
    #   await ws_print(colored("Not enough material!", "red"), player.websocket)
    #   continue

    player.library.append(deepcopy(choice))
    chosen_spells.append(choice)
    # player.material -= choice.material_cost
    choice.copies_remaining -= 1
  
  # NOTE: We're not doing material cost adjustment right now
  # Do admin to adjust spell costs
  # increase_cost_spells = random.sample(chosen_spells, 3) if len(chosen_spells) > 3 else chosen_spells
  # for spell in increase_cost_spells:
  #   spell.material_cost += 3
  # no_recharge_spell = random.choice(chosen_spells)
  # unchosen_spells = [ls for ls in drafting_library if ls not in chosen_spells]
  # total_discounts = 0
  # while total_discounts < 6:
  #   spell_to_discount = random.choice(unchosen_spells)
  #   if spell_to_discount.material_cost > 0:
  #     spell_to_discount.material_cost -= 1
  #     total_discounts += 1

  # Remove some chosen spells from the haven library
  num_spells_to_remove = 1 if len(chosen_spells) <= 6 else 2
  spells_to_remove = random.sample([ls for ls in chosen_spells if ls in haven.library], num_spells_to_remove)
  for ls in spells_to_remove:
    await ws_input(colored("This spell is now spent: ", "red") + f"{ls.spell.description}.", player.websocket)
    haven.library.remove(ls)

  for ls in drafting_library:
    # if ls is not no_recharge_spell:
    ls.copies_remaining = ls.max_copies_remaining

  await ws_print(haven.render(player=player), player.websocket)

async def draft_spell_for_haven(game_state, websocket):
    # get a new spell for the haven
    await ws_print(game_state.haven.render(), websocket)
    choices = random.sample(random.choice(game_state.map.region_drafts).spell_pool, 3)
    await ws_print("\n" + numbered_list(choices), websocket)
    chosen_spell = await choose_obj(choices, "Choose a spell to add to the haven library > ", websocket)
    game_state.haven.library.append(LibrarySpell(chosen_spell))

async def draft_ritual_for_haven(game_state, websocket):
    # add a new ritual to the haven
    ritual_choices = [faction.ritual for faction in game_state.map.factions]
    await ws_print(game_state.haven.render(), websocket)
    await ws_print("\n" + numbered_list(ritual_choices), websocket)
    chosen_ritual = await choose_obj(ritual_choices, "Choose a ritual to add to the haven > ", websocket)
    game_state.haven.rituals.append(chosen_ritual)