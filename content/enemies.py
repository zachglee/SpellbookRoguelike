from copy import deepcopy
from typing import List
from model.encounter import EnemySet, Enemy, EnemySpawn
from content.enemy_actions import (
  AttackAction, AttackSide, AttackAll, EnergyThresholdAction, HealAction, SelfDamageAction, AttackImmediate,
  BackstabAction, NearFarAction, PackTacticsAction, MoveAction, CowardlyAction,
  CallAction, MultiAction, SpellcastThresholdAction, WindupAction, HealthThresholdAction,
  NothingAction, CautiousAction, AddConditionAction, SetConditionAction,
  TheVultureEntryAction, OverwhelmAction, SideOverwhelmAction)

#

enemies = {
  "Harpy Harrier": Enemy.make(10, "Harpy Harrier", BackstabAction(AttackAction(4), AttackAction(2))),
  "Ravenous Hound": Enemy.make(10, "Ravenous Hound", PackTacticsAction(AttackAction(5), AttackAction(2))),
  "Zombie": Enemy.make(16, "Zombie", NearFarAction(AttackAction(6), MoveAction(-1))),
  "Bandit": Enemy.make(15, "Bandit", CowardlyAction(MoveAction(1), AttackAction(4))),
  "Bat": Enemy.make(3, "Bat", AttackAction(1)),
  "Vampire": Enemy.make(20, "Vampire", AttackAction(8, lifesteal=True)),
  "Hawk": Enemy.make(3, "Hawk", AddConditionAction("vulnerable", 1, "player"), entry=AddConditionAction("vulnerable", 1, "player")),
  "Hunter": Enemy.make(20, "Hunter", NearFarAction(MultiAction([MoveAction(1), AddConditionAction("armor", 1, "self")]), AttackAction(10))),
  "Charging Ogre": Enemy.make(30, "Charging Ogre", NearFarAction(AttackAction(8), MultiAction([MoveAction(-10), AddConditionAction("empower", 8, "self")]))),
  "Evasive Skydancer": Enemy.make(15, "Evasive Skydancer", CautiousAction(AddConditionAction("sharp", 3, "self"), AttackAction(6)), entry=AddConditionAction("enduring", 6, "self")),
  "The Vulture": Enemy.make(40, "The Vulture", AttackAction(3), entry=TheVultureEntryAction()),
  #
  "Skitterer": Enemy.make(3, "Skitterer", OverwhelmAction(AttackAction(3), AttackAction(1), 4)),
  "Decaying Corpse": Enemy.make(20, "Decaying Corpse", AttackAction(6), entry=AddConditionAction("poison", 4, "self")),
  "Faerie Assassin": Enemy.make(6, "Faerie Assassin", BackstabAction(AddConditionAction("poison", 3, "player"), AttackAction(3))),
  "Knifehand": Enemy.make(20, "Knifehand", MultiAction([AttackAction(4), AttackAction(5), AttackAction(6)])),
  "Blazing Eye": Enemy.make(16, "Blazing Eye", BackstabAction(AddConditionAction("burn", 1, "player"), AddConditionAction("burn", 5, "player"))),
  "Creeping Shadow": Enemy.make(10, "Creeping Shadow", BackstabAction(AddConditionAction("sharp", 5, "self"), AttackAction(1)), entry=AddConditionAction("durable", 2, "self"), exp=10),
  "Stoneguard": Enemy.make(6, "Stoneguard", AttackAction(3), entry=AddConditionAction("armor", 3, "self")),
  "Conniving Impfiend": Enemy.make(6, "Conniving Impfiend", OverwhelmAction(AddConditionAction("burn", 2, "player"), AttackAction(2), 3)),
  "Insistent Duelist": Enemy.make(20, "Insistent Duelist",
                              SideOverwhelmAction(
                                MultiAction([AddConditionAction("sharp", 2, "self"), AddConditionAction("armor", 2, "self")]),
                                MultiAction([SetConditionAction("armor", 0, "self"), AttackAction(3), AttackAction(3)]), 2
                              ), entry=AddConditionAction("ward", 1, "player")),
  #
  "Cultist": Enemy.make(10, "Cultist", CallAction("Demon of the Inferno", 1), entry=AddConditionAction("burn", 4, "self"), exp=3),
  "Demon of the Inferno": Enemy.make(40, "Demon of the Inferno", AttackAction(10, lifesteal=True), entry=AddConditionAction("burn", 4, "player")),
  "Injured Troll": Enemy.make(40, "Injured Troll", AttackAction(4), entry=MultiAction([SelfDamageAction(20), AddConditionAction("regen", 6, "self")]), exp=14),
  "Crossbow Deadeye": Enemy.make(12, "Crossbow Deadeye", WindupAction(AttackAction(10), 1)),
  "Herald of Doom": Enemy.make(5, "Herald of Doom", SelfDamageAction(5)),
  "The Executioner": Enemy.make(40, "The Executioner", WindupAction(AttackAction(25), 1)),
  "Cloud of Daggers": Enemy.make(6, "Cloud of Daggers",
                            MultiAction([AttackAction(2), AttackAction(2), AttackAction(2),
                                        AttackSide(2), AttackSide(2), AttackSide(2)]),
                            entry=AddConditionAction("durable", 2, "self"), exp=6),
  "Slumbering Giant": Enemy.make(45, "Slumbering Giant", AttackAction(20), entry=AddConditionAction("stun", 4, "self")),
  "Mindless Maw": Enemy.make(50, "Mindless Maw", MultiAction([AttackImmediate(5, lifesteal=True), AddConditionAction("sharp", 5, "self")]), entry=SelfDamageAction(30), exp=20),
  "Midnight Courtier": Enemy.make(15, "Imperious Seelie", EnergyThresholdAction(
      AddConditionAction("retaliate", 3, "self"), AddConditionAction("poison", 3, "player"), 2)),
  "Zealous Battlemage": Enemy.make(8, "Zealous Battlemage", AttackAction(1), entry=MultiAction([AddConditionAction("block", 8, "self"), AddConditionAction("empower", 8, "self")])),
  "Draelish Captain": Enemy.make(7, "Draelish Captain", AttackAction(0), entry=MultiAction([AddConditionAction("block", 4, "all_enemies"), AddConditionAction("empower", 4, "all_enemies")])),
  "Conscript": Enemy.make(6, "Conscript", CowardlyAction(NothingAction(), AttackAction(2), hp_threshold=7)),
  #
  "Fire Elemental": Enemy.make(20, "Fire Elemental",
                      MultiAction([
                        AddConditionAction("burn", 3, "player"),
                        AddConditionAction("red", 1, "player"),
                        SetConditionAction("burn", 0, "self")])),
  "Frost Elemental": Enemy.make(25, "Frost Elemental",
                       MultiAction([
                          AddConditionAction("slow", 2, "player"),
                          AddConditionAction("blue", 1, "player"),
                          AttackAction(1)])),
  "Lightning Elemental": Enemy.make(15, "Lightning Elemental",
                            MultiAction([
                              AttackAction(6),
                              AddConditionAction("gold", 1, "player"),
                              AddConditionAction("empower", 6, "player")])),
  "Vengeful Mine": Enemy.make(1, "Vengeful Mine", OverwhelmAction(MultiAction([SelfDamageAction(3), AttackAction(6)]), NothingAction(), 5), entry=AddConditionAction("retaliate", 3, "self")),
  "Bomber Zealot": Enemy.make(8, "Bomber Zealot", WindupAction(MultiAction([AttackAction(16), AttackSide(16), SelfDamageAction(16)]), 1), entry=AddConditionAction("block", 8, "self")),
  "Grizzled Shieldmage": Enemy.make(10, "Grizzled Shieldmage",
                               NearFarAction(AttackAction(3),
                                             MultiAction([AddConditionAction("shield", 5, "immediate"), AddConditionAction("retaliate", 1, "immediate")])),
                               entry=AddConditionAction("block", 10, "self")),
  "Incubated Fleshling": Enemy.make(6, "Incubated Fleshling", AttackAction(1)),
  "Corrupting Spire": Enemy.make(1, "Corrupting Spire", NothingAction(), entry=MultiAction([
    AddConditionAction("stun", 1, "all_enemies"),
    AddConditionAction("sharp", 5, "all_enemies"),
    AddConditionAction("regen", 5, "all_enemies"),
    AddConditionAction("block", 5, "all_enemies"),
  ])),
  "Lurking Scavenger": Enemy.make(12, "Lurking Scavenger", PackTacticsAction(AttackAction(5, lifesteal=True), AddConditionAction("regen", 2, "self"))),
  "Artificer Princess": Enemy.make(10, "Artificer Princess",
                              NearFarAction(AttackAction(1),
                                            MultiAction([
                                              AddConditionAction("sharp", 2, "self"),
                                              AddConditionAction("armor", 2, "self"),
                                            ])),
                              entry=AddConditionAction("sharp", 2, "all_enemies")),
  "Vampire Lord": Enemy.make(24, "Vampire Lord",
                        HealthThresholdAction(
                          AddConditionAction("sharp", 1, "player"), AttackAction(6, lifesteal=True), 24),
                        entry=MultiAction([
                          SelfDamageAction(6),
                          AddConditionAction("retaliate", 3, "self"),
                        ])),
  "Cocky Descender": Enemy.make(9, "Cocky Descender",
                                  HealthThresholdAction(
                                    MultiAction([AttackAction(4), AttackAction(4)]),
                                    AttackAction(2), 9)),
  "Fickle Witch-Queen": Enemy.make(12, "Fickle Witch-Queen",
                           CautiousAction(NothingAction(), WindupAction(MultiAction([
                               SetConditionAction("poison", 0, "player"),
                               AddConditionAction("regen", 4, "player")
                               ]), 2)),
                           entry=AddConditionAction("poison", 3, "player")),
  "Screeching Fury": Enemy.make(18, "Screeching Fury",
                           HealthThresholdAction(AttackAction(2),
                                                 MultiAction([
                                                     AttackAction(4),
                                                     AttackAction(4),
                                                     AddConditionAction("sharp", 1, "self")]
                                                 ), 18)),
  "Witch-Burner Devil": Enemy.make(20, "Witch-Burner Devil",
                              EnergyThresholdAction(AddConditionAction("burn", 4, "player"), AttackAction(1), 1)),
  "Tithetaker": Enemy.make(25, "Tithetaker",
                      EnergyThresholdAction(
                          AddConditionAction("regen", 1, "player"),
                          AttackAction(13, lifesteal=True), 6)),
  "Generous Sprite": Enemy.make(1, "Generous Sprite",
                         BackstabAction(
                             WindupAction(AddConditionAction("green", 1, "player"), 2),
                             SelfDamageAction(1),
                         )),
  "Blue Spirit-Hunter": Enemy.make(12, "Blue Spirit-Hunter", EnergyThresholdAction(
      MultiAction([
          AddConditionAction("shield", 3, "self"),
          AttackAction(3),
      ]),
      NothingAction(), 1, colors=["blue"])),
  "Red Spirit-Hunter": Enemy.make(12, "Red Spirit-Hunter", EnergyThresholdAction(
      AddConditionAction("burn", 3, "player"),
      NothingAction(), 1, colors=["red"])),
  "Gold Spirit-Hunter": Enemy.make(12, "Gold Spirit-Hunter", EnergyThresholdAction(
      AttackAction(6),
      NothingAction(), 1, colors=["gold"])),
  "Font of Magic": Enemy.make(16, "Font of Magic",
                         MultiAction([
                            AddConditionAction("red", 1, "player"),
                            AddConditionAction("gold", 1, "player"),
                            AddConditionAction("blue", 1, "player"),
                         ])),
  "Nightmare Remnant": Enemy.make(5, "Nightmare Remnant", BackstabAction(AttackAction(5), SelfDamageAction(5))),
  "Dreamstalker": Enemy.make(20, "Dreamstalker", BackstabAction(
      AddConditionAction("slow", 2, "player"),
      AttackAction(6))),
  "Shadow of a Doubt": Enemy.make(20, "Shadow of a Doubt", BackstabAction(
      AddConditionAction("vulnerable", 2, "player"),
      AttackAction(6))),
  "Necromancer Apprentice": Enemy.make(12, "Necromancer Apprentice",
      NearFarAction(
        MultiAction([MoveAction(1), AttackAction(3), SelfDamageAction(3)]),
        AddConditionAction("regen", 4, "immediate"),
      ),
      entry=AddConditionAction("undying", 1, "all_enemies")),
  "Assault Golem": Enemy.make(20, "Assault Golem", CautiousAction(AttackAction(10), MultiAction([
      AddConditionAction("shield", 2, "self"), AttackAction(2)]))),
  "Aegis Orb": Enemy.make(20, "Aegis Orb", MultiAction([AddConditionAction("armor", 1, "all_enemies"), AddConditionAction("retaliate", 1, "all_enemies")])),
  "Defective Shieldbot": Enemy.make(10, "Defective Shieldbot",
                               MultiAction([AttackAction(3), AddConditionAction("shield", -6, "self")]),
                               entry=AddConditionAction("shield", 30, "self")),
  "Plated Warmech": Enemy.make(12, "Plated Warmech", AttackAction(4), entry=AddConditionAction("armor", 6, "self")),
  "Relentless Legionnaire": Enemy.make(8, "Relentless Legionnaire", AttackAction(2),
    entry=MultiAction([AddConditionAction("undying", 1, "self"), AddConditionAction("empower", 3, "self")])),
  "Eternal Berserker": Enemy.make(12, "Eternal Berserker", MultiAction([
     AttackAction(2), AddConditionAction("sharp", 2, "self"), AddConditionAction("regen", 3, "self")]),
    entry=MultiAction([AddConditionAction("undying", 3, "self")])),
  "Risen Warrior": Enemy.make(15, "Risen Warrior", AttackAction(10), entry=AddConditionAction("encase", 20, "self")),
  "Intrepid Bannerman": Enemy.make(15, "Intrepid Bannerman", AddConditionAction("empower", 4, "side"),
    entry=AddConditionAction("undying", 1, "self")),
  "Inquisitive Eye": Enemy.make(4, "Inquisitive Eye", CallAction(None, 1)),
  "Collector's Cage": Enemy.make(4, "Collector's Cage", WindupAction(AddConditionAction("doom", 1, "player"), 1, windup_action=AddConditionAction("encase", 4, "player"))),
  "Grasping Hand": Enemy.make(4, "Grasping Hand", AddConditionAction("slow", 1, "player")),
  "Collector of Bodies": Enemy.make(16, "Collector of Bodies", AddConditionAction("doom", 1, "player"),
                               entry=AddConditionAction("encase", 16, "player")),
  "Collector of Magic": Enemy.make(20, "Collector of Magic", EnergyThresholdAction(AttackAction(10), NothingAction(), 1)),
  "Collector of Still-lifes": Enemy.make(20, "Collector of Still-lifes", SpellcastThresholdAction(
      AttackAction(10), AddConditionAction("slow", 1, "player"), 1)),
  "Doom of Blades": Enemy.make(40, "Doom of Blades", MultiAction([AttackAll(15), AttackAction(15)])),
  "Doom of Plagues": Enemy.make(40, "Doom of Plagues", AddConditionAction("poison", 3, "player"),
                           entry=AddConditionAction("poison", 6, "player")),
  "Wave of Doom": Enemy.make(15, "Wave of Doom", WindupAction(AttackAction(8), 1),
                         entry=AddConditionAction("retaliate", 1, "self")),
  "Horde Beast": Enemy.make(10, "Horde Beast", OverwhelmAction(AttackAction(8), AttackAction(4), 4)),
  "Blade Forger": Enemy.make(8, "Blade Forger", SideOverwhelmAction(
      NothingAction(), AddConditionAction("sharp", 2, "player"), 2)),
  "Wandering Healer": Enemy.make(8, "Wandering Healer", CautiousAction(NothingAction(),
      AddConditionAction("regen", 2, "player")), entry=AddConditionAction("regen", 3, "player")),
  "Defiant Survivor": Enemy.make(8, "Defiant Survivor", CautiousAction(
      NothingAction(), AddConditionAction("searing", 3, "player"))),
  "Grizzled Armorer": Enemy.make(8, "Grizzled Armorer", SideOverwhelmAction(
      NothingAction(), AddConditionAction("armor", 1, "player"), 2)),

  # Hoarding Dragons? Wound them and they go away. Or they go into neutral mode They interact with your items?
  # more enemy design that favor's blue playstyle -- enemies that attack every other turn but have tons of health
  #  so its not efficient to kill them, you just want to block them
  # Anti-mage faction? A lot of spellcast threshold stuff? Pro item
  # step-up faction? Little guys that get stronger as long as there are no higher maxhp enemies?
  # set up break on you and they hurt you extra when they break. (rewards you for full-blocking)

  # Gets stronger if other enemies dead
  # Really late-spawning enemies where you actually do just need to survive them?
  # Swarm of late spawning enemies?
  # Calling enemies?
  # * really big burst of enemies where the main issue is just burst kill them all in one turn?
  # More cowardly enemies? ^^ Swarm of low hp cowardly enemies?

  # reverse cowardly? It's good if there's noone higher hp than them? Commander?
  # does something good for you when there gets to be 5 enemies?
  # heal immediate?
  # more call action enemies?
  # enemy that rewards you for full blocking its attacks
  # energy vampire -- rylie ellam
  # enemies where damage is not the best option
}

