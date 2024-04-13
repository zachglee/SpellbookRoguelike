from typing import Any


class Event:
  def __init__(self, tags, source=None, target=None, effect=None, metadata=None, description=None):
    self.tags = tags
    self.source = source
    self.target = target
    self.effect = effect
    self.metadata = metadata # for storing arbitrary stuff
    self.description = description # for rendering what's happening to the player

  @property
  def blocking(self):
    return not any(tag in self.tags for tag in [
      "lose_hp",
      "attack",
      "enemy_death",
      "enemy_spawn",
      "spell_cast",
      "defense_break",
      "end_turn",
      "begin_turn",
      "end_round",
      "page",
      "face",
      "condition"])

  def resolve(self):
    if self.effect:
      self.effect(self.source, self.target)

  def has_tag(self, tag):
    return tag in self.tags

  def __repr__(self) -> str:
    return f"Event {self.tags}"
