from model.spellbook import Spell
from content.command_generators import *
from content.trigger_functions import *

# Red Color Identity:

red_enemy_dies = [
  [Spell(rules_text="When an enemy dies, gain 4 empower and deal overkill damage to immediate.", color="red", type="Passive",
         triggers_on=passive_for_death_overkill, raw_commands=["empower p 4", "damage i ^"]),
  Spell(rules_text="inflict 1 vulnerable", color="red", type="Producer", raw_commands=["vulnerable _ 1"]),
  Spell(rules_text="Deal 9 damage. If this kills, +1 red.", color="red", type="Converter", conversion_color="gold",
        targets=["_"], raw_commands=["damage _ 9"], generate_commands_post=if_kill("_", ["red p 1"])),
  Spell(rules_text="Deal 16 damage", color="red", type="Consumer", raw_commands=["damage _ 16"])],
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
  Spell(rules_text="deal 2 damage. If this kills an enemy, recharge, refresh, +1 time.", color="red", type="Producer",
        raw_commands=["damage _ 2"], generate_commands_post=if_kill("_", ["time -1", "recharge last"])),
  Spell(rules_text="Gain 1 sharp for every missing 4 health.", color="red", type="Converter", conversion_color="gold",
        generate_commands_pre=for_player_missing_hp(4, ["sharp p *"])),
  Spell(rules_text="8 damage to all enemies on target side.", color="red", type="Consumer", raw_commands=["damage iside 8"])],
  #
  [Spell(rules_text="When you lose hp, inflict 3 burn on all enemies.", color="red", type="Passive",
         triggers_on=passive_lose_hp, raw_commands=["burn a 3"]),
  Spell(rules_text="gain 2 regen and 2 burn.", color="red", type="Producer", raw_commands=["regen p 2", "burn p 2"]),
  Spell(rules_text="Gain 2 regen. Inflict 3 burn.", color="red", type="Converter", conversion_color="gold", raw_commands=["regen p 2", "burn _ 3"]),  # NOTE: Purple
  Spell(rules_text="Inflict 3 burn. Tick all burn and gain life equal to damage dealt in this way.", color="red", type="Consumer", raw_commands=["burn _ 3"])], 
]

red_big_attack = [
  [Spell(rules_text="Gain 1 red, 1 sharp, and 1 prolific for every 6 damage you survive each round.", color="red", type="Passive",
         triggers_on=passive_for_survive_6_damage_in_turn, raw_commands=["red p ^", "sharp p ^", "prolific p ^"]),
  Spell(rules_text="If you're at or below half health, +1 red.", color="red", type="Producer",
        generate_commands_pre=if_player_hp(0.5, ["red p 1"], above=False)),
  # TODO: Fix this -- it's bugged and does 1 less energy than it should I think because the conversion is not instant?
  Spell(rules_text="Deal 2 damage x times, where x is amount of energy you have.", color="red", type="Converter", conversion_color="gold",
        generate_commands_post=for_player_energy(["repeat * damage _ 2"])),
  # TODO: implement the 3+ energy part
  Spell(rules_text="Deal 11 damage. If you have 3 or more energy, recharge and refresh this.", color="red", type="Consumer", raw_commands=["damage _ 11"])],
  #
  [Spell(rules_text="Gain 1 regen, deal 3 damage to all for every 6 damage you survive each round.", color="red", type="Passive",
         triggers_on=passive_for_survive_6_damage_in_turn, raw_commands=["regen p ^", "repeat ^ damage a 3"]),
  Spell(rules_text="If at full health, deal 6 damage, otherwise gain 1 regen.", color="red", type="Producer",
        generate_commands_pre=if_player_hp(1.0, ["damage _ 6"], else_commands=["regen p 1"], above=True)),
  Spell(rules_text="Suffer 3 damage, gain 3 sharp.", color="red", type="Converter", conversion_color="gold", raw_commands=["suffer p 3", "sharp p 3"]), # NOTE: Green
  Spell(rules_text="Deal 6 damage. Heal for unblocked.", color="red", type="Consumer", raw_commands=["lifesteal _ 6"])],
]

