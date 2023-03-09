from termcolor import colored
from collections import defaultdict
import random

from utils import colorize, numbered_list, choose_obj

class Ritual:
  def __init__(self, name, description, resource_cost, labor_cost, encounter_trigger, effect):
    self.name = name
    self.description = description
    self.resource_cost = resource_cost # dict
    self.labor = 0
    self.labor_cost = labor_cost
    self.encounter_trigger = encounter_trigger # takes an encounter and returns a boolean
    self.effect = effect # takes an encounter and modifies it

    self.encounters_remaining = 3
  
  def render(self):
    return colorize(f"({self.labor}/{self.labor_cost}) {self.name} - {self.resource_cost}")

class RitualDraft:
  def __init__(self, rituals):
    self.resource_pool = defaultdict(lambda: 0)
    self.rituals = rituals

  def can_cast(self, ritual):
    return all(self.resource_pool[resource] >= ritual.resource_cost[resource]
               for resource in ritual.resource_cost) and ritual.labor >= ritual.labor_cost

  @property
  def castable_rituals(self):
    return sorted([ritual for ritual in self.rituals if self.can_cast(ritual)], key=lambda ritual: ritual.labor, reverse=True)
  
  def add_player_contribution(self, player):
    for resource in player.resources:
      self.resource_pool[resource] += player.resources[resource]
    print(self.render())
    chosen_ritual = choose_obj(self.rituals, colored("Choose a ritual to labor on > ", "red"))
    chosen_ritual.labor += 1
  
  def render(self):
    render_str = numbered_list(self.rituals)
    render_str += "\nResource Pool: " + colorize(str(dict(self.resource_pool)))
    return render_str
