from typing import List
from termcolor import colored
from collections import defaultdict
import random

from utils import colorize, numbered_list, choose_obj, ws_print

class RitualEvent:
  def __init__(self, trigger, effect):
    self.trigger = trigger
    self.effect = effect


class Ritual:
  def __init__(self, name, description, faction, required_progress, ritual_events):
    self.name = name
    self.description = description
    self.faction: str = faction
    self.progress = 0
    self.required_progress = required_progress

    self.level = 0
    self.experience = 0

    self.ritual_events: List[RitualEvent] = ritual_events

  @property
  def next_level_xp(self):
    return 15 # 16 - (1 * self.level)

  @property
  def activable(self):
    return self.progress >= self.required_progress

  async def run_events(self, encounter):
    for ritual_event in self.ritual_events:
      if ritual_event.trigger(encounter):
        await ws_print(colored(f"Ritual {self.name} triggered!", "yellow"), encounter.player.websocket)
        await ritual_event.effect(encounter)

  def render(self):
    progress_str = colored(f"({self.progress}/{self.required_progress})", "yellow")
    experience_str = colored(f"[{self.experience}/{self.next_level_xp}]", "magenta")
    return colorize(f"{experience_str} {progress_str} {self.name} (Lv. {self.level}) - {self.description}")