red_hit_big_enemy = [
  [Spell(rules_text="The 1st time you damage each enemy in a turn, inflict 5 burn if at least 10hp remains.", color="red", type="Passive",
         triggers_on=passive_first_damage_10hp_remains, raw_commands=["burn ^ 5"]),
  Spell(rules_text="Deal 4 damage to immediate.", color="red", type="Producer", raw_commands=["damage i 4"]),
  Spell(rules_text="Apply 1 poison. Apply extra 1 poison for every 4 hp the target has.", color="red", type="Converter", conversion_color="blue",
        targets=["_"], generate_commands_pre=for_enemy_remaining_hp("_", 5, ["poison _ 1", "poison _ *"])), # NOTE: Purple
  Spell(rules_text="Target loses half its remaining health.", color="red", type="Consumer",
        targets=["_"], generate_commands_pre=for_enemy_remaining_hp("_", 2, ["suffer _ *"]))],
  #
  [Spell(rules_text="The 1st time you damage each enemy in a turn, gain 3 regen if at least 10hp remains.", color="red", type="Passive",
         triggers_on=passive_first_damage_10hp_remains, raw_commands=["regen p 3"]),
  Spell(rules_text="Deal 6 damage to a target at or above 10 health.", color="red", type="Producer",
        targets=["_"], generate_commands_pre=if_enemy_hp("_", 10, ["damage _ 6"], above=True)),
  # TODO: make the stun target the same enemy automatically
  Spell(rules_text="Deal 6 damage. Stun 1 the target if 10 or more hp remains.", color="red", type="Converter", conversion_color="blue",
        targets=["_"], raw_commands=["damage _ 6"], generate_commands_post=if_enemy_hp("_", 10, ["stun _ 1"], above=True)),
  Spell(rules_text="Deal damage equal to target's missing health.", color="red", type="Consumer",
        targets=["_"], generate_commands_pre=for_enemy_missing_hp("_", 1, ["damage _ *"]))],
]

red_first_3_turns = [
  [Spell(rules_text="At start of first 3 turns, gain 3 fleeting sharp", color="red", type="Passive",
          triggers_on=passive_first_3_turns, raw_commands=["sharp p 3", "delay 0 sharp p -3"]),
  Spell(rules_text="call 1, +3 time", color="red", type="Producer", raw_commands=["call 1", "time -3"]),
  Spell(rules_text="Deal 2 damage to random x times, where x is 8 - turn number", color="red", type="Converter", conversion_color="blue",
        generate_commands_pre=for_turn_number(["repeat * damage r 2"], lambda t: 8 - t)),
  Spell(rules_text="Call 1 three times. Gain 6 sharp.", color="red", type="Consumer", raw_commands=["call 1", "call 1", "call 1", "sharp p 6"])],
  #
  [Spell(rules_text="At start of first 3 turns, gain 1 inventive and 1 prolific.", color="red", type="Passive",
          triggers_on=passive_first_3_turns, raw_commands=["inventive p 1", "prolific p 1"]),
  Spell(rules_text="If this has 0 or less charges, gain dig deep 2.", color="red", type="Producer",
        generate_commands_post=if_spell_charges(0, ["dig p 2"], above=False)),
  Spell(rules_text="Call 2. Gain 15 empower.", color="red", type="Converter", conversion_color="gold", raw_commands=["call 2", "empower p 15"]),
  Spell(rules_text="Regen 1. If this has 0 or less charges, deal 12 damage to random twice.", color="red", type="Consumer",
        raw_commands=["regen p 1"], generate_commands_post=if_spell_charges(0, ["damage r 12", "damage r 12"], above=False))]
]

red_random_target = [
  [Spell(rules_text="At turn start, inflict 1 vulnerable on a random enemy", color="red", type="Passive",
          triggers_on=passive_turn_start, raw_commands=["vulnerable r 1"]),
  Spell(rules_text="deal 3 damage to a random enemy.", color="red", type="Producer", raw_commands=["damage r 3"]),
  Spell(rules_text="Gain 2 sharp this turn, inflict 2 vulnerable on all enemies.", color="red", type="Converter", conversion_color="gold",
        raw_commands=["sharp p 2", "delay 0 sharp p -2", "vulnerable a 2"]),
  Spell(rules_text="Deal 12 damage to any target.", color="red", type="Consumer", raw_commands=["damage _ 12"])],
  #
  [Spell(rules_text="At turn start, inflict 3 poison on a random enemy", color="red", type="Passive",
          triggers_on=passive_turn_start, raw_commands=["poison r 3"]),
  Spell(rules_text="deal 2 damage to a random enemy twice.", color="red", type="Producer", raw_commands=["damage r 2", "damage r 2"]),
  Spell(rules_text="Inflict 6 poison on a damaged enemy.", color="red", type="Converter", conversion_color="blue", raw_commands=["poison _damaged 6"]),
  Spell(rules_text="Gain 4 regen and 4 vulnerable.", color="red", type="Consumer", raw_commands=["regen p 4", "vulnerable p 4"])]
]

