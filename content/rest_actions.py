from model.rest_site import RestAction

def condition_effect_factory(condition, magnitude):
  def condition_factory(gs):
    gs.player.conditions[condition] += magnitude
  return condition_factory

def heal_effect_factory(hp):
  def heal_effect(gs):
    gs.player.hp += hp

heal = RestAction({"red": 3}, heal_effect_factory(10), "Heals for 6.")
sharp = RestAction({"red": 3}, condition_effect_factory("sharp", 2), "Gain 2 sharp.")
armor = RestAction({"blue": 3}, condition_effect_factory("armor", 1), "Gain 1 armor.")
ward = RestAction({"blue": 3}, condition_effect_factory("ward", 2), "Gain 2 ward.")
searing = RestAction({"gold": 3}, condition_effect_factory("searing", 2), "Gain 2 searing.")
prolific = RestAction({"gold": 3}, condition_effect_factory("prolific", 2), "Gain 2 prolific.")

# energies

red_energy = RestAction({"red": 2}, condition_effect_factory("red", 1), "Gain 1 red energy.")
blue_energy = RestAction({"blue": 2}, condition_effect_factory("blue", 1), "Gain 1 blue energy.")
gold_energy = RestAction({"gold": 2}, condition_effect_factory("gold", 1), "Gain 1 gold energy.")

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