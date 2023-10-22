import random
from model.spellbook import LibrarySpell, SpellbookSpell
from model.shop import Shop, ShopItem
from content.enemies import enemy_sets
from content.spells import (spells, red_pages, blue_pages, gold_pages,
                            red_page_sets, blue_page_sets, gold_page_sets)
from content.rituals import rituals
from content.items import ancient_key
from content.enemy_factions import factions


def generate_enemy_set_pool(n=10):
  random.shuffle(enemy_sets)
  return enemy_sets[:n]

def generate_spell_pools(n_pools=1):
  random.shuffle(red_pages)
  random.shuffle(blue_pages)
  random.shuffle(gold_pages)
  spell_pools = []
  for i in range(n_pools):
    red_spell_pool = sum(red_pages[i * 2:(i + 1) * 2], [])
    blue_spell_pool = sum(blue_pages[i * 2:(i + 1) * 2], [])
    gold_spell_pool = sum(gold_pages[i * 2:(i + 1) * 2], [])
    spell_pool = red_spell_pool + blue_spell_pool + gold_spell_pool
    spell_pools.append(spell_pool)
  return spell_pools

def generate_faction_sets(n_sets=1, set_size=3, overlap=0):
  random.shuffle(factions)
  return [factions[(i*set_size)-(i*overlap):((i+1)*set_size)-(i*overlap)] for i in range(n_sets)]

def generate_library_spells(size, spell_pool=spells, copies=3):
  sampled_spells = random.sample(spell_pool, size)
  return [LibrarySpell(sp, copies=copies) for sp in sampled_spells]

def generate_spellbook_spells(size, spell_pool=spells):
  random.shuffle(spell_pool)
  return [SpellbookSpell(sp) for sp in spell_pool[:size]]

def generate_rituals(size, ritual_pool=rituals):
  random.shuffle(ritual_pool)
  return [r for r in ritual_pool[:size]]

def generate_shop(n_items, item_pool, key=False):
  random.shuffle(item_pool)
  shop_items = []
  for item in item_pool[:n_items]:
    if item.material_cost:
      stock = 1
      cost = item.material_cost
    elif item.rare:
      stock = 1
      cost = 15
    elif item.name in ["Gold Potion", "Red Potion", "Blue Potion"]:
      stock = 2
      cost = 3
    elif not item.rare:
      stock = 1
      cost = 6
    shop_items.append(ShopItem(item, cost=cost, stock=stock))
  if key:
    shop_items.append(ShopItem(ancient_key, cost=36, stock=1))
  return Shop(shop_items)