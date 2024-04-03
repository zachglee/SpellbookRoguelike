from model.item import Item

red_potion = Item.make("Red Potion", 1, "Gain 1 Red", ["red p 1"], weight=0.5)
blue_potion = Item.make("Blue Potion", 1, "Gain 1 Blue", ["blue p 1"], weight=0.5)
gold_potion = Item.make("Gold Potion", 1, "Gain 1 gold", ["gold p 1"], weight=0.5)
# green_potion = Item.make("Green Potion", 1, "Gain 1 green", ["green p 1"], weight=0.5)
# purple_potion = Item.make("Purple Potion", 1, "Gain 1 purple", ["purple p 1"], weight=0.5)

minor_health_potion = Item.make("Minor Health Potion", 1, "Heal 5", ["heal p 5"], material_cost=8)
middling_health_potion = Item.make("Middling Health Potion", 2, "Heal 4", ["heal p 4"], material_cost=12)
major_health_potion = Item.make("Major Health Potion", 5, "Heal 3", ["heal p 3"], material_cost=18)
health_potions = [minor_health_potion, middling_health_potion, major_health_potion]

ancient_key = Item.make("Ancient Key", 1, "A key to a door long forgotten.", [], weight=0, rare=True, craftable=False)

minor_energy_potions = [red_potion, blue_potion, gold_potion]
minor_energy_potions_dict = {"red": red_potion, "blue": blue_potion, "gold": gold_potion}

rusty_sword = Item.make("Rusty Sword", 3, "Deal 3 damage", ["damage i 3"])
battered_shield = Item.make("Battered Shield", 3, "Block 4", ["block p 4"])

starting_weapons = [rusty_sword, battered_shield]