doombringers = [
  # Doombringers
  EnemySet("Doom of Blades", [
    EnemySpawn(4, "b", enemies["Blade Forger"]),
    EnemySpawn(6, "f", enemies["Doom of Blades"]),
  ], faction="Doombringers"),
  EnemySet("Doom of Plagues", [
    EnemySpawn(3, "b", enemies["Wandering Healer"]),
    EnemySpawn(5, "f", enemies["Doom of Plagues"]),
  ], faction="Doombringers"),
  EnemySet("Doom of Waves", [
    EnemySpawn(3, "b", enemies["Defiant Survivor"]),
    EnemySpawn(4, "f", enemies["Wave of Doom"]),
    EnemySpawn(5, "f", enemies["Wave of Doom"]),
    EnemySpawn(6, "f", enemies["Wave of Doom"]),
  ], faction="Doombringers"),
  EnemySet("Doom of Hordes", [
    EnemySpawn(4, "b", enemies["Grizzled Armorer"]),
    EnemySpawn(6, "f", enemies["Horde Beast"]),
    EnemySpawn(6, "f", enemies["Horde Beast"]),
    EnemySpawn(6, "b", enemies["Horde Beast"]),
    EnemySpawn(6, "b", enemies["Horde Beast"]),
  ], faction="Doombringers")
]

