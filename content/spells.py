from model.spellbook import Spell
from content.command_generators import *
from content.trigger_functions import *

# Red Color Identity:

red_enemy_dies = [
  [Spell(rules_text="When an enemy dies, gain 4 empower and deal overkill damage to immediate.", color="red", type="Passive",
         triggers_on=passive_for_death_overkill, raw_commands=["empower p 4", "damage i ^"]),
  Spell(rules_text="inflict 1 vulnerable", color="red", type="Producer", raw_commands=["vulnerable _ 1"]),
  Spell(rules_text="Deal 10. If this kills, +1 red.", color="red", type="Converter", conversion_color="gold",
        targets=["_"], raw_commands=["damage _ 10"], generate_commands_post=if_kill("_", ["red p 1"])),
  Spell(rules_text="Deal 18", color="red", type="Consumer", raw_commands=["damage _ 18"])],
  #
  [Spell(rules_text="When an enemy dies, inflict 4 burn on random.", color="red", type="Passive",
         triggers_on=passive_for_death_overkill, raw_commands=["burn r 4"]),
  Spell(rules_text="inflict 2 burn.", color="red", type="Producer", raw_commands=["burn _ 2"]),
  Spell(rules_text="Inflict 5 burn.", color="red", type="Converter", conversion_color="blue", raw_commands=["burn _ 5"]),
  Spell(rules_text="Inflict 2 burn, then inflict their burn on all enemies.", color="red", type="Consumer",
        targets=["_"], raw_commands=["burn _ 2"], generate_commands_post=for_burn("_", ["burn a *"]))],
]

red_take_damage = [
  [Spell(rules_text="When you lose hp, gain 5 empowered.", color="red", type="Passive",
         triggers_on=passive_lose_hp, raw_commands=["empower p 5"]),
  Spell(rules_text="Deal 2. If this kills an enemy, recharge, refresh, +1 time.", color="red", type="Producer",
        raw_commands=["damage _ 2"], generate_commands_post=if_kill("_", ["time -1", "recharge last", "refresh last"])),
  Spell(rules_text="Gain 1 sharp for every missing 4 health.", color="red", type="Converter", conversion_color="gold",
        generate_commands_pre=for_player_missing_hp(4, ["sharp p *"])),
  Spell(rules_text="9 damage to all enemies on faced side.", color="red", type="Consumer", raw_commands=["damage iside 9"])],
  #
  [Spell(rules_text="When you lose hp, inflict 3 burn on all enemies.", color="red", type="Passive",
         triggers_on=passive_lose_hp, raw_commands=["burn a 3"]),
  Spell(rules_text="gain 2 regen and 2 burn.", color="red", type="Producer", raw_commands=["regen p 2", "burn p 2"]),
  Spell(rules_text="Inflict 3 burn. Heal equal to the target's burn.", color="red", type="Converter", conversion_color="gold",
        targets=["_"], raw_commands=["burn _ 3"], generate_commands_post=for_burn("_", ["heal p *"])),
  Spell(rules_text="Gain 1 regen per enemy.", color="red", type="Consumer",
        generate_commands_pre=for_enemies(["regen p *"]))], 
]

red_big_attack = [
  [Spell(rules_text="If <= half health at turn start, gain 1 red, 2 sharp, and deal 3 to random.", color="red", type="Passive",
         triggers_on=passive_at_half_health, raw_commands=["red p 1", "sharp p 2", "damage r 3"]),
  Spell(rules_text="If you're at or below half health, +2 red.", color="red", type="Producer",
        generate_commands_pre=if_player_hp(0.5, ["red p 2"], above=False)),
  Spell(rules_text="Deal 2 x times, where x is amount of energy you have.", color="red", type="Converter", conversion_color="gold",
        generate_commands_post=for_player_energy(["repeat * damage _ 2"])),
  Spell(rules_text="Deal 13. If you have 3 or more energy, recharge and refresh this.", color="red", type="Consumer",
        raw_commands=["damage _ 13"], generate_commands_post=if_player_energy(3, ["recharge last", "refresh last"]))],
  #
  [Spell(rules_text="If at or below half health at turn start, gain 4 regen.", color="red", type="Passive",
         triggers_on=passive_at_half_health, raw_commands=["regen p 4"]),
  Spell(rules_text="If at full health, deal 8, otherwise gain 1 regen.", color="red", type="Producer",
        generate_commands_pre=if_player_hp(1.0, ["damage _ 8"], else_commands=["regen p 1"], above=True)),
  Spell(rules_text="Suffer 3 damage, gain 3 sharp.", color="red", type="Converter", conversion_color="gold", raw_commands=["suffer p 3", "sharp p 3"]), # NOTE: Green
  Spell(rules_text="Deal 6. Heal for unblocked.", color="red", type="Consumer", raw_commands=["lifesteal _ 6"])],
]

