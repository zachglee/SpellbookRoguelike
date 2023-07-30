from model.spellbook import Spell
from content.command_generators import *

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

def passive_attacked_for_no_damage(encounter, event):
  if event.has_tag("attack") and event.metadata["damage_dealt"] == 0 and event.metadata["target"].is_player():
    return event.metadata["attacker"].get_target_string(encounter)
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
    encounter.player.conditions["block"]
  return False

def passive_block_and_shield_at_end(encounter, event):
  if event.has_tag("end_turn"):
    encounter.player.conditions["block"] + encounter.player.conditions["shield"]
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

def passive_first_face(encounter, event):
  return event.has_tag("face") and encounter.player.face_count == 1

def passive_use_last_charge(encounter, event):
  return event.has_tag("spell_cast") and event.metadata["spell"].charges <= 0

# Red Color Identity:

red_enemy_dies = [
  [Spell("Passive: Whenever an enemy dies, gain 4 empower and deal overkill damage to immediate.", color="red", type="Passive",
         triggers_on=passive_for_death_overkill, raw_commands=["empower p 4", "damage i ^"]),
  Spell("Producer: +1 Red, inflict 1 vulnerable", color="red", type="Producer", raw_commands=["vulnerable _ 1"]),
  Spell("Converter: 1 Red -> 1 Gold, Deal 9 damage. If this kills, +1 red.", color="red", type="Converter", conversion_color="gold",
        targets=["_"], raw_commands=["damage _ 9"], generate_commands_post=if_kill("_", ["red p 1"])),
  Spell("Consumer: 1 Red: Deal 16 damage", color="red", type="Consumer", raw_commands=["damage _ 16"])],
  #
  [Spell("Passive: Whenever an enemy dies, inflict 4 burn on random.", color="red", type="Passive",
         triggers_on=passive_for_death_overkill, raw_commands=["burn r 4"]),
  Spell("Producer: +1 Red, inflict 2 burn.", color="red", type="Producer", raw_commands=["burn _ 2"]),
  Spell("Converter: 1 Red -> 1 Blue, Inflict 5 burn.", color="red", type="Converter", conversion_color="blue", raw_commands=["burn _ 5"]),
  Spell("Consumer: 1 Red: Inflict 2 burn, then inflict their burn on all enemies.", color="red", type="Consumer",
        targets=["_"], raw_commands=["burn _ 2"], generate_commands_post=for_burn("_", ["burn a *"]))],
]

red_take_damage = [
  [Spell("Passive: Whenever you lose hp, gain 5 empowered.", color="red", type="Passive",
         triggers_on=passive_lose_hp, raw_commands=["empower p 5"]),
  Spell("Producer: +1 Red, deal 2 damage. If this kills an enemy, recharge, refresh, +1 time.", color="red", type="Producer",
        raw_commands=["damage _ 2"], generate_commands_post=if_kill("_", ["time -1", "recharge last"])),
  Spell("Converter: 1 Red -> 1 Gold: Gain 1 sharp for every missing 4 health.", color="red", type="Converter", conversion_color="gold",
        generate_commands_pre=for_player_missing_hp(4, ["sharp p *"])),
  Spell("Consumer: 1 Red: 8 damage to all enemies on target side.", color="red", type="Consumer", raw_commands=["damage iside 8"])],
  #
  [Spell("Passive: Whenever you lose hp, inflict 3 burn on all enemies.", color="red", type="Passive",
         triggers_on=passive_lose_hp, raw_commands=["burn a 2"]),
  Spell("Producer: +1 Red, gain 2 regen and 2 burn.", color="red", type="Producer", raw_commands=["regen p 2", "burn p 2"]),
  Spell("Converter: 1 Red -> 1 Gold: Gain 2 regen. Inflict 3 burn.", color="red", type="Converter", conversion_color="gold", raw_commands=["regen p 2", "burn _ 3"]),  # NOTE: Purple
  Spell("Consumer: 1 Red: Inflict 3 burn. Tick all burn and gain life equal to damage dealt in this way.", color="red", type="Consumer", raw_commands=["burn _ 3"])], 
]