the_collectors = [
  # The Collectors
  EnemySet("Collector of Bodies", [
    EnemySpawn(1, "b", enemies["Collector's Cage"]),
    EnemySpawn(4, "f", enemies["Collector of Bodies"]),
  ], faction="The Collectors"),
  EnemySet("Collector of Magic", [
    EnemySpawn(1, "b", enemies["Inquisitive Eye"]),
    EnemySpawn(4, "f", enemies["Collector of Magic"]),
  ], faction="The Collectors"),
  EnemySet("Collector of Still-lifes", [
    EnemySpawn(1, "b", enemies["Grasping Hand"]),
    EnemySpawn(4, "f", enemies["Collector of Still-lifes"]),
  ], faction="The Collectors"),
  EnemySet("Acquisitions Party", [
    EnemySpawn(1, "b", enemies["Inquisitive Eye"]),
    EnemySpawn(1, "f", enemies["Inquisitive Eye"]),
    EnemySpawn(2, "b", enemies["Collector's Cage"]),
    EnemySpawn(2, "f", enemies["Collector's Cage"]),
    EnemySpawn(3, "b", enemies["Grasping Hand"]),
    EnemySpawn(3, "f", enemies["Grasping Hand"])
  ], faction="The Collectors")
]

undying_legion = [
  # Undying Legion
  EnemySet("Relentless Legionnaire", [
    EnemySpawn(2, "f", enemies["Relentless Legionnaire"]),
    EnemySpawn(3, "b", enemies["Relentless Legionnaire"]),
    EnemySpawn(4, "f", enemies["Relentless Legionnaire"])
  ], faction="Undying Legion"),
  EnemySet("Eternal Berserker", [
    EnemySpawn(1, "f", enemies["Eternal Berserker"]),
  ], faction="Undying Legion"),
  EnemySet("Risen Warrior", [
    EnemySpawn(1, "b", enemies["Risen Warrior"])
  ], faction="Undying Legion"),
  EnemySet("Intrepid Bannerman", [
    EnemySpawn(3, "f", enemies["Intrepid Bannerman"]),
    EnemySpawn(4, "f", enemies["Conscript"])
  ], faction="Undying Legion")
]