red_page_sets = [red_enemy_dies, red_take_damage, red_big_attack, red_hit_big_enemy, red_first_3_turns, red_random_target]
red_pages = red_enemy_dies + red_take_damage + red_big_attack + red_hit_big_enemy + red_first_3_turns + red_random_target
red_spells = sum(red_pages, [])

# Blue Color Identity

blue_block_hits = [
  [Spell(rules_text="When you’re attacked and take no damage, deal 6 damage to attacker and shield 1.", color="blue", type="Passive",
         triggers_on=passive_attacked_for_no_damage, raw_commands=["damage ^ 6", "shield p 1"]),
  Spell(rules_text="gain 1 block per enemy.", color="blue", type="Producer",
        generate_commands_pre=for_enemies(["block p *"])),
  Spell(rules_text="Gain 9 block", color="blue", type="Converter", conversion_color="gold", raw_commands=["block p 9"]),  # NOTE: Green
  Spell(rules_text="Gain 8 armor this turn.", color="blue", type="Consumer",
        raw_commands=["armor p 8", "delay 0 armor p -8"])],
  #
  [Spell(rules_text="When you’re attacked and take no damage, gain 3 retaliate and shield 1", color="blue", type="Passive",
         triggers_on=passive_attacked_for_no_damage, raw_commands=["retaliate p 3", "shield p 1"]),
  Spell(rules_text="gain 1 block and Break: deal 6 damage to attacker.", color="blue", type="Producer", raw_commands=["block p 1", "break damage ^ 6"]),
  Spell(rules_text="Block 5. Deal 4 damage.", color="blue", type="Converter", conversion_color="gold", raw_commands=["block p 5", "damage _ 4"]),
  # TODO: implement the damage scaling part
  Spell(rules_text="Block 4. Break: Deal 4 times the breaker’s attack damage back.", color="blue", type="Consumer", raw_commands=["block p 4"])],
]

blue_turn_3 = [
  [Spell(rules_text="At start of 3rd turn and onwards, block 4.", color="blue", type="Passive",
         triggers_on=passive_turn_3_onwards_at_begin, raw_commands=["block p 4"]),
  Spell(rules_text="Inflict 1 stun on an enemy that entered this turn.", color="blue", type="Producer", raw_commands=["stun _entered 1"]),
  Spell(rules_text="Stun 1 or deal 15 damage to a stunned enemy.", color="blue", type="Converter", conversion_color="red",
        targets=["_"], generate_commands_pre=if_enemy_condition("_", "stun", 1, ["damage _ 15"], else_commands=["stun _ 1"], above=True)),
  Spell(rules_text="Inflict 3 stun.", color="blue", type="Consumer", raw_commands=["stun _ 3"])],
  #
  [Spell(rules_text="At start of 3rd turn and onwards, deal 3 damage to all enemies.", color="blue", type="Passive",
         triggers_on=passive_turn_3_onwards_at_begin, raw_commands=["damage a 3"]),
  Spell(rules_text="ward 1.", color="blue", type="Producer", raw_commands=["ward p 1"]),
  Spell(rules_text="At the end of next turn, all enemies take 8 damage.", color="blue", type="Converter", conversion_color="red",
        raw_commands=["delay 1 damage a 8"]),
  Spell(rules_text="Ward 4.", color="blue", type="Consumer", raw_commands=["ward p 4"])],
]

