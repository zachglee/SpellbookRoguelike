# command_generator_factories

# TODO: need a way to compose these

# conditionals

from typing import List, Literal


def if_facing_none(commands):
  def if_facing_none_generator(encounter, targets_dict):
    if encounter.faced_enemy_queue == []:
      return commands
    else:
      return []
  return if_facing_none_generator

def if_kill(target, commands):
  def on_kill_generator(encounter, targets_dict):
    target_entity = targets_dict[target][1]
    if target_entity and target_entity.hp <= 0:
      return commands
    else:
      return []
  return on_kill_generator

def if_player_hp(fraction, commands, else_commands=[], above=True):
  def if_player_hp_generator(encounter, targets_dict):
    player_hp_fraction = encounter.player.hp / encounter.player.max_hp
    if above:
      if player_hp_fraction >= fraction:
        return commands
    else:
      if player_hp_fraction <= fraction:
        return commands
    return else_commands
  return if_player_hp_generator

def if_enemy_hp(target, hp_threshold, commands, above=True):
  def if_enemy_hp_generator(encounter, targets_dict):
    enemy_hp = targets_dict[target][1].hp
    if above:
      if enemy_hp >= hp_threshold:
        return commands
    else:
      if enemy_hp <= hp_threshold:
        return commands
    return []
  return if_enemy_hp_generator

def if_enemy_condition(target, condition, condition_threshold, commands, else_commands=[], above=True):
  def if_enemy_condition_generator(encounter, targets_dict):
    enemy_condition = targets_dict[target][1].conditions[condition]
    if above:
      if enemy_condition >= condition_threshold:
        return commands
    else:
      if enemy_condition <= condition_threshold:
        return commands
    return else_commands
  return if_enemy_condition_generator

def if_spell_charges(spell_charges, commands, above=True):
  def if_spell_charges_generator(encounter, targets_dict):
    if above:
      if encounter.last_spell_cast.charges >= spell_charges:
        return commands
    else:
      if encounter.last_spell_cast.charges <= spell_charges:
        return commands
    return []
  return if_spell_charges_generator

def if_player_energy(energy, commands, above=True):
  def if_player_energy_generator(encounter, targets_dict):
    if above:
      if encounter.player.total_energy() >= energy:
        return commands
    else:
      if encounter.player.total_energy() <= energy:
        return commands
    return []
  return if_player_energy_generator

# scalers

def for_dead_enemies(commands, magnitude_func=lambda x: x):
  def for_dead_enemies_generator(encounter, targets_dict):
    dead_enemies_magnitude = magnitude_func(len(encounter.dead_enemies))
    return [cmd.replace("*", str(dead_enemies_magnitude)) for cmd in commands]
  return for_dead_enemies_generator

def for_burn(target, commands):
  def for_burn_generator(encounter, targets_dict):
    burn_magnitude = targets_dict[target][1].conditions["burn"]
    return [cmd.replace("*", str(burn_magnitude)) for cmd in commands]
  return for_burn_generator

def for_spells_cast(commands, magnitude_func=lambda x: x):
  def for_spells_cast_generator(encounter, targets_dict):
    spells_cast_magnitude = magnitude_func(len(encounter.spells_cast_this_turn))
    return [cmd.replace("*", str(spells_cast_magnitude)) for cmd in commands]
  return for_spells_cast_generator

def for_player_energy(commands, magnitude_func=lambda x: x):
  def for_player_energy_generator(encounter, targets_dict):
    player_energy_magnitude = magnitude_func(encounter.player.total_energy())
    return [cmd.replace("*", str(player_energy_magnitude)) for cmd in commands]
  return for_player_energy_generator

def for_player_missing_hp(unit_hp, commands):
  def for_player_missing_hp_generator(encounter, targets_dict):
    missing_hp_magnitude = int((encounter.player.max_hp - encounter.player.hp) / unit_hp)
    return [cmd.replace("*", str(missing_hp_magnitude)) for cmd in commands]
  return for_player_missing_hp_generator

def for_enemy_missing_hp(target, unit_hp, commands):
  def for_enemy_missing_hp_generator(encounter, targets_dict):
    missing_hp_magnitude = int((targets_dict[target][1].max_hp - targets_dict[target][1].hp) / unit_hp)
    return [cmd.replace("*", str(missing_hp_magnitude)) for cmd in commands]
  return for_enemy_missing_hp_generator

def for_enemy_remaining_hp(target, unit_hp, commands):
  def for_enemy_remaining_hp_generator(encounter, targets_dict):
    remaining_hp_magnitude = int(targets_dict[target][1].hp / unit_hp)
    return [cmd.replace("*", str(remaining_hp_magnitude)) for cmd in commands]
  return for_enemy_remaining_hp_generator

def for_enemies(commands, magnitude_func=lambda x: x, specifier: Literal["total", "behind", "ahead", "front", "back"] = "total"):
  def for_enemies_generator(encounter, targets_dict):
    if specifier == "total":
      enemies_raw = len(encounter.back) + len(encounter.front)
    elif specifier == "behind":
      enemies_raw = len(encounter.unfaced_enemy_queue)
    elif specifier == "ahead":
      enemies_raw = len(encounter.faced_enemy_queue)
    elif specifier == "front":
      enemies_raw = len(encounter.front)
    elif specifier == "back":
      enemies_raw = len(encounter.back)
    enemies_magnitude = magnitude_func(enemies_raw)
    return [cmd.replace("*", str(enemies_magnitude)) for cmd in commands]
  return for_enemies_generator

def for_player_condition(conditions: List[str], commands, magnitude_func=lambda x: x):
  def for_player_condition_generator(encounter, targets_dict):
    raw_condition_magnitude = sum([encounter.player.conditions[condition] for condition in conditions], 0)
    processed_condition_magnitude = magnitude_func(raw_condition_magnitude)
    return [cmd.replace("*", str(processed_condition_magnitude)) for cmd in commands]
  return for_player_condition_generator

def for_turn_number(commands, magnitude_func=lambda x: x):
  def for_turn_number_generator(encounter, targets_dict):
    turn_number_magnitude = magnitude_func(encounter.turn)
    return [cmd.replace("*", str(turn_number_magnitude)) for cmd in commands]
  return for_turn_number_generator

def for_missing_charges(commands, magnitude_func=lambda x: x):
  def for_missing_charges_generator(encounter, targets_dict):
    missing_charges_raw = sum([spell.max_charges - spell.charges for spell in encounter.player.spellbook.current_page.spells], 0)
    missing_charges_magnitude = magnitude_func(missing_charges_raw)
    return [cmd.replace("*", str(missing_charges_magnitude)) for cmd in commands]
  return for_missing_charges_generator