freed_automata = [
  # Freed Automata
  EnemySet("Assault Golem", [
    EnemySpawn(2, "f", enemies["Assault Golem"])
  ], faction="Freed Automata"),
  EnemySet("Aegis Orb", [
    EnemySpawn(1, "f", enemies["Aegis Orb"])
  ], faction="Freed Automata"),
  EnemySet("Defective Shieldbot", [
    EnemySpawn(1, "f", enemies["Defective Shieldbot"])
  ], faction="Freed Automata"),
  EnemySet("Plated Warmech", [
    EnemySpawn(3, "f", enemies["Plated Warmech"])
  ], faction="Freed Automata")
]

saik_collective = [
  # Sa'ik Collective
  EnemySet("Harpy Harriers", [
    EnemySpawn(1, "b", enemies["Harpy Harrier"]),
    EnemySpawn(2, "f", enemies["Harpy Harrier"]),
    EnemySpawn(3, "b", enemies["Harpy Harrier"])
  ], faction="Sa'ik Collective"),
  EnemySet("Evasive Skydancer", [
    EnemySpawn(2, "f", enemies["Evasive Skydancer"])
  ], faction="Sa'ik Collective"),
  EnemySet("Sa'ik Descenders", [
    EnemySpawn(3, "f", enemies["Cocky Descender"]),
    EnemySpawn(3, "b", enemies["Cocky Descender"]),
  ], faction="Sa'ik Collective"),
  EnemySet("Screeching Fury", [
    EnemySpawn(3, "b", enemies["Screeching Fury"]),
  ], faction="Sa'ik Collective")
]

