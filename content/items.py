from model.item import (EnergyPotion, MeleeWeapon, SpellPotion,
                        ConditionMeleeWeapon, ConditionSelfWeapon, CustomItem)

red_potion = EnergyPotion("red", 1)
blue_potion = EnergyPotion("blue", 1)
gold_potion = EnergyPotion("gold", 1)

minor_energy_potions = [red_potion, blue_potion, gold_potion]

rusty_sword = MeleeWeapon("Rusty Sword", 3, 3)
battered_shield = ConditionSelfWeapon("Battered Shield", 3, "block", 4)

starting_weapons = [rusty_sword, battered_shield]

# signature items (these are powerful items you get at level 9. Powerful mainly because they're as needed.)
the_bomb = CustomItem("The Bomb", 1, "At end of turn: deal 21 to all enemies, 7 damage to self", ["delay 0 damage a 21", "delay 0 damage p 7"])
ignited_ichor = CustomItem("Ignited Ichor", 1, "burn 4 self, gain 8 block, 8 searing presence, 8 retaliate", ["burn p 4", "block p 8", "searing p 8", "retaliate p 8"])
poison_darts = CustomItem("Poison Darts", 2, "inflict 2 stun and 4 poison", ["stun _ 2", "poison _ 4"])
seekers_bow = CustomItem("Seeker's Bow", 3, "deal 4 to any target", ["damage _ 4"])
lightning_rod = CustomItem("Lightning Rod", 3, "deal 10 to random", ["damage r 10"])
elixir_of_life = CustomItem("Elixir of Life", 6, "gain 1 regen", ["regen p 1"])

# TODO rework the level 9 signature item now that I have faction-based items
signature_items = [the_bomb, ignited_ichor, poison_darts, seekers_bow, lightning_rod, elixir_of_life]