red_hit_big_enemy = [
  [Spell(rules_text="When you attack an enemy: inflict 3 burn if >= 10hp remains.", color="red", type="Passive",
         triggers_on=passive_first_damage_10hp_remains, raw_commands=["burn ^ 3"]),
  Spell(rules_text="Deal 4 to immediate.", color="red", type="Producer", raw_commands=["damage i 4"]),
  Spell(rules_text="Apply 2 poison. Apply extra 1 poison for every 4 hp the target has.", color="red", type="Converter", conversion_color="blue",
        targets=["_"], generate_commands_pre=for_enemy_remaining_hp("_", 4, ["poison _ 2", "poison _ *"])), # NOTE: Purple
  Spell(rules_text="Target loses half its remaining health.", color="red", type="Consumer",
        targets=["_"], generate_commands_pre=for_enemy_remaining_hp("_", 2, ["suffer _ *"]))],
  #
  [Spell(rules_text="When you attack an enemy: gain 2 regen if >= 10hp remains.", color="red", type="Passive",
         triggers_on=passive_first_damage_10hp_remains, raw_commands=["regen p 2"]),
  Spell(rules_text="Deal 8 to a target at or above 10 health.", color="red", type="Producer",
        targets=["_"], generate_commands_pre=if_enemy_hp("_", 10, ["damage _ 8"], above=True)),
  Spell(rules_text="Deal 6. Stun 1 the target if 10 or more hp remains.", color="red", type="Converter", conversion_color="blue",
        targets=["_"], raw_commands=["damage _ 6"], generate_commands_post=if_enemy_hp("_", 10, ["stun _ 1"], above=True)),
  Spell(rules_text="Target suffers damage equal to its missing health.", color="red", type="Consumer",
        targets=["_"], generate_commands_pre=for_enemy_missing_hp("_", 1, ["suffer _ *"]))],
]

red_first_3_turns = [
  [Spell(rules_text="At start of first 3 turns, gain 4 fleeting sharp", color="red", type="Passive",
          triggers_on=passive_first_3_turns, raw_commands=["sharp p 4", "delay 0 sharp p -4"]),
  Spell(rules_text="call 1, +4 time", color="red", type="Producer", raw_commands=["call 1", "time -4"]),
  Spell(rules_text="Deal 2 to random x times, where x is 8 - turn number", color="red", type="Converter", conversion_color="blue",
        generate_commands_pre=for_turn_number(["repeat * damage r 2"], lambda t: 8 - t)),
  Spell(rules_text="Call 1 three times. Gain 6 sharp.", color="red", type="Consumer", raw_commands=["call 1", "call 1", "call 1", "sharp p 6"])],
  #
  [Spell(rules_text="At start of first 3 turns, gain 1 inventive and 1 prolific.", color="red", type="Passive",
          triggers_on=passive_first_3_turns, raw_commands=["inventive p 1", "prolific p 1"]),
  Spell(rules_text="Call 1, gain dig deep 2.", color="red", type="Producer",
        raw_commands=["call 1", "dig p 2"]),
  Spell(rules_text="Call 2. Gain 15 empower.", color="red", type="Converter", conversion_color="gold", raw_commands=["call 2", "empower p 15"]),
  Spell(rules_text="Consume all energy to deal 15 to random x times, where x is energy consumed.", color="red", type="Consumer",
        generate_commands_pre=for_player_energy(["repeat * damage r 15"], magnitude_func=lambda x: x+1),
        raw_commands=["red p =0", "blue p =0", "green p =0", "gold p =0"])]
]

