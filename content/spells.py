# Red Color Identity:
# - Straight big damage to facing side
# - full AOE
# - burn
# - self-damage
# * taking damage matters
# * getting kills matters
# * slaying big enemies (attack enemy with more max hp than your current hp?)
# * taking big hits (6+ damage in hit?)


red_enemy_dies = [
  ["Passive: Whenever an enemy dies, deal overkill damage + 4 to target behind.",
  "Producer: +1 Red, inflict 1 vulnerable",
  "Converter: 1 Red -> 1 Gold, Deal 9 damage. If this kills, +1 red.",
  "Consumer: 1 Red: Deal 16 damage"],
  #
  ["Passive: Whenever an enemy dies, inflict its burn +3 on its side.",
  "Producer: +1 Red, inflict 2 burn.",
  "Converter: 1 Red -> 1 Blue, Inflict 5 burn.",
  "Consumer: 1 Red: Inflict 2 burn, then inflict their burn on all enemies."],
]

red_take_damage = [
  ["Passive: Whenever you lose hp, gain 4 empowered.",
  "Producer: +1 Red, deal 2 damage. If this kills an enemy, recharge, refresh, +1 time.",
  "Converter: 1 Red -> 1 Gold: Gain 1 sharp for every missing 4 health.",
  "Consumer: 1 Red: 8 damage to all enemies on target side."],
  #
  ["Passive: Whenever you lose hp, inflict 2 burn on all enemies.",
  "Producer: +1 Red, when you take damage this turn, lose no life and gain half of it as burn.",
  "Converter: 1 Red -> 1 Gold: Double burn on an entity and you may transfer it to another entity.", # NOTE: Purple
  "Consumer: 1 Red: Inflict 3 burn. Tick all burn and gain life equal to damage dealt in this way."],
]

red_big_attack = [
  ["Passive: Gain 1 Red energy and recharge 1 random spell for every 7 damage you survive each round.",
  "Producer: +1 Red, If you're below half health, +1 more red.",
  "Converter: 1 Red -> 1 Gold: Deal 2 damage x times, where x is amount of energy you have.", # NOTE: Green
  "Consumer: 1 Red: Deal 11 damage. Then you may consume 1 energy of any type to recharge and refresh this."],
  #
  ["Passive: Gain 2 regen, deal 2 damage to all for every 7 damage you survive each round.",
  "Producer: +1 Red, If at full health, deal 6 damage, otherwise gain 1 regen.",
  "Converter: 1 Red -> 1 Gold: Suffer 3 damage, gain 3 sharp.",
  "Consumer: 1 Red: Deal 7 damage. Heal for unblocked."],
]

red_hit_big_enemy = [
  ["Passive: The 1st time you damage each enemy in a turn, inflict 5 burn if at least 10hp remains.",
  "Producer: +1 Red, Deal 4 damage to immediate.",
  "Converter: 1 Red -> 1 Blue: Apply 3 burn, then tick all conditions 2 times.", # NOTE: Purple
  "Consumer: 1 Red: Deal damage to an enemy equal to half target's remaining health."],
  #
  ["Passive: The 1st time you damage each enemy in a turn, gain 3 regen if at least 10hp remains.",
  "Producer: +1 Red, Deal 6 damage to a target at or above 10 health.",
  "Converter: 1 Red -> 1 Blue: Deal 6 damage. Stun 1 the target if it's at or above 10 health.",
  "Consumer: 1 Red: Deal damage equal to target's missing health."],
]

# red target access -- meteor strike, random hit target, hit any targets w/o facing

red_page_sets = [red_enemy_dies, red_take_damage, red_big_attack, red_hit_big_enemy]
red_pages = red_enemy_dies + red_take_damage + red_big_attack + red_hit_big_enemy
red_spells = sum(red_pages, [])

# Blue Color Identity
# - block
# - armor
# - ward
# - stun
# - durable
# - moving enemies?
# - defense + reactivity
# - charging up / stall
# - time delayed effects
# * Blocking damage matters
# * stall matters
# * overblocking matters?
# * pacifism matters? No kills at all?
# * outnumbered mattesr

blue_block_hits = [
  ["Passive: Whenever you’re attacked and take no damage, deal 4 damage to attacker.",
  "Producer: +1 Blue, gain 1 block per enemy.",
  "Converter: 1 Blue -> 1 Gold: Gain 9 block", # NOTE: Green
  "Consumer: 1 Blue: Gain 6 armor this turn."],
  #
  ["Passive: Whenever you’re attacked and take no damage, gain 2 retaliate.",
  "Producer: +1 Blue, gain 1 block and Break: deal 5 damage to attacker.",
  "Converter: 1 Blue -> 1 Gold: Block 5. Deal 4 damage.",
  "Consumer: 1 Blue: Block 4. Break: Deal 4 times the breaker’s attack damage back.",]
]

blue_turn_3 = [
  ["Passive: At beginning of 3rd turn and onwards, block 4.",
  "Producer: +1 Blue, Inflict 1 stun on an enemy that entered this turn.",
  "Converter: 1 Blue -> 1 Red: Stun 1 or deal 15 damage to a stunned enemy.", # NOTE: Purple
  "Consumer: 1 Blue: Inflict 3 stun."],
  #
  ["Passive: At beginning of 3rd turn and onwards, deal 3 damage to all enemies.",
  "Producer: +1 Blue, ward 1.",
  "Converter: 1 Blue -> 1 Red: At the end of next turn, all enemies take 6 damage.",
  "Consumer: 1 Blue: Ward 4."],
]

