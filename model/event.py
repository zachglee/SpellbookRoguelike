from typing import Any


class Event:
  def __init__(self, tags, source=None, target=None, effect=None, metadata=None):
    self.tags = tags
    self.source = source
    self.target = target
    self.effect = effect
    self.metadata = metadata # for storing arbitrary stuff

  def resolve(self):
    if self.effect:
      self.effect(self.source, self.target)

  def has_tag(self, tag):
    return tag in self.tags

  def __repr__(self) -> str:
    return f"Event({self.tags}) {self.metadata}"