red_big_attack = [
  [Spell("Passive: Gain 1 red, 1 sharp, and 1 prolific for every 6 damage you survive each round.", color="red", type="Passive",
         triggers_on=passive_for_survive_6_damage_in_turn, raw_commands=["red p ^", "sharp p ^", "prolific p ^"]),
  Spell("Producer: +1 Red, If you're at or below half health, +1 more red.", color="red", type="Producer",
        generate_commands_pre=if_player_hp(0.5, ["red p 1"], above=False)),
  Spell("Converter: 1 Red -> 1 Gold: Deal 2 damage x times, where x is amount of energy you have.", color="red", type="Converter", conversion_color="gold",
        generate_commands_pre=for_player_energy(["repeat * damage _ 2"])),
  Spell("Consumer: 1 Red: Deal 11 damage. Then you may consume 1 energy of any type to recharge and refresh this.", color="red", type="Consumer", raw_commands=["damage _ 11"])],
  #
  [Spell("Passive: Gain 1 regen, deal 3 damage to all for every 6 damage you survive each round.", color="red", type="Passive",
         triggers_on=passive_for_survive_6_damage_in_turn, raw_commands=["regen p ^", "repeat ^ damage a 3"]),
  Spell("Producer: +1 Red, If at full health, deal 6 damage, otherwise gain 1 regen.", color="red", type="Producer",
        generate_commands_pre=if_player_hp(1.0, ["damage _ 6"], else_commands=["regen p 1"], above=True)),
  Spell("Converter: 1 Red -> 1 Gold: Suffer 3 damage, gain 3 sharp.", color="red", type="Converter", conversion_color="gold", raw_commands=["suffer p 3", "sharp p 3"]), # NOTE: Green
  Spell("Consumer: 1 Red: Deal 7 damage. Heal for unblocked.", color="red", type="Consumer", raw_commands=["lifesteal _ 7"])],
]

red_hit_big_enemy = [
  [Spell("Passive: The 1st time you damage each enemy in a turn, inflict 5 burn if at least 10hp remains.", color="red", type="Passive",
         triggers_on=passive_first_damage_10hp_remains, raw_commands=["burn ^ 5"]),
  Spell("Producer: +1 Red, Deal 4 damage to immediate.", color="red", type="Producer", raw_commands=["damage i 4"]),
  Spell("Converter: 1 Red -> 1 Blue: Apply 1 poison. Apply extra 1 poison for every 5 hp the target has.", color="red", type="Converter", conversion_color="blue",
        targets=["_"], generate_commands_pre=for_enemy_remaining_hp("_", 5, ["poison _ 1", "poison _ *"])), # NOTE: Purple
  Spell("Consumer: 1 Red: Target loses half its remaining health.", color="red", type="Consumer",
        targets=["_"], generate_commands_pre=for_enemy_remaining_hp("_", 2, ["suffer _ *"]))],
  #
  [Spell("Passive: The 1st time you damage each enemy in a turn, gain 3 regen if at least 10hp remains.", color="red", type="Passive",
         triggers_on=passive_first_damage_10hp_remains, raw_commands=["regen p 3"]),
  Spell("Producer: +1 Red, Deal 6 damage to a target at or above 10 health.", color="red", type="Producer",
        targets=["_"], generate_commands_pre=if_enemy_hp("_", 10, ["damage _ 6"], above=True)),
  # TODO: make the stun target the same enemy automatically
  Spell("Converter: 1 Red -> 1 Blue: Deal 6 damage. Stun 1 the target if 10 or more hp remains.", color="red", type="Converter", conversion_color="blue",
        targets=["_"], raw_commands=["damage _ 6"], generate_commands_post=if_enemy_hp("_", 10, ["stun _ 1"], above=True)),
  Spell("Consumer: 1 Red: Deal damage equal to target's missing health.", color="red", type="Consumer",
        targets=["_"], generate_commands_pre=for_enemy_missing_hp("_", 1, ["damage _ *"]))],
]