house_of_imir = [
  # House of Imir
  EnemySet("Ravenous Hounds", [
    EnemySpawn(2, "f", enemies["Ravenous Hound"]),
    EnemySpawn(3, "b", enemies["Ravenous Hound"]),
    EnemySpawn(4, "f", enemies["Ravenous Hound"])
  ], faction="House of Imir"),
  EnemySet("Wanton Vampire", [
    EnemySpawn(3, "b", enemies["Bat"]),
    EnemySpawn(4, "f", enemies["Vampire"])
  ], faction="House of Imir"),
  EnemySet("Lurking Scavengers", [
    EnemySpawn(1, "b", enemies["Lurking Scavenger"]),
    EnemySpawn(3, "b", enemies["Lurking Scavenger"]),
    EnemySpawn(5, "b", enemies["Lurking Scavenger"]),
  ], faction="House of Imir"),
  EnemySet("Vampire Lord", [
    EnemySpawn(3, "f", enemies["Vampire Lord"]),
  ], faction="House of Imir"),
]

movs_horde = [
  # Mov's Horde
  EnemySet("Zombie Mob", [
    EnemySpawn(3, "f", enemies["Zombie"]),
    EnemySpawn(4, "f", enemies["Zombie"]),
    EnemySpawn(5, "f", enemies["Zombie"])
  ], faction="Mov's Horde"),
  EnemySet("Decaying Corpse", [
    EnemySpawn(1, "f", enemies["Decaying Corpse"])
  ], faction="Mov's Horde"),
  EnemySet("Skittering Swarm", [
    EnemySpawn(1, "f", enemies["Skitterer"]),
    EnemySpawn(2, "f", enemies["Skitterer"]),
    EnemySpawn(3, "b", enemies["Skitterer"]),
    EnemySpawn(4, "b", enemies["Skitterer"]),
    EnemySpawn(5, "f", enemies["Skitterer"]),
    EnemySpawn(5, "b", enemies["Skitterer"]),
    EnemySpawn(6, "f", enemies["Skitterer"]),
    EnemySpawn(6, "b", enemies["Skitterer"]),
  ], faction="Mov's Horde"),
  EnemySet("Necromancer Apprentice", [
    EnemySpawn(4, "f", enemies["Necromancer Apprentice"]),
  ]),
]

