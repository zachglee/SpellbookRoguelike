from model.ritual import Ritual, RitualEvent

# trigger factories

def turn_trigger_factory(turn_list):
  def turn_trigger(encounter):
    return encounter.turn in turn_list
  return turn_trigger

# effect factories

def command_effect_factory(commands):
  async def effect(encounter):
    for command in commands:
      await encounter.handle_command(command)
  return effect

# ritual event factories

def turn_command_event_factory(turn_list, commands):
  return RitualEvent(turn_trigger_factory(turn_list), command_effect_factory(commands))