blue_3_enemies = [
  ["Passive: At the beginning of your turn if there are 3 or more enemies, stun 2 of them at random.",
  "Producer: +1 Blue, gain 1 block and Break: stun 1.",
  "Converter: 1 Blue -> 1 Gold: Gain retaliate 2.", # NOTE: Green
  "Consumer: 1 Blue: Deal 4 damage to all stunned enemies. Stun 1 all enemies."],
  #
  ["Passive: At the beginning of your turn, if there are 3 or more enemies, deal 15 damage to a random enemy.",
  "Producer: +1 Blue, deal 6 damage, call 1",
  "Converter: 1 Blue -> 1 Gold: Gain retaliate 6 this turn.", # NOTE: Purple
  "Consumer: 1 Blue: Gain 3 enduring this turn."],
]

blue_excess_block = [
  ["Passive: Excess block/shield at the end of your turn is dealt as damage to immediate.",
  "Producer: +1 Blue, Gain 3 block.",
  "Converter: 1 Blue -> 1 Red: Gain 1 armor and 1 retaliate.",
  "Consumer: 1 Blue: Gain 16 block."],
  #
  ["Passive: Excess block at the end of your turn becomes shield.",
  "Producer: +1 Blue, +1 shield.",
  "Converter: 1 Blue -> 1 Gold: Convert block into shield, or shield into 2x block.",
  "Consumer: 1 Blue: Deal damage equal to twice block+shield to target."],
]

blue_page_sets = [blue_block_hits, blue_turn_3, blue_3_enemies, blue_excess_block]
blue_pages = blue_block_hits + blue_turn_3 + blue_3_enemies + blue_excess_block
blue_spells = sum(blue_pages, [])

# Gold Color Identity:
# - buffs (regen, searing presence, empower, sharp)
# - rulebreaking
# * play slow matters? (when you cast 1 or less spell in a turn, get 1 blue energy)

# gold_spells = [
gold_3rd_spell = [
  ["Passive: Whenever you cast your 3rd spell in a turn, gain 3 sharp.",
  "Producer: +1 Gold, Deal 2 damage to each adjacent enemy.",
  "Converter: 1 Gold -> 1 Red: Deal 3 damage to immediate enemy. Repeat twice more.",
  "Consumer: 1 Gold: Cast a spell on this page twice, pay nothing. Unrechargeable."],
  #
  ["Passive: Whenever you cast your 3rd spell in a turn, gain 9 block.",
  "Producer: +1 Gold, gain 1 regen.",
  "Converter: 1 Gold -> 1 Blue: Recharge + refresh a spell on this page, +1 time ",
  "Consumer: 1 Gold: Gain 5 searing presence."],
]

gold_turn_page = [
  ["Passive: Every time you turn to this page, the next spell cast doesn’t cost charges or exhaust.",
  "Producer: +1 Gold, if this has 0 or less charges, gain 4 shield.",
  "Converter: 1 Gold -> 1 Red: Deal 6 damage to immediate. Gain 4 empower for every spell on this page with <= 0 charges.", # NOTE: Green
  "Consumer: 1 Gold: Gain Dig Deep 3. (Spells can go to -1 charge) Gain 3 shield."],
  #
  ["Passive: Every time you turn to this page, your next spell cast doesn’t cost energy.",
  "Producer: +1 Gold, refresh a spell.",
  "Converter: 1 Gold -> 1 Red: +4 time. Refresh all other spells on this page.", # NOTE: Green
  "Consumer: 1 Gold: Gain x shield and deal 2x to all where x is # of spells cast this turn."],
]

gold_1_spell = [
  ["Passive: If you cast 1 or less spell in a turn, gain 1 energy of any color.",
  "Producer: +1 Gold, you may convert 1 non-gold energy to gold.",
  "Converter: 1 Gold -> 1 Red: Green: 2 regen. Gold: 3 empower. Red: 3 damage. Blue: 3 shield. Purple: 2 poison.",
  "Consumer: 1 Gold: Gain 3 inventive and 1 energy of any color."],
  #
  ["Passive: If you cast 1 or less spell in a turn, empower 6.",
  "Producer: +1 Gold, +1 time.",
  "Converter: 1 Gold -> 1 Red: Deal 6 damage to immediate. If this kills, recharge and refresh.",
  "Consumer: 1 Gold: Gain 3 prolific."],
]

gold_face_noone = [
  ["Passive: At end of turn, if facing no enemies, gain 2 searing presence.",
  "Producer: +1 Gold, gain 2 searing presence.",
  "Converter: 1 Gold -> 1 Red: Banish 1 immediate enemy.", # NOTE: Purple
  "Consumer: 1 Gold: Gain 2 armor."],
  #
  ["Passive: At end of turn, if facing no enemies, gain 3 shield.",
  "Producer: +1 Gold, if facing no enemies, empower 5.",
  "Converter: 1 Gold -> 1 Blue: Gain 5 shield.",
  "Consumer: 1 Gold: Deal 10 damage to immediate. If this kills an enemy, empower 10."],
]

gold_page_sets = [gold_3rd_spell, gold_turn_page, gold_1_spell, gold_face_noone]
gold_pages = gold_3rd_spell + gold_turn_page + gold_1_spell + gold_face_noone
gold_spells = sum(gold_pages, [])


# Green Color Identity:
# - energy matters
# - building up recurring/passive effects
# - facing mechanics?
# * stay on same page matters?
# * strong effect on first 2 turns?

spells = red_spells + blue_spells + gold_spells