red_random_target = [
  [Spell(rules_text="At turn start, inflict 3 vulnerable on a random enemy", color="red", type="Passive",
          triggers_on=passive_turn_start, raw_commands=["vulnerable r 3"]),
  Spell(rules_text="deal 6 to a random enemy.", color="red", type="Producer", raw_commands=["damage r 6"]),
  Spell(rules_text="Gain 2 sharp this turn, inflict 2 vulnerable on all enemies.", color="red", type="Converter", conversion_color="gold",
        raw_commands=["sharp p 2", "delay 0 sharp p -2", "vulnerable a 2"]),
  Spell(rules_text="Deal 12 to any target.", color="red", type="Consumer", raw_commands=["damage _ 12"])],
  #
  [Spell(rules_text="At turn start, inflict 4 poison on a random enemy", color="red", type="Passive",
          triggers_on=passive_turn_start, raw_commands=["poison r 4"]),
  Spell(rules_text="deal 3 to a random enemy twice.", color="red", type="Producer", raw_commands=["damage r 3", "damage r 3"]),
  Spell(rules_text="Inflict 8 poison on a damaged enemy.", color="red", type="Converter", conversion_color="blue", raw_commands=["poison _damaged 8"]),
  Spell(rules_text="Gain 5 regen, then you and all enemies get 5 vulnerable.", color="red", type="Consumer", raw_commands=["regen p 5", "vulnerable a 5", "vulnerable p 5"])]
]

red_page_sets = [red_enemy_dies, red_take_damage, red_big_attack, red_hit_big_enemy, red_first_3_turns, red_random_target]
red_pages = red_enemy_dies + red_take_damage + red_big_attack + red_hit_big_enemy + red_first_3_turns + red_random_target
red_spells = sum(red_pages, [])

# Blue Color Identity

blue_block_hits = [
  [Spell(rules_text="When you’re attacked and take no damage, deal 6 to attacker and shield 1.", color="blue", type="Passive",
         triggers_on=passive_attacked_for_no_damage, raw_commands=["shield p 1", "damage ^ 6"]),
  Spell(rules_text="gain 1 block per enemy.", color="blue", type="Producer",
        generate_commands_pre=for_enemies(["block p *"])),
  Spell(rules_text="Gain 9 block", color="blue", type="Converter", conversion_color="gold", raw_commands=["block p 9"]),  # NOTE: Green
  Spell(rules_text="Gain 8 armor this turn.", color="blue", type="Consumer",
        raw_commands=["armor p 8", "delay 0 armor p -8"])],
  #
  [Spell(rules_text="When you’re attacked and take no damage, gain 3 retaliate and shield 1", color="blue", type="Passive",
         triggers_on=passive_attacked_for_no_damage, raw_commands=["retaliate p 3", "shield p 1"]),
  Spell(rules_text="Block 2. Break: deal 8 to attacker.", color="blue", type="Producer", raw_commands=["block p 2", "break damage ^ 8"]),
  Spell(rules_text="Block 5. Deal 5.", color="blue", type="Converter", conversion_color="gold", raw_commands=["block p 5", "damage _ 5"]),
  Spell(rules_text="Block 10. Break: Deal 30 to attacker.", color="blue", type="Consumer", raw_commands=["block p 10", "break damage ^ 30"])],
]

blue_turn_3 = [
  [Spell(rules_text="At start of 3rd turn and onwards, block 4.", color="blue", type="Passive",
         triggers_on=passive_turn_3_onwards_at_begin, raw_commands=["block p 4"]),
  Spell(rules_text="Inflict 1 stun on an enemy that entered this turn.", color="blue", type="Producer", raw_commands=["stun _entered 1"]),
  Spell(rules_text="Stun 1 or deal 15 to a stunned enemy.", color="blue", type="Converter", conversion_color="red",
        targets=["_"], generate_commands_pre=if_enemy_condition("_", "stun", 1, ["damage _ 15"], else_commands=["stun _ 1"], above=True)),
  Spell(rules_text="Inflict 3 stun.", color="blue", type="Consumer", raw_commands=["stun _ 3"])],
  #
  [Spell(rules_text="At start of 3rd turn and onwards, deal 3 to all enemies.", color="blue", type="Passive",
         triggers_on=passive_turn_3_onwards_at_begin, raw_commands=["damage a 3"]),
  Spell(rules_text="ward 1.", color="blue", type="Producer", raw_commands=["ward p 1"]),
  Spell(rules_text="At the end of next round, all enemies take 8 damage.", color="blue", type="Converter", conversion_color="red",
        raw_commands=["delay 1 damage a 8"]),
  Spell(rules_text="Ward 4.", color="blue", type="Consumer", raw_commands=["ward p 4"])],
]