company_of_blades = [
  # Company of Blades
  EnemySet("Bandit Ambush", [
    EnemySpawn(2, "f", enemies["Bandit"]),
    EnemySpawn(2, "b", enemies["Bandit"])
  ], faction="Company of Blades"),
  EnemySet("Hunter and Hawk", [
    EnemySpawn(3, "b", enemies["Hawk"]),
    EnemySpawn(4, "f", enemies["Hunter"])
  ], faction="Company of Blades"),
  EnemySet("Insistent Duelist", [
    EnemySpawn(2, "f", enemies["Insistent Duelist"])
  ], faction="Company of Blades"),
  EnemySet("Crossbow Deadeyes", [
    EnemySpawn(2, "b", enemies["Crossbow Deadeye"]),
    EnemySpawn(4, "f", enemies["Crossbow Deadeye"]),
    EnemySpawn(6, "b", enemies["Crossbow Deadeye"]),
  ], faction="Company of Blades"),
]

giantkin = [
  # Giantkin
  EnemySet("Charging Ogre", [
    EnemySpawn(4, "f", enemies["Charging Ogre"])
  ], faction="Giantkin"),
  EnemySet("Injured Troll", [
    EnemySpawn(2, "f", enemies["Injured Troll"])
  ], faction="Giantkin"),
  EnemySet("Slumbering Giant", [
    EnemySpawn(1, "f", enemies["Slumbering Giant"]),
  ], faction="Giantkin"),
  EnemySet("The Executioner", [
    EnemySpawn(4, "b", enemies["Herald of Doom"]),
    EnemySpawn(6, "f", enemies["The Executioner"]),
  ], faction="Giantkin"),
]

