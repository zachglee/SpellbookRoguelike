from model.rest_site import RestAction

def condition_effect_factory(condition, magnitude):
  def condition_factory(gs):
    gs.player.conditions[condition] += magnitude
  return condition_factory

def heal_effect_factory(hp):
  def heal_effect(gs):
    gs.player.hp += hp
  return heal_effect

def reroll_effect_factory(rerolls):
  def reroll_effect(gs):
    gs.player.rerolls += rerolls
  return reroll_effect

heal = RestAction({"Red Essence": 3}, heal_effect_factory(10), "Heals for 6.")
sharp = RestAction({"Red Essence": 3}, condition_effect_factory("sharp", 2), "Gain 1 sharp.")
armor = RestAction({"Blue Essence": 4}, condition_effect_factory("armor", 1), "Gain 1 armor.")
ward = RestAction({"Blue Essence": 3}, condition_effect_factory("ward", 2), "Gain 2 ward.")
searing = RestAction({"Gold Essence": 3}, condition_effect_factory("searing", 2), "Gain 1 searing.")
prolific = RestAction({"Gold Essence": 3}, condition_effect_factory("prolific", 2), "Gain 2 prolific.")

# energies

red_energy = RestAction({"Red Essence": 2}, condition_effect_factory("red", 1), "Gain 1 red energy.")
blue_energy = RestAction({"Blue Essence": 2}, condition_effect_factory("blue", 1), "Gain 1 blue energy.")
gold_energy = RestAction({"Gold Essence": 2}, condition_effect_factory("gold", 1), "Gain 1 gold energy.")

rerolls = RestAction({"Bounties": 3}, reroll_effect_factory(1), "Gain 1 rerolls.")

rest_actions = [
  heal,
  sharp,
  armor,
  ward,
  searing,
  prolific,
  red_energy,
  blue_energy,
  gold_energy,
]