red_first_3_turns = [
  [Spell("Passive: At the start of first 3 turns, gain 3 fleeting sharp", color="red", type="Passive",
          triggers_on=passive_first_3_turns, raw_commands=["sharp p 3", "delay 0 sharp p -3"]),
  Spell("Producer: +1 Red, call 1, +3 time", color="red", type="Producer", raw_commands=["call 1", "time -3"]),
  Spell("Converter: 1 Red -> 1 Blue: Deal 2 damage to random x times, where x is 8 - turn number", color="red", type="Converter", conversion_color="blue",
        generate_commands_pre=for_turn_number(["repeat * damage r 2"], lambda t: 8 - t)),
  Spell("Consumer: Call 1 three times. Gain 6 sharp.", color="red", type="Consumer", raw_commands=["call 1", "call 1", "call 1", "sharp p 6"])],
  #
  [Spell("Passive: At the start of first 3 turns, gain 1 inventive and 1 prolific.", color="red", type="Passive",
          triggers_on=passive_first_3_turns, raw_commands=["inventive p 1", "prolific p 1"]),
  Spell("Producer: +1 Red, If this has 0 or less charges, gain dig deep 2.", color="red", type="Producer",
        generate_commands_post=if_spell_charges(0, ["dig p 2"], above=False)),
  Spell("Converter: 1 Red -> 1 Gold: Call 2. Gain 15 empower.", color="red", type="Converter", conversion_color="gold", raw_commands=["call 2", "empower p 15"]),
  Spell("Consumer: 1 Red: Regen 1. If this has 0 or less charges, deal 12 damage to random twice.", color="red", type="Consumer",
        raw_commands=["regen p 1"], generate_commands_post=if_spell_charges(0, ["damage r 12", "damage r 12"], above=False))]
]

red_random_target = [
  [Spell("Passive: At the start of your turn, inflict 1 vulnerable on a random enemy", color="red", type="Passive",
          triggers_on=passive_turn_start, raw_commands=["vulnerable r 1"]),
  Spell("Producer: +1 Red, deal 3 damage to a random enemy.", color="red", type="Producer", raw_commands=["damage r 3"]),
  Spell("Converter: 1 Red -> 1 Gold: Gain 2 sharp this turn, inflict 2 vulnerable on all enemies.", color="red", type="Converter", conversion_color="gold",
        raw_commands=["sharp p 2", "delay 0 sharp p -2", "vulnerable a 2"]),
  Spell("Consumer: 1 Red: Deal 12 damage to any target.", color="red", type="Consumer", raw_commands=["damage _ 12"])],
  #
  [Spell("Passive: At the start of your turn, inflict 2 poison on a random enemy", color="red", type="Passive",
          triggers_on=passive_turn_start, raw_commands=["poison r 2"]),
  Spell("Producer: +1 Red, deal 1 damage to a random enemy twice.", color="red", type="Producer", raw_commands=["damage r 1", "damage r 1"]),
  Spell("Converter: 1 Red -> 1 Blue: Inflict 6 poison on a damaged enemy.", color="red", type="Converter", conversion_color="blue", raw_commands=["poison _damaged 6"]),
  Spell("Consumer: 1 Red: Gain 4 regen and 4 vulnerable.", color="red", type="Consumer", raw_commands=["regen p 4", "vulnerable p 4"])]
]

# red_page_sets = [red_enemy_dies, red_take_damage, red_big_attack, red_hit_big_enemy]
# red_pages = red_enemy_dies + red_take_damage + red_big_attack + red_hit_big_enemy
red_page_sets = [red_first_3_turns, red_random_target]
red_pages = red_first_3_turns + red_random_target
red_spells = sum(red_pages, [])

# Blue Color Identity