blue_3_enemies = [
  [Spell(rules_text="At turn start, if there are >= 3 enemies, stun 2 of them at random.", color="blue", type="Passive",
         triggers_on=passive_3_plus_enemies_at_begin, raw_commands=["stun r 1", "stun r 1"]),
  Spell(rules_text="gain 2 block and Break: stun 1.", color="blue", type="Producer", raw_commands=["block p 2", "break stun ^ 1"]),
  Spell(rules_text="Gain retaliate 4.", color="blue", type="Converter", conversion_color="gold", raw_commands=["retaliate p 4"]),
  Spell(rules_text="Deal 6 to all stunned enemies. Stun 1 all enemies on faced side", color="blue", type="Consumer",
        generate_commands_pre=["damage ?stun 6"], raw_commands=["stun iside 1"])],
  #
  [Spell(rules_text="At turn start, if there >= 3 enemies, deal 15 to random.", color="blue", type="Passive",
         triggers_on=passive_3_plus_enemies_at_begin, raw_commands=["damage r 15"]),
  Spell(rules_text="deal 6, call 1", color="blue", type="Producer", raw_commands=["damage _ 6", "call 1"]),
  Spell(rules_text="Gain retaliate 10 this turn.", color="blue", type="Converter", conversion_color="gold",
        raw_commands=["retaliate p 10", "delay 0 retaliate p -10"]),
  Spell(rules_text="At the end of next round, deal 15 to random three times.", color="blue", type="Consumer",
        raw_commands=["delay 1 repeat 3 damage r 15"])],
]

blue_excess_block = [
  [Spell(rules_text="Excess block/shield at turn end is dealt as damage to immediate.", color="blue", type="Passive",
         triggers_on=passive_block_and_shield_at_end, raw_commands=["damage i ^"]),
  Spell(rules_text="Gain 4 block.", color="blue", type="Producer", raw_commands=["block p 4"]),
  Spell(rules_text="Gain 1 armor and 2 retaliate.", color="blue", type="Converter", conversion_color="red", raw_commands=["armor p 1", "retaliate p 2"]),
  Spell(rules_text="Gain 20 block.", color="blue", type="Consumer", raw_commands=["block p 20"])],
  #
  [Spell(rules_text="At round end, gain shield equal to block.", color="blue", type="Passive",
         triggers_on=passive_block_at_round_end, raw_commands=["shield p ^"]),
  Spell(rules_text="+2 shield.", color="blue", type="Producer", raw_commands=["shield p 2"]),
  Spell(rules_text="Block 2. Convert block into 2x shield.", color="blue", type="Converter", conversion_color="gold",
        raw_commands=["block p 2"], generate_commands_post=for_player_condition(["block"], ["shield p *", "block p =0"], lambda b: 2*b)),
  Spell(rules_text="Gain 7 block. Deal damage equal to block + shield to target.", color="blue", type="Consumer",
        raw_commands=["block p 7"], generate_commands_post=for_player_condition(["block", "shield"], ["damage _ *"], lambda b: b))],
]

