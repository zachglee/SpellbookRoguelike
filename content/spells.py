# Red Color Identity:
# - Straight big damage to facing side
# - full AOE
# - burn
# - self-damage
# * taking damage matters
# * getting kills matters
# * slaying big enemies (attack enemy with more max hp than your current hp?)
# * taking big hits (6+ damage in hit?)


red_spells = [
  "Passive: Whenever an enemy dies, deal overkill damage + 4 to target behind.",
  "Producer: +1 Red, inflict 1 vulnerable",
  "Converter: 1 Red -> 1 Green, Deal 9 damage",
  "Consumer: 1 Red: Deal 16 damage",
  #
  "Passive: Whenever an enemy dies, inflict its burn +2 on adjacent.",
  "Producer: +1 Red, inflict 2 burn.",
  "Converter: 1 Red -> 1 Blue, Inflict 5 burn.",
  "Consumer: 1 Red: Inflict 2 burn, then inflict their burn on all enemies.",
  #
  "Passive: Whenever you take damage, gain 3 empowered.",
  "Producer: +1 Red, deal 1 damage. Does not consume on ‘next attack’ effects.",
  "Converter: 1 Red -> 1 Gold: When you are attacked this turn, gain life lost as empower, and regen 1.",
  "Consumer: 1 Red: 6 damage to all enemies on target side.",
  #
  "Passive: Whenever you take damage, inflict 2 burn on adjacent enemies.",
  "Producer: +1 Red, All damage to you is halved this turn. Take all damage as burn.",
  # "Converter: 1 Red -> 1 Purple: Transfer all negative status effects from you to target enemy.",
  "Consumer: 1 Red: Inflict 3 burn. Tick all burn and gain life equal to damage dealt in this way. ",
  #
  "Passive: When you take 6+ damage in a hit, gain 1 Red energy and recharge 1 random spell on this page.",
  "Producer: +1 Red, If you're below half health, +2 instead.",
  "Converter: 1 Red -> 1 Green: Deal 2 damage x times, where x is amount of energy you have.",
  "Consumer: 1 Red: Deal 11 damage. Then you may consume 1 energy of any type to recharge and refresh this.",
  #
  "Passive: When you take 6+ damage in a hit, gain 3 regen.",
  "Producer: +1 Red, If at full health, deal 5 damage, otherwise gain 1 regen.",
  "Converter: 1 Red -> 1 Gold: Deal self 3 damage, gain 3 sharp.",
  "Consumer: 1 Red: Deal 6 damage. Heal for unblocked.",
  #
  "Passive: The first time you damage an enemy, inflict 1 burn for every 6 max hp.",
  "Producer: +1 Red, Deal 4 damage to immediate.",
  "Converter: 1 Red -> 1 Purple: Apply 3 burn, then tick all conditions 3 times."
  "Consumer: 1 Red: Deal damage to an enemy equal to half target's remaining health.",
  #
  "Passive: The first time you damage an enemy, gain 1 regen for every 6 max hp",
  "Producer: +1 Red, Deal 4 damage to a target at or above 10 health.",
  "Converter: 1 Red -> 1 Blue: Deal 6 damage. Stun the target if it's at or below half health.",
  "Consumer: 1 Red: Deal damage equal to target's missing health.",
]

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

blue_spells = [
  "Passive: Whenever you’re attacked and take no damage, deal 4 damage to attacker.",
  "Producer: +1 Blue, gain 1 block per enemy.",
  "Converter: 1 Blue -> 1 Green: Gain 7 block",
  "Consumer: 1 Blue: Gain 4 armor this turn.",
  #
  "Passive: Whenever you’re attacked and take no damage, gain 4 empowered.",
  "Producer: +1 Blue, gain 1 block and Break: gain 3 empowered.",
  "Converter: 1 Blue -> 1 Gold: Block 4. Deal 4 damage.",
  "Consumer: 1 Blue: Block 5. Break: Deal twice breaker’s attack damage back.",
  #
  "Passive: At beginning of 3rd turn and onwards, block 4.",
  "Producer: +1 Blue, Inflict 1 stun on an enemy that entered this turn.",
  # "Converter: 1 Blue -> 1 Purple: Inflict doom 2.",
  "Consumer: 1 Blue: Inflict 3 stun.",
  #
  "Passive: At beginning of 3rd turn and onwards, deal 3 damage to all enemies.",
  "Producer: +1 Blue, ward 1.",
  "Converter: 1 Blue -> 1 Red: At the end of next turn, all enemies take 8 damage.",
  "Consumer: 1 Blue: Ward 4.",
  #
  "Passive: At the beginning of your turn if there are 4 or more enemies, stun 1 at random.",
  "Producer: +1 Blue, gain 1 block and Break: stun 1.",
  "Converter: 1 Blue -> 1 Green: Stun 1 or deal 12 damage to a stunned enemy.",
  "Consumer: 1 Blue: Stun all damaged enemies.",
  #
  "Passive: At the beginning of your turn, if there are 4 or more enemies, deal 12 damage to a random enemy.",
  "Producer: +1 Blue, deal 7 damage, call 1",
  "Converter: 1 Blue -> 1 Purple: Inflict 2 poison on 4 random different enemies.",
  "Consumer: 1 Blue: Gain durable 4 this turn.",
  #
  "Passive: Excess block at the end of your turn is dealt as damage to immediate.",
  "Producer: +1 Blue, Gain 3 block.",
  "Converter: 1 Blue -> 1 Red: Gain 1 armor and 1 sharp.",
  "Consumer: 1 Blue: Gain 12 block.",
  #
  "Passive: Excess block at the end of your turn is not lost.",
  "Producer: +1 Blue, +1 block. If you have 6 or more block, gain break: deal 6 damage to breaker.",
  "Converter: 1 Blue -> 1 Gold: Block 3. Convert all block into healing.",
  "Consumer: 1 Blue: Deal damage equal to block to target.", # TODO rework
]

