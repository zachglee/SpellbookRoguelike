class Event:
  def __init__(self, tags, source=None, target=None, effect=None):
    self.tags = tags
    self.source = source
    self.target = target
    self.effect = effect

  def resolve(self):
    self.effect(self.source, self.target)