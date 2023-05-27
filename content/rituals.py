from model.ritual import Ritual

# trigger factories

def turn_trigger_factory(turn_list):
  def turn_trigger(encounter):
    return encounter.turn in turn_list
  return turn_trigger

# effect factories

def enemy_condition_effect_factory(condition_name, condition_value):
  def effect(encounter):
    for enemy in encounter.enemies:
      enemy.conditions[condition_name] += condition_value
  return effect

def player_condition_effect_factory(condition_name, condition_value):
  def effect(encounter):
    encounter.player.conditions[condition_name] += condition_value
  return effect

def player_conditions_effect_factory(condition_names, condition_values):
  def effect(encounter):
    for condition_name, condition_value in zip(condition_names, condition_values):
      encounter.player.conditions[condition_name] += condition_value
  return effect

# Progressor factories

def excess_energy_progressor_factory(color, progress):
  def excess_energy_progressor(encounter):
    excess_energy = encounter.player.conditions[color]
    if excess_energy > 0:
      return progress * excess_energy
    else:
      return 0
  return excess_energy_progressor

# Gold

strike_as_one = Ritual("Strike as One",
                       "Empower 9 on turn 3.",
                       required_progress=6,
                       encounter_trigger=turn_trigger_factory([3]),
                       effect=player_condition_effect_factory("empower", 9),
                       progressor=excess_energy_progressor_factory("gold", 2))

glimpse_the_infinite = Ritual("Glimpse the Infinite",
                              "Gain inventive 1 and prolific 1 on turns 2 and 4.",
                              required_progress=6,
                              encounter_trigger=turn_trigger_factory([2, 4]),
                              effect=player_conditions_effect_factory(["inventive", "prolific"], [1, 1]),
                              progressor=excess_energy_progressor_factory("gold", 2))

# Red

# Little healing every turn
boiling_blood = Ritual("Boiling Blood",
                       "Regen 1 every turn.",
                       required_progress=6,
                       encounter_trigger=turn_trigger_factory(list(range(1, 10))),
                       effect=player_condition_effect_factory("regen", 1),
                       progressor=excess_energy_progressor_factory("red", 2))

# Big burst of burn at end
imminent_inferno = Ritual("Imminent Inferno",
                          "Burn 3 all enemies on turns 4, 5, 6.",
                          required_progress=6,
                          encounter_trigger=turn_trigger_factory([4, 5, 6]),
                          effect=enemy_condition_effect_factory("burn", 3),
                          progressor=excess_energy_progressor_factory("red", 2))

# Blue

ambush_ensnarement = Ritual("Ambush Ensnarement",
                            "Stun all enemies 1 on turn 4.",
                            required_progress=6,
                            encounter_trigger=turn_trigger_factory([4]),
                            effect=enemy_condition_effect_factory("stun", 1),
                            progressor=excess_energy_progressor_factory("blue", 2))

# Block at beginning of encounter
armored_approach = Ritual("Armored Approach",
                          "Gain 8 block on the first 2 turns.",
                          required_progress=6,
                          encounter_trigger=turn_trigger_factory([1, 2]),
                          effect=player_condition_effect_factory("block", 8),
                          progressor=excess_energy_progressor_factory("blue", 2))

rituals = [strike_as_one, glimpse_the_infinite, boiling_blood, imminent_inferno, ambush_ensnarement, armored_approach]