blue_no_enemy_deaths = [
  [Spell(rules_text="At turn start, if no enemies are dead, gain 8 block.", color="blue", type="Passive",
          triggers_on=passive_no_dead_enemies_at_begin, raw_commands=["block p 8"]),
  Spell(rules_text="encase self 5", color="blue", type="Producer", raw_commands=["encase p 5"]),
  Spell(rules_text="Inflict 5 doom.", color="blue", type="Converter", conversion_color="red",
        raw_commands=["doom _ 5"]),
  Spell(rules_text="Encase 12 an enemy and inflict 3 doom.", color="blue", type="Consumer",
        targets=["_"], raw_commands=["encase _ 12", "doom _ 3"])],
  #
  [Spell(rules_text="At turn start, if no enemies are dead, ward self 1.", color="blue", type="Passive",
          triggers_on=passive_no_dead_enemies_at_begin, raw_commands=["ward p 1"]),
  Spell(rules_text="Deal 6 to random 1 turn from now.", color="blue", type="Producer",
        raw_commands=["delay 1 damage r 6"]),
  Spell(rules_text="Gain x time, x empower, and x block, where x is # of enemies", color="blue", type="Converter", conversion_color="gold",
        generate_commands_pre=for_enemies(["time -*", "empower p *", "block p *"])),
  Spell(rules_text="Deal 2x to all enemies, where x is turn number.", color="blue", type="Consumer",
        generate_commands_pre=for_turn_number(["damage a *"], lambda s: 2*s))],
]

blue_on_entry = [
  [Spell(rules_text="When an enemy enters, gain 1 retaliate and 3 block.", color="blue", type="Passive",
          triggers_on=passive_on_entry, raw_commands=["retaliate p 1", "block p 3"]),
  Spell(rules_text="inflict 2 poison.", color="blue", type="Producer", raw_commands=["poison _ 2"]),
  Spell(rules_text="Block 4. Break: Poison 4 all enemies.", color="blue", type="Converter", conversion_color="red",
        raw_commands=["block p 4", "break poison a 4"]),
  Spell(rules_text="Banish three enemies immediately in front and behind for this round.", color="blue", type="Consumer",
        raw_commands=["repeat 3 banish i 0", "repeat 3 banish bi 0"])],
  #
  [Spell(rules_text="When an enemy enters, deal it 4.", color="blue", type="Passive",
          triggers_on=passive_on_entry, raw_commands=["damage ^ 4"]),
  Spell(rules_text="deal 5 to an enemy that entered this turn.", color="blue", type="Producer", raw_commands=["damage _entered 5"]),
  Spell(rules_text="Deal 12 to the furthest faced enemy.", color="blue", type="Converter", conversion_color="gold",
        raw_commands=["damage distant 12"]),
  Spell(rules_text="Banish 2 an enemy.", color="blue", type="Consumer", raw_commands=["banish _ 2"])]
]

blue_page_sets = [blue_block_hits, blue_turn_3, blue_3_enemies, blue_excess_block, blue_no_enemy_deaths, blue_on_entry]
blue_pages = blue_block_hits + blue_turn_3 + blue_3_enemies + blue_excess_block + blue_no_enemy_deaths + blue_on_entry
blue_spells = sum(blue_pages, [])

# Gold Color Identity:

gold_3rd_spell = [
  [Spell(rules_text="When you cast your 3rd spell in a turn, gain 3 sharp.", color="gold", type="Passive",
         triggers_on=passive_third_spell_in_turn, raw_commands=["sharp p 3"]),
  Spell(rules_text="Deal 2 to each adjacent enemy.", color="gold", type="Producer", raw_commands=["damage f1 2", "damage b1 2"]),
  Spell(rules_text="Deal 4 to immediate enemy. Repeat twice more.", color="gold", type="Converter", conversion_color="red", raw_commands=["damage i 4", "damage i 4", "damage i 4"]),
  Spell(rules_text="Deal 12 to immediate, deal 8 to immediate behind.", color="gold", type="Consumer", raw_commands=["damage i 12", "damage bi 8"])],
  #
  [Spell(rules_text="When you cast your 3rd spell in a turn, gain 20 block.", color="gold", type="Passive",
         triggers_on=passive_third_spell_in_turn, raw_commands=["block p 20"]),
  Spell(rules_text="Recharge this spell.", color="gold", type="Producer", raw_commands=["recharge last"]),
  Spell(rules_text="Gain 5 fleeting retaliate and 5 block. Refresh this.", color="gold", type="Converter", conversion_color="blue",
        raw_commands=["retaliate p 5", "block p 5", "delay 0 retaliate p -5", "refresh last"]),
  Spell(rules_text="Gain 6 searing presence.", color="gold", type="Consumer", raw_commands=["searing p 6"])],
]