# Gold Color Identity:
# - buffs (regen, searing presence, empower, sharp)
# - rulebreaking
# * play slow matters? (when you cast 1 or less spell in a turn, get 1 blue energy)

gold_spells = [
  "Passive: Whenever you cast your 3rd spell in a turn, gain 2 sharp.",
  "Producer: +1 Gold, Deal 2 damage to each adjacent enemy.",
  "Converter: 1 Gold -> 1 Red: Deal 3 damage 3 times to immediate enemy.",
  "Consumer: 1 Gold: Gain 3 empower. Cast a spell on this page twice, only pay charges.",
  #
  "Passive: Whenever you cast your 3rd spell in a turn, gain 9 block.",
  "Producer: +1 Gold, gain 2 regen.",
  "Converter: 1 Gold -> 1 Blue: Recharge a spell on this page ",
  "Consumer: 1 Gold: Gain 5 searing presence.",
  #
  "Passive: Every time you turn to this page, the next spell cast doesn’t cost charges or exhaust.",
  "Producer: +1 Gold, if this has 0 or less charges, gain 4 block.",
  "Converter: 1 Gold -> 1 Green: Deal 6 damage to immediate. Gain 3 empower for every spell on this page with 0 or less charges.",
  "Consumer: 1 Gold: Gain Dig Deep 4. (Spells can go to -1 charge) Gain 4 block.",
  #
  "Passive: Every time you turn to this page, your next spell cast doesn’t cost energy.",
  "Producer: +1 Gold, refresh a spell.",
  "Converter: 1 Gold -> 1 Green: Cast a spell from another page of your spell book without paying its energy cost. Gain 2 regen.",
  "Consumer: 1 Gold: Gain x block and x regen where x is the number of spells cast this turn. (not counting this)",
  #
  "Passive: When you cast 1 or less spell in a turn, gain 1 gold energy.",
  "Producer: +1 Gold, you may convert 1 non-gold energy to gold.",
  "Converter: 1 Gold -> 1 Green: Gain 1 energy of each kind you do not have.",
  "Consumer: 1 Gold: Gain 3 inventive.",
  #
  "Passive: When you cast 1 or less spell in a turn, recharge a spell on this page.",
  "Producer: +1 Gold, +1 time.",
  "Converter: 1 Gold -> 1 Red: Gain 4 fleeting sharp.",
  "Consumer: 1 Gold: Gain 3 prolific.",
  #
  "Passive: At end of turn, if facing no enemies, gain 1 searing presence.",
  "Producer: +1 Gold, gain 1 searing presence.",
  "Converter: 1 Gold -> 1 Purple: Banish 1 immediate enemy.",
  "Consumer: 1 Gold: Gain 2 armor.",
  #
  "Passive: At end of turn, if facing no enemies, gain 3 shield.",
  "Producer: +1 Gold, if facing no enemies, empower 5.",
  "Converter: 1 Gold -> 1 Blue: Gain 5 shield.",
  "Consumer: 1 Gold: Deal 10 damage to immediate. If this kills an enemy, empower 10.",
]

# Green Color Identity:
# - energy matters
# - building up recurring/passive effects
# - facing mechanics?
# * stay on same page matters?
# * strong effect on first 2 turns?


spells = red_spells + blue_spells + gold_spells