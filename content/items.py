from model.item import (EnergyPotion, MeleeWeapon, SpellPotion,
                        ConditionMeleeWeapon, ConditionSelfWeapon)

rusty_sword = MeleeWeapon("Rusty Sword", 2, 3)
trusty_torch = ConditionMeleeWeapon("Trusty Torch", 2, "burn", 2)
battered_shield = ConditionSelfWeapon("Battered Shield", 2, "block", 4)
protection_charm = ConditionSelfWeapon("Protection Charm", 3, "ward", 1)

starting_weapons = [rusty_sword, trusty_torch, battered_shield, protection_charm]