gold_turn_page = [
  [Spell(rules_text="When you turn to this page, recharge a random spell and +1 time.", color="gold", type="Passive",
         triggers_on=passive_on_page, raw_commands=["recharge r", "time -1"]),
  Spell(rules_text="Gain 1 regen", color="gold", type="Producer", raw_commands=["regen p 1"]),
  Spell(rules_text="Deal 6 to immediate. Gain 1 empower for each missing spell charge on page.", color="gold", type="Converter", conversion_color="red",
        raw_commands=["damage i 6"], generate_commands_post=for_missing_charges(["empower p *"])),
  Spell(rules_text="Gain Dig Deep 3 and 3 shield. +3 time.", color="gold", type="Consumer", raw_commands=["dig p 3", "time -3", "shield p 3"])],
  #
  [Spell(rules_text="When you turn to this page, gain 2 inventive and +1 time", color="gold", type="Passive",
         triggers_on=passive_on_page, raw_commands=["inventive p 2", "time -1"]),
  Spell(rules_text="Recharge and refresh a spell.", color="gold", type="Producer"), # TODO: make this prompt you with a choice
  Spell(rules_text="Gain 5 block and break: Gain searing presence 5. Refresh this.", color="gold", type="Converter", conversion_color="red",
        raw_commands=["block p 5", "break searing p 5", "refresh last"]),
  Spell(rules_text="Gain 2x shield and deal 2x to all where x is # of spells cast this turn.", color="gold", type="Consumer",
        generate_commands_pre=for_spells_cast(["shield p *", "damage a *"], lambda s: 2*s))], 
]

gold_1_spell = [
  [Spell(rules_text="If you cast 1 or less spell in a turn, gain 1 energy of any color.", color="gold", type="Passive",
         triggers_on=passive_1_spell_in_turn, raw_commands=["wild"]),
  Spell(rules_text="you may convert 1 energy to another color.", color="gold", type="Producer"),
  Spell(rules_text="Deal 7. Deal 7. Gain 2 slow.", color="gold", type="Converter", conversion_color="red",
        raw_commands=["damage _ 7", "damage _ 7", "slow p 2"]),
  Spell(rules_text="Gain 5 retaliate and 10 block", color="gold", type="Consumer", raw_commands=["retaliate p 5", "block p 10"])],
  #
  [Spell(rules_text="If you cast 1 or less spell in a turn, empower 7.", color="gold", type="Passive",
         triggers_on=passive_1_spell_in_turn, raw_commands=["empower p 7"]),
  Spell(rules_text="+2 time.", color="gold", type="Producer", raw_commands=["time -2"]),
  Spell(rules_text="Deal 8 to immediate. If this kills, recharge and refresh.", color="gold", type="Converter", conversion_color="red",
        targets=["i"], raw_commands=["damage i 8"], generate_commands_post=if_kill("i", ["recharge last", "refresh last"])),
  Spell(rules_text="Gain 3 prolific.", color="gold", type="Consumer", raw_commands=["prolific p 3"])],
]

gold_face_noone = [
  [Spell(rules_text="At turn end, if facing no enemies, gain 2 searing presence.", color="gold", type="Passive",
         triggers_on=passive_face_noone_at_end, raw_commands=["searing p 2"]),
  Spell(rules_text="gain 2 searing presence.", color="gold", type="Producer", raw_commands=["searing p 2"]),
  Spell(rules_text="Banish immediate enemy.", color="gold", type="Converter", conversion_color="red",
        targets=["i"], raw_commands=["banish i"]),
  Spell(rules_text="Gain 2 armor.", color="gold", type="Consumer", raw_commands=["armor p 2"])],
  #
  [Spell(rules_text="At turn end, if facing no enemies, gain 3 shield.", color="gold", type="Passive",
         triggers_on=passive_face_noone_at_end, raw_commands=["shield p 3"]),
  Spell(rules_text="if facing no enemies, empower 5.", color="gold", type="Producer",
        generate_commands_pre=if_facing_none(["empower p 5"])),
  Spell(rules_text="Gain 5 shield.", color="gold", type="Converter", conversion_color="blue", raw_commands=["shield p 5"]),
  Spell(rules_text="Deal 10 to immediate. If this kills an enemy, empower 10.", color="gold", type="Consumer",
        targets=["i"], raw_commands=["damage i 10"], generate_commands_post=if_kill("i", ["empower p 10"]))],
]