blue_3_enemies = [
  [Spell(rules_text="At start of your turn if there are 3 or more enemies, stun 2 of them at random.", color="blue", type="Passive",
         triggers_on=passive_3_plus_enemies_at_begin, raw_commands=["stun r 1", "stun r 1"]),
  Spell(rules_text="gain 1 block and Break: stun 1.", color="blue", type="Producer", raw_commands=["block p 1", "break stun ^ 1"]),
  Spell(rules_text="Gain retaliate 3.", color="blue", type="Converter", conversion_color="gold", raw_commands=["retaliate p 3"]),
  Spell(rules_text="Deal 6 damage to all stunned enemies. Stun 1 all enemies.", color="blue", type="Consumer", raw_commands=["stun a 1"])],
  #
  [Spell(rules_text="At start of your turn, if there are 3 or more enemies, deal 15 damage to a random enemy.", color="blue", type="Passive",
         triggers_on=passive_3_plus_enemies_at_begin, raw_commands=["damage r 15"]),
  Spell(rules_text="deal 6 damage, call 1", color="blue", type="Producer", raw_commands=["damage _ 6", "call 1"]),
  Spell(rules_text="Gain retaliate 6 this turn.", color="blue", type="Converter", conversion_color="gold",
        raw_commands=["retaliate p 6", "delay 0 retaliate p -6"]),
  Spell(rules_text="Gain 3 enduring this turn.", color="blue", type="Consumer",
        raw_commands=["enduring p 3", "delay 0 enduring p -3"])],
]

blue_excess_block = [
  [Spell(rules_text="Excess block/shield at turn end is dealt as damage to immediate.", color="blue", type="Passive",
         triggers_on=passive_block_and_shield_at_end, raw_commands=["damage i ^"]),
  Spell(rules_text="Gain 4 block.", color="blue", type="Producer", raw_commands=["block p 4"]),
  Spell(rules_text="Gain 1 armor and 1 retaliate.", color="blue", type="Converter", conversion_color="red", raw_commands=["armor p 1", "retaliate p 1"]),
  Spell(rules_text="Gain 20 block.", color="blue", type="Consumer", raw_commands=["block p 20"])],
  #
  [Spell(rules_text="At turn end, gain shield equal to block.", color="blue", type="Passive",
         triggers_on=passive_block_at_end, raw_commands=["shield p ^"]),
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
  Spell(rules_text="Inflict 4 doom.", color="blue", type="Converter", conversion_color="red",
        raw_commands=["doom _ 4"]),
  Spell(rules_text="Encase 12 an enemy and inflict 2 doom.", color="blue", type="Consumer",
        raw_commands=["encase _ 12", "doom _ 2"])],
  #
  [Spell(rules_text="At turn start, if no enemies are dead, ward self 1.", color="blue", type="Passive",
          triggers_on=passive_no_dead_enemies_at_begin, raw_commands=["ward p 1"]),
  Spell(rules_text="Deal 6 damage to random 1 turn from now.", color="blue", type="Producer",
        raw_commands=["delay 1 damage r 6"]),
  Spell(rules_text="Gain x time, x empower, and x block, where x is # of enemies", color="blue", type="Converter", conversion_color="gold",
        generate_commands_pre=for_enemies(["time -*", "empower p *", "block p *"])),
  Spell(rules_text="Deal 2x damage to all enemies, where x is turn number.", color="blue", type="Consumer",
        generate_commands_pre=for_turn_number(["damage a *"], lambda s: 2*s))],
]

blue_on_entry = [
  [Spell(rules_text="When an enemy enters, gain 1 retaliate and 2 block.", color="blue", type="Passive",
          triggers_on=passive_on_entry, raw_commands=["retaliate p 1", "block p 2"]),
  Spell(rules_text="inflict 1 poison.", color="blue", type="Producer", raw_commands=["poison _ 1"]),
  Spell(rules_text="Block 4. Break: Poison 4 all enemies.", color="blue", type="Converter", conversion_color="red",
        raw_commands=["block p 4", "break poison a 4"]),
  Spell(rules_text="All enemies gain 1 undying. You gain 3 shield for each enemy.", color="blue", type="Consumer",
        raw_commands=["undying a 1"], generate_commands_pre=for_enemies(["shield p *"], lambda s: 3*s))],
  #
  [Spell(rules_text="When an enemy enters, deal it 3 damage.", color="blue", type="Passive",
          triggers_on=passive_on_entry, raw_commands=["damage ^ 3"]),
  Spell(rules_text="deal 5 damage to an enemy that entered this turn.", color="blue", type="Producer", raw_commands=["damage _entered 5"]),
  Spell(rules_text="Deal 10 damage to the furthest faced enemy.", color="blue", type="Converter", conversion_color="gold",
        raw_commands=["damage distant 10"]),
  Spell(rules_text="Banish 2 an enemy.", color="blue", type="Consumer", raw_commands=["banish _ 2"])]
]