fae_realm = [
  # Fae Realm
  EnemySet("Faerie Assassins", [
    EnemySpawn(2, "b", enemies["Faerie Assassin"]),
    EnemySpawn(4, "b", enemies["Faerie Assassin"]),
    EnemySpawn(6, "b", enemies["Faerie Assassin"]),
  ], faction="Fae Realm"),
  EnemySet("Midnight Court", [
      EnemySpawn(2, "f", enemies["Midnight Courtier"]),
      EnemySpawn(3, "b", enemies["Midnight Courtier"]),
  ]),
  EnemySet("Fickle Witch-Queen", [
      EnemySpawn(2, "f", enemies["Fickle Witch-Queen"])
  ], faction="Fae Realm"),
  EnemySet("Tithetaker", [
      EnemySpawn(1, "b", enemies["Generous Sprite"]),
      EnemySpawn(5, "f", enemies["Tithetaker"])
  ], faction="Fae Realm"),
]

kingdom_of_amar = [
  # Kingdom of Amar
  EnemySet("Knifehand", [
    EnemySpawn(5, "f", enemies["Knifehand"])
  ], faction="Kingdom of Amar"),
  EnemySet("Stoneguard Patrol", [
    EnemySpawn(3, "f", enemies["Stoneguard"]),
    EnemySpawn(3, "f", enemies["Stoneguard"]),
    EnemySpawn(5, "b", enemies["Stoneguard"]),
    EnemySpawn(5, "b", enemies["Stoneguard"]),
  ], faction="Kingdom of Amar"),
  EnemySet("Cloud of Daggers", [
    EnemySpawn(3, "f", enemies["Cloud of Daggers"]),
    EnemySpawn(3, "b", enemies["Cloud of Daggers"]),
  ], faction="Kingdom of Amar"),
  EnemySet("Princess' Entourage", [
    EnemySpawn(2, "f", enemies["Stoneguard"]),
    EnemySpawn(2, "f", enemies["Stoneguard"]),
    EnemySpawn(5, "f", enemies["Artificer Princess"]),
  ], faction="Kingdom of Amar"),
]

infernal_plane = [
  # Infernal Plane
  EnemySet("Blazing Eye", [
    EnemySpawn(3, "f", enemies["Blazing Eye"])
  ], faction="Infernal Plane"),
  EnemySet("Conniving Impfiends", [
    EnemySpawn(4, "b", enemies["Conniving Impfiend"]),
    EnemySpawn(4, "b", enemies["Conniving Impfiend"]),
    EnemySpawn(4, "b", enemies["Conniving Impfiend"]),
  ], faction="Infernal Plane"),
  EnemySet("Cult of the Inferno", [
    EnemySpawn(1, "b", enemies["Cultist"]),
    EnemySpawn(2, "b", enemies["Cultist"]),
    EnemySpawn(3, "b", enemies["Cultist"]),
    EnemySpawn(11, "f", enemies["Demon of the Inferno"]),
  ], faction="Infernal Plane"),
  EnemySet("Witch-Burner Devil", [
      EnemySpawn(2, "f", enemies["Witch-Burner Devil"])
  ], faction="Infernal Plane"),
]