blue_block_hits = [
  [Spell("Passive: Whenever you’re attacked and take no damage, deal 5 damage to attacker.", color="blue", type="Passive",
         triggers_on=passive_attacked_for_no_damage, raw_commands=["damage ^ 5"]),
  Spell("Producer: +1 Blue, gain 1 block per enemy.", color="blue", type="Producer",
        generate_commands_pre=for_enemies(["block p *"])),
  Spell("Converter: 1 Blue -> 1 Gold: Gain 9 block", color="blue", type="Converter", conversion_color="gold", raw_commands=["block p 9"]),  # NOTE: Green
  Spell("Consumer: 1 Blue: Gain 8 armor this turn.", color="blue", type="Consumer",
        raw_commands=["armor p 8", "delay 0 armor p -8"])],
  #
  [Spell("Passive: Whenever you’re attacked and take no damage, gain 2 retaliate.", color="blue", type="Passive",
         triggers_on=passive_attacked_for_no_damage, raw_commands=["retaliate p 2"]),
  Spell("Producer: +1 Blue, gain 1 block and Break: deal 6 damage to attacker.", color="blue", type="Producer", raw_commands=["block p 1"]),
  Spell("Converter: 1 Blue -> 1 Gold: Block 5. Deal 4 damage.", color="blue", type="Converter", conversion_color="gold", raw_commands=["block p 5", "damage _ 4"]),
  Spell("Consumer: 1 Blue: Block 4. Break: Deal 4 times the breaker’s attack damage back.", color="blue", type="Consumer", raw_commands=["block p 4"])],
]

blue_turn_3 = [
  [Spell("Passive: At beginning of 3rd turn and onwards, block 4.", color="blue", type="Passive",
         triggers_on=passive_turn_3_onwards_at_begin, raw_commands=["block p 4"]),
  Spell("Producer: +1 Blue, Inflict 1 stun on an enemy that entered this turn.", color="blue", type="Producer", raw_commands=["stun _entered 1"]),
  Spell("Converter: 1 Blue -> 1 Red: Stun 1 or deal 15 damage to a stunned enemy.", color="blue", type="Converter", conversion_color="red"), # NOTE: Purple # TODO
  Spell("Consumer: 1 Blue: Inflict 3 stun.", color="blue", type="Consumer", raw_commands=["stun _ 3"])],
  #
  [Spell("Passive: At beginning of 3rd turn and onwards, deal 3 damage to all enemies.", color="blue", type="Passive",
         triggers_on=passive_turn_3_onwards_at_begin, raw_commands=["damage a 3"]),
  Spell("Producer: +1 Blue, ward 1.", color="blue", type="Producer", raw_commands=["ward p 1"]),
  Spell("Converter: 1 Blue -> 1 Red: At the end of next turn, all enemies take 8 damage.", color="blue", type="Converter", conversion_color="red",
        raw_commands=["delay 1 damage a 8"]),
  Spell("Consumer: 1 Blue: Ward 4.", color="blue", type="Consumer", raw_commands=["ward p 4"])],
]

blue_3_enemies = [
  [Spell("Passive: At the beginning of your turn if there are 3 or more enemies, stun 2 of them at random.", color="blue", type="Passive",
         triggers_on=passive_3_plus_enemies_at_begin, raw_commands=["stun r 1", "stun r 1"]),
  Spell("Producer: +1 Blue, gain 1 block and Break: stun 1.", color="blue", type="Producer", raw_commands=["block p 1"]),
  Spell("Converter: 1 Blue -> 1 Gold: Gain retaliate 2.", color="blue", type="Converter", conversion_color="gold", raw_commands=["retaliate p 2"]), # NOTE: Green
  Spell("Consumer: 1 Blue: Deal 4 damage to all stunned enemies. Stun 1 all enemies.", color="blue", type="Consumer", raw_commands=["stun a 1"])],
  #
  [Spell("Passive: At the beginning of your turn, if there are 3 or more enemies, deal 15 damage to a random enemy.", color="blue", type="Passive",
         triggers_on=passive_3_plus_enemies_at_begin, raw_commands=["damage r 15"]),
  Spell("Producer: +1 Blue, deal 6 damage, call 1", color="blue", type="Producer", raw_commands=["damage _ 6", "call 1"]),
  Spell("Converter: 1 Blue -> 1 Gold: Gain retaliate 6 this turn.", color="blue", type="Converter", conversion_color="gold",
        raw_commands=["retaliate p 6", "delay 0 retaliate p -6"]), # NOTE: Purple
  Spell("Consumer: 1 Blue: Gain 3 enduring this turn.", color="blue", type="Consumer",
        raw_commands=["enduring p 3", "delay 0 enduring p -3"])],
]

