
class EventTrigger:
  def __init__(self, triggers_on, executor, turns_remaining=None, triggers_remaining=None, tags=[]):
    self.triggers_on_func = triggers_on
    self.executor = executor # can be a list of commands or a function
    self.turns_remaining = turns_remaining
    self.triggers_remaining = triggers_remaining
    self.tags = tags

  @property
  def finished(self):
    return self.turns_remaining == 0 or self.triggers_remaining == 0

  async def execute(self, encounter, event, trigger_output=None):
    if isinstance(self.executor, list):
      # main execution
      for cmd in self.executor:
        processed_command = cmd.replace("^", str(trigger_output))
        await encounter.handle_command(processed_command)
    else:
      self.executor(encounter, event, trigger_output=trigger_output)
  
  def triggers_on(self, encounter, event):
    if self.finished:
      return False
    return_value = self.triggers_on_func(encounter, event)
    if bool(return_value) and self.triggers_remaining is not None:
        self.triggers_remaining -= 1
    return return_value
