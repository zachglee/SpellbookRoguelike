from model.item import CustomItem

red_potion = CustomItem("Red Potion", 1, "Gain 1 Red", ["red p 1"])
blue_potion = CustomItem("Blue Potion", 1, "Gain 1 Blue", ["blue p 1"])
gold_potion = CustomItem("gold Potion", 1, "Gain 1 gold", ["gold p 1"])

minor_energy_potions = [red_potion, blue_potion, gold_potion]

rusty_sword = CustomItem("Rusty Sword", 3, "Deal 3 damage", ["damage i 3"])
battered_shield = CustomItem("Battered Shield", 3, "Block 4", ["block p 4"])

starting_weapons = [rusty_sword, battered_shield]
