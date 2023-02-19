import random
from model.spellbook import LibrarySpell, SpellbookSpell
from content.enemies import enemy_sets
from content.rest_actions import rest_actions, rerolls
from content.spells import spells, red_page_sets, blue_page_sets, gold_page_sets

def generate_spell_pool():
  random.shuffle(red_page_sets)
  random.shuffle(blue_page_sets)
  random.shuffle(gold_page_sets)
  red_spell_pool = sum(sum(red_page_sets[:2], []), [])
  blue_spell_pool = sum(sum(blue_page_sets[:2], []), [])
  gold_spell_pool = sum(sum(gold_page_sets[:2], []), [])
  spell_pool = red_spell_pool + blue_spell_pool + gold_spell_pool
  return spell_pool

def generate_library_spells(size):
  random.shuffle(spells)
  return [LibrarySpell(sp) for sp in spells[:size]]

def generate_spellbook_spells(size):
  random.shuffle(spells)
  return [SpellbookSpell(sp) for sp in spells[:size]]