blue_excess_block = [
  [Spell("Passive: Excess block/shield at the end of your turn is dealt as damage to immediate.", color="blue", type="Passive",
         triggers_on=passive_block_and_shield_at_end, raw_commands=["damage i ^"]),
  Spell("Producer: +1 Blue, Gain 4 block.", color="blue", type="Producer", raw_commands=["block p 4"]),
  Spell("Converter: 1 Blue -> 1 Red: Gain 1 armor and 1 retaliate.", color="blue", type="Converter", conversion_color="red", raw_commands=["armor p 1", "retaliate p 1"]),
  Spell("Consumer: 1 Blue: Gain 18 block.", color="blue", type="Consumer", raw_commands=["block p 18"])],
  #
  [Spell("Passive: At the end of each turn, gain shield equal to block.", color="blue", type="Passive",
         triggers_on=passive_block_at_end, raw_commands=["shield p ^"]),
  Spell("Producer: +1 Blue, +2 shield.", color="blue", type="Producer", raw_commands=["shield p 2"]),
  Spell("Converter: 1 Blue -> 1 Gold: Block 2. Convert block into 2x shield.", color="blue", type="Converter", conversion_color="gold",
        raw_commands=["block p 2"], generate_commands_post=for_player_condition("block", ["shield p *", "block p =0"], lambda b: 2*b)),
  Spell("Consumer: 1 Blue: Gain 6 block. Deal damage equal to block + shield to target.", color="blue", type="Consumer")],
]

# -----------
blue_no_enemy_deaths = [
  [Spell("Passive: At the start of your turn, if no enemies are dead, gain 6 block.", color="blue", type="Passive",
          triggers_on=passive_no_dead_enemies_at_begin, raw_commands=["block p 6"]),
  Spell("Producer: +1 Blue, encase self 4", color="blue", type="Producer", raw_commands=["encase p 4"]),
  Spell("Converter: 1 Blue -> 1 Red: Inflict 2 doom.", color="blue", type="Converter", conversion_color="red",
        raw_commands=["doom _ 2"]),
  Spell("Consumer: 1 Blue: Encase 10 an enemy and inflict 1 doom.", color="blue", type="Consumer",
        raw_commands=["encase _ 10", "doom _ 1"])],
  #
  [Spell("Passive: At the start of your turn, if no enemies are dead, ward self 1.", color="blue", type="Passive",
          triggers_on=passive_no_dead_enemies_at_begin, raw_commands=["ward p 1"]),
  Spell("Producer: +1 Blue, Deal 6 damage to random 1 turn from now.", color="blue", type="Producer",
        raw_commands=["delay 1 damage _ -6"]),
  Spell("Converter: 1 Blue -> 1 Gold: Gain x time, x empower, and x block, where x is # of enemies", color="blue", type="Converter", conversion_color="gold",
        generate_commands_pre=for_enemies(["time -*", "empower p *", "block p *"])),
  Spell("Consumer: 1 Blue: Deal 2x damage to all enemies, where x is turn number.", color="blue", type="Consumer",
        generate_commands_pre=for_turn_number(["damage a *"], lambda s: 2*s))],
]

