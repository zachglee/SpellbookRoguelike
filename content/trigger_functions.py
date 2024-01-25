# other

def trigger_player_defense_break(encounter, event):
  if event.has_tag("defense_break") and event.metadata["target"].is_player():
    source = event.metadata["source"]
    return source.get_target_string(encounter) if source else True
  return False

# Passive triggers_on

def passive_face_noone_at_end(encounter, event):
  return event.has_tag("end_turn") and encounter.faced_enemy_queue == []

def passive_turn_3_onwards_at_begin(encounter, event):
  return event.has_tag("begin_turn") and encounter.turn >= 3

def passive_turn_start(encounter, event):
  return event.has_tag("begin_turn")

def passive_1_spell_in_turn(encounter, event):
  return event.has_tag("end_turn") and len(encounter.spells_cast_this_turn) <= 1

def passive_3_plus_enemies_at_begin(encounter, event):
  return event.has_tag("begin_turn") and len(encounter.enemies) >= 3

def passive_lose_hp(encounter, event):
  # event.metadata is the amount of hp lost
  return event.has_tag("lose_hp") and event.metadata["damage"] > 0 and event.metadata["target"].is_player()

def passive_at_half_health(encounter, event):
  return event.has_tag("begin_turn") and encounter.player.hp <= encounter.player.max_hp / 2

def passive_attacked_for_no_damage(encounter, event):
  if event.has_tag("attack") and event.metadata["damage_dealt"] == 0 and event.metadata["target"].is_player():
    return event.metadata["attacker"].get_target_string(encounter) or True
  return False

def passive_third_spell_in_turn(encounter, event):
  return event.has_tag("spell_cast") and len(encounter.spells_cast_this_turn) == 3

def passive_for_survive_6_damage_in_turn(encounter, event):
  if event.has_tag("end_round"):
    print(f"----------------- damage survived: {encounter.player.damage_survived_this_turn}")
    return int(encounter.player.damage_survived_this_turn / 6)
  return False
  
def passive_block_at_end(encounter, event):
  if event.has_tag("end_turn"):
    return encounter.player.conditions["block"]
  return False

def passive_block_and_shield_at_end(encounter, event):
  if event.has_tag("end_turn"):
    return encounter.player.conditions["block"] + encounter.player.conditions["shield"]
  return False

def passive_first_damage_10hp_remains(encounter, event):
  if (event.has_tag("attack") and not event.metadata["target"].is_player() and
      event.metadata["target"].hp >= 10 and event.metadata["damage_dealt"] == event.metadata["target"].damage_taken_this_turn):
    return event.metadata["target"].get_target_string(encounter)
  return False

def passive_on_page(encounter, event):
  return event.has_tag("page")

def passive_for_death_overkill(encounter, event):
  if event.has_tag("enemy_death"):
    return max(1, -1*event.source.hp)
  
def passive_no_dead_enemies_at_begin(encounter, event):
  return event.has_tag("begin_turn") and len(encounter.dead_enemies) == 0

def passive_on_entry(encounter, event):
  if event.has_tag("enemy_spawn"):
    return event.metadata["enemy"].get_target_string(encounter)
  return False

def passive_first_3_turns(encounter, event):
  return event.has_tag("begin_turn") and encounter.turn <= 3

# TODO: Remove this on next iteration
def passive_first_face(encounter, event):
  return event.has_tag("face")

def passive_on_face(encounter, event):
  return event.has_tag("face")

def passive_use_last_charge(encounter, event):
  return event.has_tag("spell_cast") and event.metadata["spell"].charges <= 0