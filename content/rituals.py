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
      await encounter.handle_command.append(command)
  return effect

# ritual event factories

def turn_command_event_factory(turn_list, commands):
  return RitualEvent(turn_trigger_factory(turn_list), command_effect_factory(commands))



# Gold

# strike_as_one = Ritual("Strike as One",
#                        "Empower 10 on turn 3.",
#                        required_progress=3,
#                        encounter_trigger=turn_trigger_factory([3]),
#                        effect=player_condition_effect_factory("empower", 10),
#                        energy_color="gold")

# glimpse_the_infinite = Ritual("Glimpse the Infinite",
#                               "Gain inventive 1 and prolific 1 on turns 2 and 4.",
#                               required_progress=3,
#                               encounter_trigger=turn_trigger_factory([2, 4]),
#                               effect=player_conditions_effect_factory(["inventive", "prolific"], [1, 1]),
#                               energy_color="gold")

# # Red

# # Little healing every turn
# boiling_blood = Ritual("Boiling Blood",
#                        "Regen 1 every turn.",
#                        required_progress=3,
#                        encounter_trigger=turn_trigger_factory(list(range(1, 10))),
#                        effect=player_condition_effect_factory("regen", 1),
#                        energy_color="red")

# # Big burst of burn at end
# imminent_inferno = Ritual("Imminent Inferno",
#                           "Burn 3 all enemies on turns 4, 5, 6.",
#                           required_progress=3,
#                           encounter_trigger=turn_trigger_factory([4, 5, 6]),
#                           effect=enemy_condition_effect_factory("burn", 3),
#                           energy_color="red")

# # Blue

# ambush_ensnarement = Ritual("Ambush Ensnarement",
#                             "Stun all enemies 1 on turn 4.",
#                             required_progress=3,
#                             encounter_trigger=turn_trigger_factory([4]),
#                             effect=enemy_condition_effect_factory("stun", 1),
#                             energy_color="blue")

# # Block at beginning of encounter
# armored_approach = Ritual("Armored Approach",
#                           "Gain 6 block on the first 3 turns.",
#                           required_progress=3,
#                           encounter_trigger=turn_trigger_factory([1, 2, 3]),
#                           effect=player_condition_effect_factory("block", 6),
#                           energy_color="blue")

# rituals = [strike_as_one, glimpse_the_infinite, boiling_blood, imminent_inferno, ambush_ensnarement, armored_approach]