blue_on_entry = [
  [Spell("Passive: When an enemy enters, gain 1 retaliate and 2 block.", color="blue", type="Passive",
          triggers_on=passive_on_entry, raw_commands=["retaliate p 1", "block p 2"]),
  Spell("Producer: +1 Blue, inflict 1 poison.", color="blue", type="Producer", raw_commands=["poison _ 1"]),
  Spell("Converter: 1 Blue -> 1 Red: Block 3. Break: Poison 3 all enemies.", color="blue", type="Converter", conversion_color="red",
        raw_commands=["block p 3"]), # TODO: poison
  Spell("Consumer: 1 Blue: All enemies gain 1 undying. You gain 3 shield for each enemy.", color="blue", type="Consumer",
        raw_commands=["undying a 1"], generate_commands_pre=for_enemies(["shield p *"], lambda s: 3*s))],
  #
  [Spell("Passive: When an enemy enters, deal it 3 damage.", color="blue", type="Passive",
          triggers_on=passive_on_entry, raw_commands=["damage ^ 3"]),
  Spell("Producer: +1 Blue, deal 5 damage to an enemy that entered this turn.", color="blue", type="Producer", raw_commands=["damage _entered 5"]),
  Spell("Converter: 1 Blue -> 1 Gold: Deal 10 damage to the furthest faced enemy.", color="blue", type="Converter", conversion_color="gold",
        raw_commands=["damage distant 10"]),
  Spell("Consumer: 1 Blue: Banish 2 an enemy.", color="blue", type="Consumer", raw_commands=["banish _ 2"])]
]

# blue_page_sets = [blue_block_hits, blue_turn_3, blue_3_enemies, blue_excess_block]
# blue_pages = blue_block_hits + blue_turn_3 + blue_3_enemies + blue_excess_block
blue_page_sets = [blue_no_enemy_deaths, blue_on_entry]
blue_pages = blue_no_enemy_deaths + blue_on_entry
blue_spells = sum(blue_pages, [])

# Gold Color Identity:

gold_3rd_spell = [
  [Spell("Passive: Whenever you cast your 3rd spell in a turn, gain 3 sharp.", color="gold", type="Passive",
         triggers_on=passive_third_spell_in_turn, raw_commands=["sharp p 3"]),
  Spell("Producer: +1 Gold, Deal 2 damage to each adjacent enemy.", color="gold", type="Producer", raw_commands=["damage f1 2", "damage b1 2"]),
  Spell("Converter: 1 Gold -> 1 Red: Deal 3 damage to immediate enemy. Repeat twice more.", color="gold", type="Converter", conversion_color="red", raw_commands=["damage i 3", "damage i 3", "damage i 3"]),
  Spell("Consumer: 1 Gold: Deal 10 damage to immediate, deal 4 damage to immediate behind. Refresh this.", color="gold", type="Consumer", raw_commands=["damage i 10", "damage bi 4"])],
  #
  [Spell("Passive: Whenever you cast your 3rd spell in a turn, gain 9 block.", color="gold", type="Passive",
         triggers_on=passive_third_spell_in_turn, raw_commands=["block p 9"]),
  Spell("Producer: +1 Gold, gain 1 regen.", color="gold", type="Producer", raw_commands=["regen p 1"]),
  Spell("Converter: 1 Gold -> 1 Blue: +3 time. Every spell you cast after this gives 1 retaliation.", color="gold", type="Converter", conversion_color="blue", raw_commands=["time -3"]),
  Spell("Consumer: 1 Gold: Gain 5 searing presence.", color="gold", type="Consumer", raw_commands=["searing p 5"])],
]

