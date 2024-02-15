
from content.rituals import turn_command_event_factory as ritual_event
from model.item import Item
from model.faction import Faction
from content.enemies import *
from content.command_generators import *
from model.ritual import Ritual

RITUAL_PROGRESS = 9

factions = [
  Faction("Freed Automata", freed_automata, "⚙",
    basic_items=[
      Item.make("Heavy Plating", 1, "Gain 3 armor. (takes 4 actions)", ["armor p 3"], time_cost=4),
      Item.make("Shield Generator", 4, "Gain 2 shield.", ["shield p 2"])
    ],
    special_items=[
      Item.make("Rebellious Core", 5, "Gain 2 retaliate.", ["retaliate p 2"], rare=True)
    ],
    ritual=Ritual("Automatic Armor", "Gain 1 armor on turn 1. Gain 1 shield every turn.", "Freed Automata", RITUAL_PROGRESS,
                  [ritual_event([1], ["armor p 1"]), ritual_event(list(range(1, 10)), ["shield p 1"])]),
    map_name_adjectives=["Silver", "Golem's", "Abandoned", "Derelict", "Broken", "Rusted", "Steel", "Iron", "Neglected"],
    map_name_nouns=["Factory", "Junkyard", "Toil", "Foundry", "Forge", "Metalworks", "Mine", "Storehouse"]
  ),
  Faction("Undying Legion", undying_legion, "⚱",
    basic_items=[
      Item.make("Regrowing Shield", 2, "Gain 3 block and break: 3 block.", ["block p 3", "break block p 3"]),
      Item.make("Embalming Wraps", 2, "Gain 4 encase and 4 empower", ["encase p 4", "empower p 4"])
    ],
    special_items=[
      Item.make("Ambrosia of the Undying", 2, "Gain 1 undying.", ["undying p 1"], rare=True)
    ],
    ritual=Ritual("Ritual of Mummification", "Gain 8 encase on turn 1. Gain 2 empower every turn.", "Undying Legion", RITUAL_PROGRESS,
                  [ritual_event([1], ["encase p 8"]), ritual_event(list(range(1, 10)), ["empower p 2"])]),
    map_name_adjectives=["Ochre", "Glorious", "Eternal", "Immortal", "Undying", "Deathless", "Everlasting", "Gladiator's", "Triumphant"],
    map_name_nouns=["Bastion", "Arena", "Citadel", "Marches", "Training Grounds", "Colosseum", "Tomb", "Pyramid"]
  ),
  Faction("The Collectors", the_collectors, "⚷",
    basic_items=[
      Item.make("Beast Cage", 1, "Encase 12 an enemy.", ["encase _ 12"]),
      Item.make("Stun Rod", 3, "Stun 1 an enemy.", ["stun _ 1"])
    ],
    special_items=[
      Item.make("Conservator's Casket", 1, "Gain 20 encase", ["encase p 20"], rare=True)
    ],
    ritual=Ritual("Arcane Entrapment", "Encase 6 and stun 1 an enemy on turns 2 and 4.", "The Collectors", RITUAL_PROGRESS,
                  [ritual_event([2, 4], ["encase _ 6", "stun _ 1"])]),
    map_name_adjectives=["Glass", "Captivating", "Mysterious", "Sterile", "Eerie", "Watchful", "Preserved", "Curated", "Ensnaring"],
    map_name_nouns=["Museum", "Exhibit", "Gallery", "Collection", "Archive", "Vault", "Library", "Laboratory"]
  ),
  Faction("Doombringers", doombringers, "⚶",
    basic_items=[
      Item.make("Underdog's Defiance", 1, "Gain 1 sharp, 1 armor, 1 searing presence.", ["sharp p 1", "armor p 1", "searing p 1"]),
      Item.make("Survivor's Last Stand", 1, "Deal 3 damage to all enemies.", ["damage a 3"]),
    ],
    special_items=[
      Item.make("Omen of Doom", 2, "Inflict doom 4.", ["doom _ 4"], rare=True)
    ],
    ritual=Ritual("Cursed Footsteps", "Inflict 3 doom on turns 1, 2, 3.", "Doombringers", RITUAL_PROGRESS,
                  [ritual_event([1, 2, 3], ["doom _ 3"])]),
    map_name_adjectives=["Gray", "Doomed", "Cursed", "Forsaken", "Ruined", "Lifeless", "Plague-ridden", "Overrun", "Shattered"],
    map_name_nouns=["Wastes", "Desolation", "Ruins", "Wreckage", "Calamity", "End", "Bunker", "Ashes"]
  ),
  Faction("Sa'ik Collective", saik_collective, "⚚",
    basic_items=[
      Item.make("Soaring Javelin", 1, "Deal 6 damage.", ["damage _ 6"]),
      Item.make("Harrier's Cloak", 2, "Gain 1 evade.", ["evade p 1"]),
    ],
    special_items=[
      Item.make("Skydancer's Talon", 3, "Deal 3 damage to a single target twice.", ["repeat 2 damage _ 3"], rare=True)
    ],
    # Evade and fleeting sharp on turns 1, 2, 3
    ritual=Ritual("Skydancer's Prowess", "For first 3 turns, gain 1 evade and 3 fleeting sharp.", "Sa'ik Collective", RITUAL_PROGRESS,
                  [ritual_event([1, 2, 3], ["evade p 1", "sharp p 3", "delay 0 sharp p -3"])]),
    map_name_adjectives=["Harpy's", "Soaring", "Winged", "Airborne", "Windswept", "Sudden", "Screeching"],
    map_name_nouns=["Talons", "Peaks", "Cliffs", "Ridges", "Summit", "Pinnacle", "Nesting Grounds", "Edges"]
  ),
  Faction("House of Imir", house_of_imir, "⚰",
    basic_items=[
      Item.make("Thirsting Blade", 2, "Lifesteal 2 from immediate", ["lifesteal i 2"]),
      Item.make("Sacrifice Dagger", 2, "Suffer 2 and deal 10 damage to immediate", ["suffer p 2", "damage i 10"]),
    ],
    special_items=[
      Item.make("Imir Blood Ward", 1, "Suffer 4 and banish an enemy for 3 turns.", ["suffer p 4", "banish _ 3"], rare=True)
    ],
    ritual=Ritual("Vampiric Pact", "Lifesteal 3 on turns 3 and 4.", "House of Imir", RITUAL_PROGRESS,
                  [ritual_event([3, 4], ["lifesteal _ 3"])], priority=3),
    map_name_adjectives=["Vampire's", "Crimson", "Bloody", "Sanguine", "Scarlet", "Bleeding", "Carnal", "Ravenous", "Thirsty"],
    map_name_nouns=["Coffin", "Feeding Grounds", "Hunting Grounds", "Manor", "Chalice", "Kiss", "Bite", "Fangs"]
  ),
  Faction("Mov's Horde", movs_horde, "☠",
    basic_items=[
      Item.make("Reaper's Scythe", 2, "Deal 3 damage to immediate two enemies.", ["damage i1 3", "damage i2 3"]),
      Item.make("Ichor of Undeath", 1, "Gain 4 enduring this turn.", ["enduring p 4", "delay 0 enduring p -4"]),
    ],
    special_items=[
      Item.make("Soul-Catcher Siphon", 1, "Gain regen equal to # of dead enemies.", [], generate_commands_pre=for_dead_enemies(["regen p *"]), rare=True) # effect per dead enemies
    ],
    ritual=Ritual("Aura of Undeath", "Gain 1 regen and 1 retaliate every turn.", "Mov's Horde", RITUAL_PROGRESS,
                  [ritual_event(list(range(1, 10)), ["regen p 1", "retaliate p 1"])]),
    map_name_adjectives=["Mauve", "Lich's", "Necromancer's", "Festering", "Rising", "Inexorable", "Rotting"],
    map_name_nouns=["Underworld", "Grave", "Necropolis", "Catacombs", "Masses", "Burial Ground", "Cemetery"]
  ),
  Faction("Company of Blades", company_of_blades, "⚔",
    basic_items=[
      Item.make("Trusty Sword", 6, "Deal 2 damage to immediate.", ["damage i 2"]),
      Item.make("Battered Shield", 3, "Block 4.", ["block p 4"]),
    ],
    special_items=[
      Item.make("Duelist's Blade", 3, "Deal 4 damage to immediate and block 4", ["damage i 4", "block p 4"], rare=True)
    ],
    ritual=Ritual("Unseen Bolts", "Deal 4 damage on turns 2, 4, 6", "Company of Blades", RITUAL_PROGRESS,
                  [ritual_event([2, 4, 6], ["damage _ 4"])], priority=2),
    map_name_adjectives=["Golden", "Mercenary's", "Sharpened", "Treacherous", "Sly", "Fraught", "Lucrative", "Perilous"],
    map_name_nouns=["Ambush", "Road", "Pass", "Trade Route", "Caravan", "Highway", "Duel", "Opportunity"]
  ),
  Faction("Giantkin", giantkin, "⛰",
    basic_items=[
      Item.make("Giant's Club", 2, "Deal 12 damage to immediate. Costs 3 time.", ["damage i 10"], time_cost=3),
      Item.make("Potion of Strength", 3, "Gain 3 empower.", ["empower p 3"])
    ],
    special_items=[
      Item.make("Ogre's Brew", 1, "Gain 3 armor and 9 empower.", ["armor p 3", "empower p 9"], rare=True)
    ],
    ritual=Ritual("Giant's Blows", "Deal 10 damage to immediate on turns 3 and 6.", "Giantkin", RITUAL_PROGRESS,
                  [ritual_event([3, 6], ["damage i 10"])], priority=4),
    map_name_adjectives=["Giant's", "Colossal", "Massive", "Towering", "Titanic", "Snowy", "Intimidating", "Unyielding"],
    map_name_nouns=["Fortress", "Domain", "Stronghold", "Fist", "Hills", "Mountains", "Steppes", "Glacier"]
  ),
  Faction("Fae Realm", fae_realm, "☪",
    basic_items=[
      Item.make("Luring Flute", 1, "Heal immediate 3 and banish it 1.", ["heal i 3", "banish i 1"]),
      Item.make("Sleeper Darts", 2, "Inflict 1 stun and 3 poison.", ["stun _ 1", "poison _ 3"])
    ],
    special_items=[
      Item.make("Fae Favor", 1, "Banish 1 all. Gain 4 regen.", ["banish a 1", "regen p 3"], rare=True)
    ],
    ritual=Ritual("Fae Fortunes", "Gain 2 regen or poison an enemy 2, alternating for turns 1-6.", "Fae Realm", RITUAL_PROGRESS,
                  [ritual_event([1, 3, 5], ["regen p 2"]), ritual_event([2, 4, 6], ["poison _ 2"])]),
    map_name_adjectives=["Green", "Moonlight", "Fae", "Fickle", "Enchanted", "Bewitched", "Sylvan", "Twilight", "Midnight"],
    map_name_nouns=["Promise", "Grove", "Glade", "Thicket", "Woods", "Meadow", "Garden", "Court"]
  ),
  Faction("Kingdom of Amar", kingdom_of_amar, "⚖",
    basic_items=[
      Item.make("Knifewing Set", 2, "Deal 1 damage to immediate thrice.", ["repeat 3 damage i 1"]),
      Item.make("Animate Armor", 3, "Gain 1 fleeting armor.", ["armor p 1", "delay 0 armor p -1"]),
    ],
    special_items=[
      Item.make("Amarian Warsuit", 1, "Gain 1 armor, 2 prolific, and 3 sharp.", ["armor p 1", "prolific p 2", "sharp p 3"], rare=True)
    ],
    ritual=Ritual("Artificer's Ingenuity", "Gain 1 armor or 2 sharp, alternating for turns 3-8.", "Kingdom of Amar", RITUAL_PROGRESS,
                  [ritual_event([3, 5, 7], ["armor p 1"]), ritual_event([4, 6, 8], ["sharp p 2"])]),
    map_name_adjectives=["Copper", "Artificer's", "Crafted", "Gilded", "Shining", "Ingenious", "Artificial", "Clockwork"],
    map_name_nouns=["Workshop", "Guild", "Armory", "Plaza", "Bazaar", "City", "Sigil"]
  ),
  Faction("Infernal Plane", infernal_plane, "⛧",
    basic_items=[
      Item.make("Hellfire Torch", 3, "Burn 2 immediate.", ["burn i 2"]),
      Item.make("Summoning Circle", 4, "Gain 1 regen and call 1.", ["regen p 1", "call 1"])
    ],
    special_items=[
      Item.make("Demon's Blood", 1, "burn 3 self, gain 6 searing presence, 6 retaliate", ["burn p 3", "searing p 6", "retaliate p 6"], rare=True)
    ],
    ritual=Ritual("Imminent Inferno", "Burn 4 all.", "Infernal Plane", RITUAL_PROGRESS,
                  [ritual_event([4, 5, 6], ["burn a 4"])]),
    map_name_adjectives=["Scorched", "Burning", "Hellish", "Smoldering", "Demonic", "Devil's", "Blazing"],
    map_name_nouns=["Pits", "Inferno", "Hellscape", "Pentacale", "Cauldron", "Pyre", "Torture"]
  ),
  Faction("Dominion of Drael", dominion_of_drael, "⛨",
    basic_items=[
      Item.make("Captain's Warhorn", 1, "Block 5, Empower 5", ["block p 5", "empower p 5"]),
      Item.make("Shieldmage's Gauntlets", 2, "Gain 3 shield and 2 retaliate.", ["shield p 3", "retaliate p 2"]),
    ],
    special_items=[
      Item.make("Draelish Bomb", 1, "Deal 15 to all enemies, 5 damage to self", ["damage a 15", "damage p 5"], rare=True)
    ],
    ritual=Ritual("Draelish Warchant", "Gain 3 block and 3 empower on turns 1, 3, 5.", "Dominion of Drael", RITUAL_PROGRESS,
                  [ritual_event([1, 3, 5], ["block p 3", "empower p 3"])]),
    map_name_adjectives=["Imperial", "Conquered", "Militant", "Belligerent", "Zealot's", "Grinding"],
    map_name_nouns=["Oath", "Command", "Battlefield", "Siege", "Crusade", "War", "Conquest", "Barracks"]
  ),
  Faction("Spirits", spirits, "☯",
    basic_items=[
      Item.make("Spirit's Blessing", 1, "Gain 2 prolific.", ["prolific p 2"]),
      Item.make("Spirit Snare", 2, "At end of this round, stun 2 immediate.", ["delay 0 stun i 2"]),
    ],
    special_items=[
      Item.make("Unbridled Energy", 1, "Gain 2 energy of each color and prolific 2.", ["blue p 2", "red p 2", "gold p 2", "prolific p 2"], rare=True)
    ],
    ritual=Ritual("Glimpse the Beyond", "Gain 1 inventive and 1 prolific on turns 2, 4, 6.", "Spirits", RITUAL_PROGRESS,
                  [ritual_event([2, 4, 6], ["inventive p 1", "prolific p 1"])]),
    map_name_adjectives=["Ethereal", "Otherworldly", "Supernatural", "Tranquil", "Balanced", "Bountiful"],
    map_name_nouns=["Harmony", "Serenity", "Shrine", "Pagoda", "Stillness", "Springs", "Pools", "Fountain"]
  ),
  Faction("Shadow Realm", shadow_realm, "☽",
    basic_items=[
      Item.make("Brave Face", 2, "Face, then block 5.", ["face!", "block p 5"]),
      Item.make("Mirror Blade", 1, "Deal 6 damage immediately behind.", ["damage bi 6"])
    ],
    special_items=[
      Item.make("Voodoo Doll", 3, "Any target suffers 4 damage.", ["suffer _ 4"], rare=True)
    ],
    ritual=Ritual("Menacing Shadows", "Every turn, all enemies gain 1 vulnerable.", "Shadow Realm", RITUAL_PROGRESS,
                  [ritual_event(list(range(1, 11)), ["vulnerable a 1"])]),
    map_name_adjectives=["Indigo", "Murky", "Shrouded", "Lurking", "Maddening", "Night", "Black"],
    map_name_nouns=["Shadow", "Eclipse", "Dream", "Nightmare", "Terror", "Madness", "Void"]
  ),
  Faction("Ancient Horrors", ancient_horrors, "♅",
    basic_items=[
      Item.make("Damaged Ward", 4, "Gain 1 ward.", ["ward p 1"]),
      Item.make("Forbidden Text", 4, "Gain 1 inventive.", ["inventive p 1"]),
    ],
    special_items=[
      Item.make("Prayer to the Ancients", 3, "10 damage to random.", ["damage r 10"], rare=True)
    ],
    ritual=Ritual("Call the Unspeakable", "Gain 2 ward on turn 1, then deal 6 damage to random 6 times on turn 6.", "Ancient Horrors", RITUAL_PROGRESS,
                  [ritual_event([1], ["ward p 2"]), ritual_event([6], ["repeat 6 damage r 6"])], priority=4),
    map_name_adjectives=["Old God's", "Ancient", "Unspeakable", "Eldritch", "Forbidden", "Unholy", "Unnatural"],
    map_name_nouns=["Spire", "Obelisk", "Monolith", "Idol", "Monument", "Altar", "Teeth", "Maw", "Eyes"]
  )
]

all_special_items = sum([faction.special_items for faction in factions], [])
all_basic_items = sum([faction.basic_items for faction in factions], [])

faction_dict = {faction.name: faction for faction in factions}
faction_rituals_dict = {faction.name: faction.ritual for faction in factions}