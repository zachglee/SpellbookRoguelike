import random
from model.route import Route
from model.rest_site import RestSite
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


def generate_routes(n) -> Route:
  random.shuffle(rest_actions)
  random.shuffle(enemy_sets)
  routes = []
  for i in range(n):
    rest_site_actions = rest_actions[i*4:(i+1)*4] + [rerolls]
    rest_site = RestSite(rest_site_actions, None)
    spell_pool = generate_spell_pool()
    route = Route(enemy_sets[i*9:(i+1)*9], rest_site, spell_pool)
    routes.append(route)
  return routes