dominion_of_drael = [
  # Dominion of Drael
  EnemySet("Zealous Battlemages", [
    EnemySpawn(1, "f", enemies["Zealous Battlemage"]),
    EnemySpawn(2, "f", enemies["Zealous Battlemage"]),
  ], faction="Dominion of Drael"),
  EnemySet("Draelish Patrol", [
    EnemySpawn(2, "f", enemies["Conscript"]),
    EnemySpawn(3, "f", enemies["Conscript"]),
    EnemySpawn(4, "f", enemies["Conscript"]),
    EnemySpawn(5, "f", enemies["Draelish Captain"])
  ], faction="Dominion of Drael"),
  EnemySet("Draelish Bombsquad", [
    EnemySpawn(2, "f", enemies["Bomber Zealot"]),
    EnemySpawn(4, "b", enemies["Bomber Zealot"]),
  ], faction="Dominion of Drael"),
  EnemySet("Shieldmage Squad", [
    EnemySpawn(3, "f", enemies["Grizzled Shieldmage"]),
    EnemySpawn(4, "f", enemies["Grizzled Shieldmage"]),
    EnemySpawn(5, "f", enemies["Grizzled Shieldmage"]),
  ], faction="Dominion of Drael"),
]

spirits = [
  # Spirits
  EnemySet("Lightning Elemental", [
    EnemySpawn(1, "f", enemies["Lightning Elemental"])
  ], faction="Spirits"),
  EnemySet("Frost Elemental", [
    EnemySpawn(2, "f", enemies["Frost Elemental"])
  ], faction="Spirits"),
  EnemySet("Fire Elemental", [
    EnemySpawn(3, "f", enemies["Fire Elemental"])
  ], faction="Spirits"),
  EnemySet("Font of Magic", [
      EnemySpawn(4, "f", enemies["Blue Spirit-Hunter"]),
      EnemySpawn(4, "f", enemies["Red Spirit-Hunter"]),
      EnemySpawn(4, "f", enemies["Gold Spirit-Hunter"]),
      EnemySpawn(5, "b", enemies["Font of Magic"])
  ], faction="Spirits"),
]

shadow_realm = [
  # Shadow Realm
  EnemySet("Creeping Shadow", [
    EnemySpawn(1, "b", enemies["Creeping Shadow"])
  ], faction="Shadow Realm"),
  EnemySet("Nightmare Remnant", [
    EnemySpawn(2, "b", enemies["Nightmare Remnant"]),
    EnemySpawn(2, "f", enemies["Nightmare Remnant"]),
    EnemySpawn(3, "b", enemies["Nightmare Remnant"]),
    EnemySpawn(3, "f", enemies["Nightmare Remnant"]),
    EnemySpawn(4, "b", enemies["Nightmare Remnant"]),
    EnemySpawn(4, "f", enemies["Nightmare Remnant"]),
  ], faction="Shadow Realm"),
  EnemySet("Dreamstalker", [
    EnemySpawn(3, "b", enemies["Dreamstalker"])
  ], faction="Shadow Realm"),
  EnemySet("Shadow of a Doubt", [
    EnemySpawn(4, "b", enemies["Shadow of a Doubt"])
  ])
]

ancient_horrors = [
  # Ancient Horrors
  EnemySet("Vengeful Minefield", [
    EnemySpawn(1, "f", enemies["Vengeful Mine"]),
    EnemySpawn(2, "b", enemies["Vengeful Mine"]),
    EnemySpawn(3, "f", enemies["Vengeful Mine"]),
    EnemySpawn(4, "b", enemies["Vengeful Mine"]),
  ], faction="Ancient Horrors"),
  EnemySet("Corrupting Spire", [
    EnemySpawn(2, "b", enemies["Incubated Fleshling"]),
    EnemySpawn(3, "b", enemies["Incubated Fleshling"]),
    EnemySpawn(4, "b", enemies["Incubated Fleshling"]),
    EnemySpawn(5, "b", enemies["Corrupting Spire"]),
  ], faction="Ancient Horrors"),
  EnemySet("Mindless Maw", [
    EnemySpawn(4, "f", enemies["Mindless Maw"]),
  ], faction="Ancient Horrors"),
  EnemySet("The Vulture", [
    EnemySpawn(6, "b", enemies["The Vulture"])
  ], faction="Ancient Horrors"),
]

factions = [
    saik_collective,
    house_of_imir,
    movs_horde,
    company_of_blades,
    giantkin,
    fae_realm,
    kingdom_of_amar,
    infernal_plane,
    dominion_of_drael,
    spirits,
    shadow_realm,
    ancient_horrors
]

enemy_sets = (
    saik_collective +
    house_of_imir +
    movs_horde +
    company_of_blades +
    giantkin +
    fae_realm +
    kingdom_of_amar +
    infernal_plane +
    dominion_of_drael +
    spirits +
    shadow_realm +
    ancient_horrors
)
