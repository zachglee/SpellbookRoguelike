from model.item import (EnergyPotion, MeleeWeapon, SpellPotion,
                        ConditionMeleeWeapon, ConditionSelfWeapon)

rusty_sword = MeleeWeapon("Rusty Sword", 3, 3)
trusty_torch = ConditionMeleeWeapon("Trusty Torch", 3, "burn", 2)
battered_shield = ConditionSelfWeapon("Battered Shield", 3, "block", 4)
protection_charm = ConditionSelfWeapon("Protection Charm", 4, "ward", 1)

starting_weapons = [rusty_sword, trusty_torch, battered_shield, protection_charm]