gold_first_face = [
  [Spell(rules_text="Whenever you face, gain 3 block.", color="gold", type="Passive",
          triggers_on=passive_on_face, raw_commands=["block p 3"]),
  Spell(rules_text="Stun 1 immediate behind.", color="gold", type="Producer", raw_commands=["stun bi 1"]),
  Spell(rules_text="Gain 2 shield for each enemy behind.", color="gold", type="Converter", conversion_color="blue",
        raw_commands=[], generate_commands_post=for_enemies(["shield p *"], magnitude_func=lambda e: 2*e, specifier="behind")),
  Spell(rules_text="Deal 8 to immediate x times where x is # of enemies behind.", color="gold", type="Consumer",
        generate_commands_post=for_enemies(["repeat * damage i 8"], specifier="behind"))],
  #
  [Spell(rules_text="Whenever you face, deal 3 to immediate.", color="gold", type="Passive",
          triggers_on=passive_on_face, raw_commands=["damage i 3"]),
  Spell(rules_text="inflict 4 vulnerable on immediate behind.", color="gold", type="Producer", raw_commands=["vulnerable bi 4"]),
  Spell(rules_text="Gain 2 sharp this turn, face, deal 5 to immediate.", color="gold", type="Converter", conversion_color="red",
        raw_commands=["sharp p 2", "delay 0 sharp p -2", "face!", "damage i 5"]),
  Spell(rules_text="Deal 12 to immediate. If this kills, face deal 12 to immediate.", color="gold", type="Consumer",
        targets=["i"], raw_commands=["damage i 12"], generate_commands_post=if_kill("i", ["face!", "damage i 12"]))]
]

gold_use_last_charge = [
  [Spell(rules_text="When you cast a spell's last charge, gain 6 shield.", color="gold", type="Passive",
         triggers_on=passive_use_last_charge, raw_commands=["shield p 6"]),
  Spell(rules_text="gain 1 inventive", color="gold", type="Producer", raw_commands=["inventive p 1"]),
  Spell(rules_text="Gain 3 shield. Gain 5 empower.", color="gold", type="Converter", conversion_color="blue",
        raw_commands=["shield p 3", "empower p 5"]),
  Spell(rules_text="Deal 6 to immediate x times, where x is amount of energy.", color="gold", type="Consumer",
        generate_commands_pre=for_player_energy(["repeat * damage i 6"], magnitude_func=lambda x: x+1))],
  #
  [Spell(rules_text="When you cast a spell's last charge, deal 8 to immediate.", color="gold", type="Passive",
          triggers_on=passive_use_last_charge, raw_commands=["damage i 8"]),
  Spell(rules_text="Gain dig deep 1.", color="gold", type="Producer", raw_commands=["dig p 1"]),
  Spell(rules_text="Gain 3 inventive, 3 shield.", color="gold", type="Converter", conversion_color="red",
        raw_commands=["inventive p 3", "shield p 3"]),
  Spell(rules_text="Gain block and searing presence equal to missing charges on page.", color="gold", type="Consumer",
        generate_commands_pre=for_missing_charges(["block p *", "searing p *"]))]
]

gold_page_sets = [gold_3rd_spell, gold_turn_page, gold_1_spell, gold_face_noone, gold_first_face, gold_use_last_charge]
gold_pages = gold_3rd_spell + gold_turn_page + gold_1_spell + gold_face_noone + gold_first_face + gold_use_last_charge
gold_spells = sum(gold_pages, [])

spells = red_spells + blue_spells + gold_spells

spells_by_id = {}
for i, spell in enumerate(spells):
  spell.id = i
  spells_by_id[i] = spell

# TODO ideas:
# - to make straight damage stronger -- effects like break that trigger on hitting stuff
# - Double your empower?
# - on-hit effects (no limit)
# - stuff that turns enemy's power against them? Doom?
# - when you get big attacked?
# - Mark, which is like sharp for a specific enemy -- to help you burst down a specific enemy.
# - passive that scales off when you cast a spell?