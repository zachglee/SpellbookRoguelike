from model.item import CustomItem

red_potion = CustomItem("Red Potion", 1, "Gain 1 Red", ["red p 1"])
blue_potion = CustomItem("Blue Potion", 1, "Gain 1 Blue", ["blue p 1"])
gold_potion = CustomItem("Gold Potion", 1, "Gain 1 gold", ["gold p 1"])

minor_health_potion = CustomItem("Minor Health Potion", 1, "Heal 5", ["heal p 5"], material_cost=8)
middling_health_potion = CustomItem("Middling Health Potion", 2, "Heal 4", ["heal p 4"], material_cost=12)
major_health_potion = CustomItem("Major Health Potion", 5, "Heal 3", ["heal p 3"], material_cost=18)
health_potions = [minor_health_potion, middling_health_potion, major_health_potion]

minor_energy_potions = [red_potion, blue_potion, gold_potion]
minor_energy_potions_dict = {"red": red_potion, "blue": blue_potion, "gold": gold_potion}

rusty_sword = CustomItem("Rusty Sword", 3, "Deal 3 damage", ["damage i 3"])
battered_shield = CustomItem("Battered Shield", 3, "Block 4", ["block p 4"])

starting_weapons = [rusty_sword, battered_shield]