blue_page_sets = [blue_block_hits, blue_turn_3, blue_3_enemies, blue_excess_block, blue_no_enemy_deaths, blue_on_entry]
blue_pages = blue_block_hits + blue_turn_3 + blue_3_enemies + blue_excess_block + blue_no_enemy_deaths + blue_on_entry
blue_spells = sum(blue_pages, [])

# Gold Color Identity:

gold_3rd_spell = [
  [Spell(rules_text="When you cast your 3rd spell in a turn, gain 3 sharp.", color="gold", type="Passive",
         triggers_on=passive_third_spell_in_turn, raw_commands=["sharp p 3"]),
  Spell(rules_text="Deal 2 damage to each adjacent enemy.", color="gold", type="Producer", raw_commands=["damage f1 2", "damage b1 2"]),
  Spell(rules_text="Deal 3 damage to immediate enemy. Repeat twice more.", color="gold", type="Converter", conversion_color="red", raw_commands=["damage i 3", "damage i 3", "damage i 3"]),
  Spell(rules_text="Deal 12 damage to immediate, deal 6 damage to immediate behind.", color="gold", type="Consumer", raw_commands=["damage i 12", "damage bi 6"])],
  #
  [Spell(rules_text="When you cast your 3rd spell in a turn, gain 9 block.", color="gold", type="Passive",
         triggers_on=passive_third_spell_in_turn, raw_commands=["block p 9"]),
  Spell(rules_text="gain 1 regen.", color="gold", type="Producer", raw_commands=["regen p 1"]),
  Spell(rules_text="+3 time. Every spell you cast after this gives 1 retaliation.", color="gold", type="Converter", conversion_color="blue", raw_commands=["time -3"]),
  Spell(rules_text="Gain 5 searing presence.", color="gold", type="Consumer", raw_commands=["searing p 5"])],
]

gold_turn_page = [
  [Spell(rules_text="When you turn to this page, recharge a random spell.", color="gold", type="Passive",
         triggers_on=passive_on_page, raw_commands=["recharge r"]),
  Spell(rules_text="if this has 0 or less charges, gain 4 shield.", color="gold", type="Producer",
        generate_commands_post=if_spell_charges(0, ["shield p 4"], above=False)),
  Spell(rules_text="Deal 6 damage to immediate. Gain 1 empower for each missing spell charge on this page.", color="gold", type="Converter", conversion_color="red",
        raw_commands=["damage i 6"], generate_commands_post=for_missing_charges(["empower p *"])),
  Spell(rules_text="Gain Dig Deep 3. (Spells can go to -1 charge) Gain 3 shield.", color="gold", type="Consumer", raw_commands=["dig p 3", "shield p 3"])],
  #
  [Spell(rules_text="When you turn to this page, gain 1 inventive.", color="gold", type="Passive",
         triggers_on=passive_on_page, raw_commands=["inventive p 1"]),
  Spell(rules_text="refresh a spell.", color="gold", type="Producer"),
  Spell(rules_text="+4 time, +1 inventive, refresh and recharge last spell cast.", color="gold", type="Converter", conversion_color="red",
        raw_commands=["time -4", "inventive p 1", "recharge last"]),
  Spell(rules_text="Gain 2x shield and deal 2x to all where x is # of spells cast this turn.", color="gold", type="Consumer",
        generate_commands_pre=for_spells_cast(["shield p *", "damage a *"], lambda s: 2*s))], 
]