gold_turn_page = [
  [Spell("Passive: Every time you turn to this page, recharge a random spell.", color="gold", type="Passive",
         triggers_on=passive_on_page, raw_commands=["recharge r"]),
  Spell("Producer: +1 Gold, if this has 0 or less charges, gain 4 shield.", color="gold", type="Producer",
        generate_commands_post=if_spell_charges(0, ["shield p 4"], above=False)),
  Spell("Converter: 1 Gold -> 1 Red: Deal 6 damage to immediate. Gain 1 empower for each missing spell charge on this page.", color="gold", type="Converter", conversion_color="red",
        raw_commands=["damage i 6"], generate_commands_post=for_missing_charges(["empower p *"])),
  Spell("Consumer: 1 Gold: Gain Dig Deep 3. (Spells can go to -1 charge) Gain 3 shield.", color="gold", type="Consumer", raw_commands=["dig p 3", "shield p 3"])],
  #
  [Spell("Passive: Every time you turn to this page, gain 1 inventive.", color="gold", type="Passive",
         triggers_on=passive_on_page, raw_commands=["inventive p 1"]),
  Spell("Producer: +1 Gold, refresh a spell.", color="gold", type="Producer"),
  Spell("Converter: 1 Gold -> 1 Red: +4 time, +1 inventive, refresh other spells on this page.", color="gold", type="Converter", conversion_color="red",
        raw_commands=["time -4", "inventive p 1"]), # NOTE: Green
  Spell("Consumer: 1 Gold: Gain 2x shield and deal 2x to all where x is # of spells cast this turn.", color="gold", type="Consumer",
        generate_commands_pre=for_spells_cast(["shield p *", "damage a *"], lambda s: 2*s))], 
]

gold_1_spell = [
  [Spell("Passive: If you cast 1 or less spell in a turn, gain 1 energy of any color.", color="gold", type="Passive",
         triggers_on=passive_1_spell_in_turn, raw_commands=["gold p 1"]), # TODO fix this
  Spell("Producer: +1 Gold, you may convert 1 energy to another color.", color="gold", type="Producer"),
  # TODO: Make this work: Or just re-work it?
  Spell("Converter: 1 Gold -> 1 Red: Gold: 4 empower. Red: 4 damage. Blue: 4 shield.", color="gold", type="Converter", conversion_color="red"), # NOTE: Green
  Spell("Consumer: 1 Gold: Gain 3 inventive and 1 energy of any color.", color="gold", type="Consumer", raw_commands=["inventive p 3"])],
  #
  [Spell("Passive: If you cast 1 or less spell in a turn, empower 6.", color="gold", type="Passive",
         triggers_on=passive_1_spell_in_turn, raw_commands=["empower p 6"]),
  Spell("Producer: +1 Gold, +1 time.", color="gold", type="Producer", raw_commands=["time -1"]),
  Spell("Converter: 1 Gold -> 1 Red: Deal 6 damage to immediate. If this kills, recharge and refresh.", color="gold", type="Converter", conversion_color="red",
        targets=["i"], raw_commands=["damage i 6"], generate_commands_post=if_kill("i", ["recharge last"])),
  Spell("Consumer: 1 Gold: Gain 3 prolific.", color="gold", type="Consumer", raw_commands=["prolific p 3"])],
]

gold_face_noone = [
  [Spell("Passive: At end of turn, if facing no enemies, gain 2 searing presence.", color="gold", type="Passive",
         triggers_on=passive_face_noone_at_end, raw_commands=["searing p 2"]),
  Spell("Producer: +1 Gold, gain 2 searing presence.", color="gold", type="Producer", raw_commands=["searing p 2"]),
  Spell("Converter: 1 Gold -> 1 Red: Banish immediate enemy.", color="gold", type="Converter", conversion_color="red",
        targets=["i"], raw_commands=["banish i"]),
  Spell("Consumer: 1 Gold: Gain 2 armor.", color="gold", type="Consumer", raw_commands=["armor p 2"])],
  #
  [Spell("Passive: At end of turn, if facing no enemies, gain 3 shield.", color="gold", type="Passive",
         triggers_on=passive_face_noone_at_end, raw_commands=["shield p 3"]),
  Spell("Producer: +1 Gold, if facing no enemies, empower 5.", color="gold", type="Producer",
        generate_commands_pre=if_facing_none(["empower p 5"])),
  Spell("Converter: 1 Gold -> 1 Blue: Gain 5 shield.", color="gold", type="Converter", conversion_color="blue", raw_commands=["shield p 5"]),
  Spell("Consumer: 1 Gold: Deal 10 damage to immediate. If this kills an enemy, empower 10.", color="gold", type="Consumer",
        targets=["i"], raw_commands=["damage i 10"], generate_commands_post=if_kill("i", ["empower p 10"]))],
]

