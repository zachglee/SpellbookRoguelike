# from model.encounter import EnemySet, Enemy, EnemySpawn
from model.item import CustomItem
from model.faction import Faction
from content.enemies import *
from content.command_generators import *

factions = [
  Faction("Sa'ik Collective", saik_collective,
    basic_items=[
      CustomItem("Soaring Javelin", 1, "Deal 6 damage.", ["damage _ 6"]),
      CustomItem("Harrier's Cloak", 2, "Gain 1 evade.", ["evade p 1"]),
    ],
    special_items=[
      CustomItem("Skydancer's Talon", 3, "Deal 2 damage to a single target twice.", ["repeat 2 damage _ 2"], rare=True)
    ],
  ),
  Faction("House of Imir", house_of_imir,
    basic_items=[
      CustomItem("Thirsting Blade", 2, "Lifesteal 2 from immediate", ["lifesteal i 2"]),
      CustomItem("Sacrifice Dagger", 2, "Suffer 2 and deal 10 damage to immediate", ["suffer p 2", "damage i 10"]),
    ],
    special_items=[
      CustomItem("Imir Blood Ward", 1, "Suffer 5 and banish an enemy for 2 turns.", ["suffer p 5", "banish _ 2"], rare=True,)
    ]
  ),
  Faction("Mov's Horde", movs_horde,
    basic_items=[
      CustomItem("Reaper's Scythe", 2, "Deal 3 damage to immediate two enemies.", ["damage i1 3", "damage i2 3"]),
      CustomItem("Ichor of Undeath", 1, "Gain 4 enduring this turn.", ["enduring p 4", "delay 0 enduring p -4"]),
    ],
    special_items=[
      CustomItem("Soul-Catcher Siphon", 1, "", [], generate_commands_pre=for_dead_enemies(["regen p *"]), rare=True) # effect per dead enemies
    ]
  ),
  Faction("Company of Blades", company_of_blades,
    basic_items=[
      CustomItem("Trusty Sword", 6, "Deal 2 damage to immediate.", ["damage i 2"]),
      CustomItem("Battered Shield", 3, "Block 4.", ["block p 4"]),
    ],
    special_items=[
      CustomItem("Duelist's Blade", 3, "Deal 4 damage to immediate and block 4", ["damage i 4", "block p 4"], rare=True)
    ]
  ),
  Faction("Giantkin", giantkin,
    basic_items=[
      CustomItem("Giant's Club", 3, "Deal 10 damage to immediate.", ["damage i 10"], time_cost=3),
      CustomItem("Potion of Strength", 3, "Gain 3 empower.", ["empower p 3"])
    ],
    special_items=[
      CustomItem("Ogre's Brew", 1, "Gain 3 armor and 9 empower.", ["armor p 3", "empower p 9"], rare=True)
    ],
  ),
  Faction("Fae Realm", fae_realm,
    basic_items=[
      CustomItem("Luring Flute", 1, "Heal immediate 3 and banish it 1.", ["heal i 3", "banish i 1"]),
      CustomItem("Sleeper Darts", 2, "Inflict 1 stun and 3 poison.", ["stun _ 1", "poison _ 3"])
    ],
    special_items=[
      CustomItem("Fae Favor", 1, "Banish 1 all at end of round, then gain 3 regen.", ["delay 0 banish a 1", "delay 0 regen p 3"], rare=True)
    ]
  ),
  Faction("Kingdom of Amar", kingdom_of_amar,
    basic_items=[
      CustomItem("Knifewing Set", 2, "Deal 1 damage to immediate thrice.", ["repeat 3 damage i 1"]),
      CustomItem("Animate Armor", 2, "Gain 1 armor.", ["armor p 1"]),
    ],
    special_items=[
      CustomItem("Amarian Warsuit", 1, "Gain 2 armor, 3 prolific, and 4 sharp.", ["armor p 2", "prolific p 3", "sharp p 4"], rare=True)
    ]
  ),
  Faction("Infernal Plane", infernal_plane,
    basic_items=[
      CustomItem("Hellfire Torch", 3, "Burn 2 immediate.", ["burn i 2"]),
      CustomItem("Summoning Circle", 4, "Gain 1 regen and call 1.", ["regen p 1", "call 1"])
    ],
    special_items=[
      CustomItem("Demon's Blood", 1, "burn 3 self, gain 9 searing presence, 9 retaliate", ["burn p 3", "searing p 8", "retaliate p 8"], rare=True)
    ]
  ),
  Faction("Dominion of Drael", dominion_of_drael,
    basic_items=[
      CustomItem("Captain's Warhorn", 1, "Block 5, Empower 5", ["block p 5", "empower p 5"]),
      CustomItem("Shieldmage's Gauntlets", 2, "Gain 3 shield and 2 retaliate.", ["shield p 3", "retaliate p 2"]),
    ],
    special_items=[
      CustomItem("Draelish Bomb", 1, "At end of turn: deal 21 to all enemies, 7 damage to self", ["delay 0 damage a 21", "delay 0 damage p 7"], rare=True)
    ]
  ),
  Faction("Spirits", spirits,
    basic_items=[
      CustomItem("Spirit's Blessing", 1, "Gain 2 prolific.", ["prolific p 2"]),
      CustomItem("Spirit Snare", 2, "At end of next round, stun 3 immediate.", ["delay 1 stun i 3"]),
    ],
    special_items=[
      CustomItem("Unbridled Energy", 1, "Gain 2 energy of each color and prolific 2.", ["blue p 2", "red p 2", "gold p 2", "prolific p 2"], rare=True)
    ]
  ),
  Faction("Shadow Realm", shadow_realm,
    basic_items=[
      CustomItem("Brave Face", 2, "Face, then block 5.", ["face", "block p 5"]),
      CustomItem("Mirror Blade", 1, "Deal 6 damage immediately behind.", ["damage bi 6"])
    ],
    special_items=[
      CustomItem("Voodoo Doll", 3, "Any target suffers 4 damage.", ["suffer _ 4"], rare=True)
    ]
  ),
  Faction("Ancient Horrors", ancient_horrors,
    basic_items=[
      CustomItem("Damaged Ward", 4, "Gain 1 ward.", ["ward p 1"]),
      CustomItem("Forbidden Text", 4, "Gain 1 inventive.", ["inventive p 1"]),
    ],
    special_items=[
      CustomItem("Prayer to the Ancients", 3, "10 damage to random.", ["damage r 10"], rare=True)
    ]
  )
]

all_special_items = sum([faction.special_items for faction in factions], [])