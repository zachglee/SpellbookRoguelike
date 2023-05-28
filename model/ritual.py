from termcolor import colored
from collections import defaultdict
import random

from utils import colorize, numbered_list, choose_obj

class Ritual:
  def __init__(self, name, description, required_progress, encounter_trigger, effect, progressor):
    self.name = name
    self.description = description
    self.progress = 0
    self.required_progress = required_progress

    self.encounter_trigger = encounter_trigger # takes an encounter and returns a boolean
    self.effect = effect # takes an encounter and modifies it
    self.progressor = progressor # takes an encounter and produces amount of progression from it

    self.encounters_remaining = 1

  @property
  def activable(self):
    return self.progress >= self.required_progress

  def render(self):
    return colorize(f"({self.progress}/{self.required_progress}) {self.name} - {self.description}")