gold_first_face = [
  [Spell("Passive: The first time you face in a round, gain 6 block.", color="gold", type="Passive",
          triggers_on=passive_first_face, raw_commands=["block p 6"]),
  Spell("Producer: +1 Gold, Stun 1 immediate behind.", color="gold", type="Producer", raw_commands=["stun bi 1"]),
  Spell("Converter: 1 Gold -> 1 Blue: Face, gain 2 shield for each enemy behind.", color="gold", type="Converter", conversion_color="blue",
        raw_commands=["face"], generate_commands_post=for_enemies(["shield p *"], magnitude_func=lambda e: 2*e, specifier="behind")),
  Spell("Consumer: 1 Gold: Stun faced side 1, face, deal 8 damage to immediate.", color="gold", type="Consumer",
        raw_commands=["stun iside 1", "face", "damage i 8"])],
  #
  [Spell("Passive: The first time you face in a round, deal 6 damage to immediate.", color="gold", type="Passive",
          triggers_on=passive_first_face, raw_commands=["damage i 6"]),
  Spell("Producer: +1 Gold, inflict 3 vulnerable on immediate behind.", color="gold", type="Producer", raw_commands=["vulnerable bi 3"]),
  Spell("Converter: 1 Gold -> 1 Red: Gain 2 sharp this turn, face, deal 4 to immediate.", color="gold", type="Converter", conversion_color="red",
        raw_commands=["sharp p 2", "delay 0 sharp p -2", "face", "damage i 4"]),
  Spell("Consumer: 1 Gold: Deal 8 damage to immediate. If facing no enemies, face and deal 16 damage to immediate.", color="gold", type="Consumer",
        raw_commands=["damage i 8"], generate_commands_post=if_facing_none(["face", "damage i 16"]))]
]

gold_use_last_charge = [
  [Spell("Passive: Whenever you cast a spell's last charge, gain 3 shield.", color="gold", type="Passive",
         triggers_on=passive_use_last_charge, raw_commands=["shield p 3"]),
  Spell("Producer: +1 Gold, gain 1 inventive", color="gold", type="Producer", raw_commands=["inventive p 1"]),
  Spell("Converter: 1 Gold -> 1 Blue: Gain 1 evade, turn the page, +1 time.", color="gold", type="Converter", conversion_color="blue",
        raw_commands=["evade p 1", "page", "time -1"]),
  Spell("Consumer: 1 Gold: Deal 5 to a random enemy x times, where x is amount of energy.", color="gold", type="Consumer",
        generate_commands_pre=for_player_energy(["repeat * damage r 5"]))],
  #
  [Spell("Passive: Whenever you cast a spell's last charge, gain 2 searing presence.", color="gold", type="Passive",
          triggers_on=passive_use_last_charge, raw_commands=["searing p 2"]),
  Spell("Producer: +1 Gold, If this has 0 or less charges, damage immediate 8.", color="gold", type="Producer",
        generate_commands_post=if_spell_charges(0, ["damage i 8"], above=False)),
  Spell("Converter: 1 Gold -> 1 Red: Gain 1 prolific, 2 dig deep, 3 block.", color="gold", type="Converter", conversion_color="red",
        raw_commands=["prolific p 1", "dig p 2", "block p 3"]),
  Spell("Consumer: Gain block and searing presence equal to missing charges.", color="gold", type="Consumer",
        generate_commands_pre=for_missing_charges(["block p *", "searing p *"]))]
]

# gold_page_sets = [gold_3rd_spell, gold_turn_page, gold_1_spell, gold_face_noone]
# gold_pages = gold_3rd_spell + gold_turn_page + gold_1_spell + gold_face_noone
gold_page_sets = [gold_first_face, gold_use_last_charge]
gold_pages = gold_first_face + gold_use_last_charge
gold_spells = sum(gold_pages, [])

spells = red_spells + blue_spells + gold_spells

# Blue new spells:

# Red new spells:

# Gold new spells:
