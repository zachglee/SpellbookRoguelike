import random
from model.spellbook import LibrarySpell, SpellbookSpell
from model.shop import Shop, ShopItem
from content.enemies import enemy_sets
from content.spells import (spells, red_pages, blue_pages, gold_pages,
                            red_page_sets, blue_page_sets, gold_page_sets)
from content.items import ancient_key, blank_page
from content.enemy_factions import factions


def generate_enemy_set_pool(n=10):
  random.shuffle(enemy_sets)
  return enemy_sets[:n]

def generate_spell_pools(n_pools=1):
  random.shuffle(red_pages)
  random.shuffle(blue_pages)
  random.shuffle(gold_pages)
  spell_pools = []
  for i in range(0, n_pools):
    red_spell_pool = sum(red_pages[i:i + 2], [])
    blue_spell_pool = sum(blue_pages[i:i + 2], [])
    gold_spell_pool = sum(gold_pages[i:i + 2], [])
    spell_pool = red_spell_pool + blue_spell_pool + gold_spell_pool
    spell_pools.append(spell_pool)
  return spell_pools

def generate_faction_sets(n_sets=1, set_size=2, overlap=0, faction_pool=factions):
  random.shuffle(faction_pool)
  pool_size = len(faction_pool)
  return [factions[((i * set_size) - (i * overlap)) % pool_size:
                   (((i+1) * set_size) - (i * overlap)) % (pool_size+1)]
                   for i in range(n_sets)]

def generate_library_spells(size, spell_pool=spells, copies=3):
  sampled_spells = random.sample(spell_pool, size)
  return [LibrarySpell(sp, copies=copies) for sp in sampled_spells]

def generate_spellbook_spells(size, spell_pool=spells):
  random.shuffle(spell_pool)
  return [SpellbookSpell(sp) for sp in spell_pool[:size]]

def generate_shop_item(item):
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
  return ShopItem(item, cost=cost, stock=stock)

def generate_blank_page_shop_item():
  variance = random.randint(0, 11)
  def blank_page_effect(player):
    player.remaining_blank_archive_pages += 1
  return ShopItem(blank_page, cost=15 + variance, stock=2, immediate_effect=blank_page_effect)

def generate_ancient_key_shop_item():
  variance = random.randint(0, 26)
  def ancient_key_effect(player):
    player.boss_keys += 1
  return ShopItem(ancient_key, cost=25 + variance, stock=1, immediate_effect=ancient_key_effect)

def generate_shop(n_items, item_pool, key=False, page=False) -> Shop:
  random.shuffle(item_pool)
  shop_items = []
  for item in item_pool[:n_items]:
    shop_items.append(generate_shop_item(item))
  if key:
    shop_items.append(generate_ancient_key_shop_item())
  # Trying out saying you get these from key runs:
  # if page:
  #   shop_items.append(generate_blank_page_shop_item())
  return Shop(shop_items)

def generate_crafting_shop(n_items, player) -> Shop:
  item_pool = [item for item in player.seen_items if item.craftable]
  random.shuffle(item_pool)
  shop_items_dict = {}
  for item in item_pool[:n_items]:
    if shop_items_dict.get(item.name):
      shop_items_dict[item.name].stock += 1
    else:
      shop_item = generate_shop_item(item)
      shop_items_dict[item.name] = shop_item
  return Shop(list(shop_items_dict.values()))