gold_1_spell = [
  [Spell(rules_text="If you cast 1 or less spell in a turn, gain 1 energy of any color.", color="gold", type="Passive",
         triggers_on=passive_1_spell_in_turn, raw_commands=[]), # TODO fix this
  Spell(rules_text="you may convert 1 energy to another color.", color="gold", type="Producer"),
  Spell(rules_text="Deal 4 damage twice. Gain 2 slow.", color="gold", type="Converter", conversion_color="red",
        raw_commands=["damage _ 4", "damage _ 4", "slow p 2"]), # NOTE: Green
  Spell(rules_text="Gain 3 inventive and 1 energy of any color.", color="gold", type="Consumer", raw_commands=["inventive p 3"])],
  #
  [Spell(rules_text="If you cast 1 or less spell in a turn, empower 6.", color="gold", type="Passive",
         triggers_on=passive_1_spell_in_turn, raw_commands=["empower p 6"]),
  Spell(rules_text="+1 time.", color="gold", type="Producer", raw_commands=["time -1"]),
  Spell(rules_text="Deal 6 damage to immediate. If this kills, recharge and refresh.", color="gold", type="Converter", conversion_color="red",
        targets=["i"], raw_commands=["damage i 6"], generate_commands_post=if_kill("i", ["recharge last"])),
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
  Spell(rules_text="Deal 10 damage to immediate. If this kills an enemy, empower 10.", color="gold", type="Consumer",
        targets=["i"], raw_commands=["damage i 10"], generate_commands_post=if_kill("i", ["empower p 10"]))],
]

gold_first_face = [
  [Spell(rules_text="The first time you face in a turn, gain 6 block.", color="gold", type="Passive",
          triggers_on=passive_first_face, raw_commands=["block p 6"]),
  Spell(rules_text="Stun 1 immediate behind.", color="gold", type="Producer", raw_commands=["stun bi 1"]),
  Spell(rules_text="Face, gain 2 shield for each enemy behind.", color="gold", type="Converter", conversion_color="blue",
        raw_commands=["face!"], generate_commands_post=for_enemies(["shield p *"], magnitude_func=lambda e: 2*e, specifier="behind")),
  Spell(rules_text="Stun faced side 1, face, deal 8 damage to immediate.", color="gold", type="Consumer",
        raw_commands=["stun iside 1", "face!", "damage i 8"])],
  #
  [Spell(rules_text="The first time you face in a turn, deal 6 damage to immediate.", color="gold", type="Passive",
          triggers_on=passive_first_face, raw_commands=["damage i 6"]),
  Spell(rules_text="inflict 3 vulnerable on immediate behind.", color="gold", type="Producer", raw_commands=["vulnerable bi 3"]),
  Spell(rules_text="Gain 2 sharp this turn, face, deal 4 to immediate.", color="gold", type="Converter", conversion_color="red",
        raw_commands=["sharp p 2", "delay 0 sharp p -2", "face!", "damage i 4"]),
  Spell(rules_text="Deal 6 damage to immediate. If facing no enemies, face and deal 16 damage to immediate.", color="gold", type="Consumer",
        raw_commands=["damage i 8"], generate_commands_post=if_facing_none(["face!", "damage i 16"]))]
]

gold_use_last_charge = [
  [Spell(rules_text="When you cast a spell's last charge, gain 4 shield.", color="gold", type="Passive",
         triggers_on=passive_use_last_charge, raw_commands=["shield p 4"]),
  Spell(rules_text="gain 1 inventive", color="gold", type="Producer", raw_commands=["inventive p 1"]),
  Spell(rules_text="Gain 1 evade, turn the page, +1 time.", color="gold", type="Converter", conversion_color="blue",
        raw_commands=["evade p 1", "page!", "time -1"]),
  Spell(rules_text="Deal 5 to a random enemy x times, where x is amount of energy.", color="gold", type="Consumer",
        generate_commands_pre=for_player_energy(["repeat * damage r 5"]))],
  #
  [Spell(rules_text="When you cast a spell's last charge, gain 3 searing presence.", color="gold", type="Passive",
          triggers_on=passive_use_last_charge, raw_commands=["searing p 3"]),
  Spell(rules_text="If this has 0 or less charges, damage immediate 8.", color="gold", type="Producer",
        generate_commands_post=if_spell_charges(0, ["damage i 8"], above=False)),
  Spell(rules_text="Gain 1 prolific, 2 dig deep, 3 block.", color="gold", type="Converter", conversion_color="red",
        raw_commands=["prolific p 1", "dig p 2", "block p 3"]),
  Spell(rules_text="Gain block and searing presence equal to missing charges on this page.", color="gold", type="Consumer",
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
