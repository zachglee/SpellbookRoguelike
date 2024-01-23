from copy import deepcopy
from typing import List
from model.enemy import EnemySet, Enemy, EnemySpawn
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
                            entry=AddConditionAction("durable", 3, "self"), exp=6),
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
                               NearFarAction(AttackAction(2),
                                             MultiAction([AddConditionAction("shield", 5, "immediate"), AddConditionAction("retaliate", 1, "immediate")])),
                               entry=AddConditionAction("block", 10, "self")),
  "Incubated Fleshling": Enemy.make(6, "Incubated Fleshling", AttackAction(1)),
  "Corrupting Spire": Enemy.make(1, "Corrupting Spire", NothingAction(), entry=MultiAction([
    AddConditionAction("stun", 1, "all_enemies"),
    AddConditionAction("sharp", 4, "all_enemies"),
    AddConditionAction("regen", 4, "all_enemies"),
    AddConditionAction("shield", 4, "all_enemies"),
  ])),
  "Lurking Scavenger": Enemy.make(12, "Lurking Scavenger", PackTacticsAction(AttackAction(5, lifesteal=True), AddConditionAction("regen", 2, "self"))),
  "Artificer Princess": Enemy.make(12, "Artificer Princess",
                              NearFarAction(AttackAction(1),
                                            MultiAction([
                                              AddConditionAction("sharp", 2, "self"),
                                              AddConditionAction("armor", 2, "self"),
                                            ])),
                              entry=AddConditionAction("sharp", 2, "all_enemies")),
  "Vampire Lord": Enemy.make(25, "Vampire Lord",
                        HealthThresholdAction(
                          AddConditionAction("sharp", 1, "player"), AttackAction(7, lifesteal=True), 1),
                        entry=MultiAction([
                          SelfDamageAction(7),
                          AddConditionAction("retaliate", 2, "self"),
                        ])),
  "Cocky Descender": Enemy.make(9, "Cocky Descender",
                                  HealthThresholdAction(
                                    MultiAction([AttackAction(4), AttackAction(4)]),
                                    AttackAction(2), 1)),
  "Fickle Witch-Queen": Enemy.make(12, "Fickle Witch-Queen",
                           CautiousAction(NothingAction(), WindupAction(MultiAction([
                               SetConditionAction("poison", 0, "player"),
                               AddConditionAction("regen", 4, "player")
                               ]), 2)),
                           entry=AddConditionAction("poison", 3, "player")),
  "Screeching Fury": Enemy.make(20, "Screeching Fury",
                           HealthThresholdAction(AttackAction(2),
                                                 MultiAction([
                                                     AttackAction(5),
                                                     AttackAction(5),
                                                     AddConditionAction("sharp", 1, "self")]
                                                 ), 1)),
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
  "Font of Magic": Enemy.make(10, "Font of Magic", NothingAction(),
                         entry=MultiAction([
                            AddConditionAction("red", 1, "player"),
                            AddConditionAction("gold", 1, "player"),
                            AddConditionAction("blue", 1, "player"),
                         ])),
  "Nightmare Remnant": Enemy.make(5, "Nightmare Remnant", BackstabAction(AttackAction(5), SelfDamageAction(5))),
  "Dreamstalker": Enemy.make(20, "Dreamstalker", BackstabAction(
      AddConditionAction("slow", 2, "player"),
      AttackAction(6))),
  "Shadow of a Doubt": Enemy.make(20, "Shadow of a Doubt", BackstabAction(
      AttackAction(6),
      AddConditionAction("vulnerable", 2, "player"))),
  "Necromancer Apprentice": Enemy.make(15, "Necromancer Apprentice",
      NearFarAction(
        MultiAction([AddConditionAction("regen", 3, "self"), AttackAction(3)]),
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
  "Collector's Cage": Enemy.make(4, "Collector's Cage", WindupAction(MultiAction([AddConditionAction("doom", 1, "player"), AddConditionAction("encase", 4, "player")]), 1)),
  "Grasping Hand": Enemy.make(4, "Grasping Hand", AddConditionAction("slow", 1, "player")),
  "Cagemaster": Enemy.make(16, "Cagemaster", AddConditionAction("doom", 1, "player"),
                               entry=AddConditionAction("encase", 16, "player")),
  "Specimen Collector": Enemy.make(20, "Specimen Collector", EnergyThresholdAction(AttackAction(10), NothingAction(), 1)),
  "Magecatcher": Enemy.make(20, "Magecatcher", SpellcastThresholdAction(
      AttackAction(10), AddConditionAction("slow", 1, "player"), 1)),
  "Doom of Blades": Enemy.make(40, "Doom of Blades", MultiAction([AttackAll(15), AttackAction(15)])),
  "Doom of Plagues": Enemy.make(40, "Doom of Plagues", AddConditionAction("poison", 2, "player"),
                           entry=AddConditionAction("poison", 5, "player")),
  "Wave of Doom": Enemy.make(15, "Wave of Doom", WindupAction(AttackAction(8), 1),
                         entry=AddConditionAction("retaliate", 1, "self")),
  "Horde Beast": Enemy.make(10, "Horde Beast", OverwhelmAction(AttackAction(8), AttackAction(4), 4)),
  "Blade Forger": Enemy.make(8, "Blade Forger", SideOverwhelmAction(
      NothingAction(), AddConditionAction("sharp", 2, "player"), 2)),
  "Wandering Healer": Enemy.make(8, "Wandering Healer", CautiousAction(NothingAction(),
      AddConditionAction("regen", 2, "player")), entry=AddConditionAction("regen", 2, "player")),
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

def make_enemy(name):
  return deepcopy(enemies[name])

doombringers = [
  # Doombringers
  EnemySet("Doom of Blades", [
    EnemySpawn(4, "b", make_enemy("Blade Forger")),
    EnemySpawn(6, "f", make_enemy("Doom of Blades")),
  ], faction="Doombringers", description="Late-spawning enemy that attacks everyone."),
  EnemySet("Doom of Plagues", [
    EnemySpawn(3, "b", make_enemy("Wandering Healer")),
    EnemySpawn(5, "f", make_enemy("Doom of Plagues")),
  ], faction="Doombringers", description="Late-spawning enemy that adds poison."),
  EnemySet("Doom of Waves", [
    EnemySpawn(3, "b", make_enemy("Defiant Survivor")),
    EnemySpawn(4, "f", make_enemy("Wave of Doom")),
    EnemySpawn(5, "f", make_enemy("Wave of Doom")),
    EnemySpawn(6, "f", make_enemy("Wave of Doom")),
  ], faction="Doombringers", description="3 late spawning enemies with slow attacks and retaliate."),
  EnemySet("Doom of Hordes", [
    EnemySpawn(4, "b", make_enemy("Grizzled Armorer")),
    EnemySpawn(6, "f", make_enemy("Horde Beast")),
    EnemySpawn(6, "f", make_enemy("Horde Beast")),
    EnemySpawn(6, "b", make_enemy("Horde Beast")),
    EnemySpawn(6, "b", make_enemy("Horde Beast")),
  ], faction="Doombringers", description="4 enemies that spawn all at once and have Overwhelm.")
]

the_collectors = [
  # The Collectors
  EnemySet("Cagemaster", [
    EnemySpawn(1, "b", make_enemy("Collector's Cage")),
    EnemySpawn(4, "f", make_enemy("Cagemaster")),
  ], faction="The Collectors", description="Encases and inflicts doom on you."),
  EnemySet("Specimen Collector", [
    EnemySpawn(1, "b", make_enemy("Inquisitive Eye")),
    EnemySpawn(4, "f", make_enemy("Specimen Collector")),
  ], faction="The Collectors", description="Attacks you if you have any energy."),
  EnemySet("Magecatcher", [
    EnemySpawn(1, "b", make_enemy("Grasping Hand")),
    EnemySpawn(4, "f", make_enemy("Magecatcher")),
  ], faction="The Collectors", description="Attacks you if you cast a spell."),
  EnemySet("Acquisitions Party", [
    EnemySpawn(1, "b", make_enemy("Inquisitive Eye")),
    EnemySpawn(1, "f", make_enemy("Inquisitive Eye")),
    EnemySpawn(2, "b", make_enemy("Collector's Cage")),
    EnemySpawn(2, "f", make_enemy("Collector's Cage")),
    EnemySpawn(3, "b", make_enemy("Grasping Hand")),
    EnemySpawn(3, "f", make_enemy("Grasping Hand"))
  ], faction="The Collectors", description="6 small minions that call enemies, slow you, and encase you.")
]

undying_legion = [
  # Undying Legion
  EnemySet("Relentless Legionnaire", [
    EnemySpawn(2, "f", make_enemy("Relentless Legionnaire")),
    EnemySpawn(3, "b", make_enemy("Relentless Legionnaire")),
    EnemySpawn(4, "f", make_enemy("Relentless Legionnaire"))
  ], faction="Undying Legion", description="3 enemies start with empower and undying."),
  EnemySet("Eternal Berserker", [
    EnemySpawn(1, "f", make_enemy("Eternal Berserker")),
  ], faction="Undying Legion", description="One enemy with lots of undying and regen"),
  EnemySet("Risen Warrior", [
    EnemySpawn(1, "b", make_enemy("Risen Warrior"))
  ], faction="Undying Legion", description="Starts encased, has heavy attacks."),
  EnemySet("Intrepid Bannerman", [
    EnemySpawn(3, "f", make_enemy("Conscript")),
    EnemySpawn(4, "f", make_enemy("Intrepid Bannerman"))
  ], faction="Undying Legion", description="Empowers enemies on its side.")
]

freed_automata = [
  # Freed Automata
  EnemySet("Assault Golem", [
    EnemySpawn(2, "f", make_enemy("Assault Golem"))
  ], faction="Freed Automata", description="Hits back hard if you attack it."),
  EnemySet("Aegis Orb", [
    EnemySpawn(1, "f", make_enemy("Aegis Orb"))
  ], faction="Freed Automata", description="Gives all enemies armor and retaliate."),
  EnemySet("Defective Shieldbot", [
    EnemySpawn(1, "f", make_enemy("Defective Shieldbot"))
  ], faction="Freed Automata", description="Starts with a large decaying shield."),
  EnemySet("Plated Warmech", [
    EnemySpawn(3, "f", make_enemy("Plated Warmech"))
  ], faction="Freed Automata", description="Very heavily armored."),
]

saik_collective = [
  # Sa'ik Collective
  EnemySet("Harpy Harriers", [
    EnemySpawn(1, "b", make_enemy("Harpy Harrier")),
    EnemySpawn(2, "f", make_enemy("Harpy Harrier")),
    EnemySpawn(3, "b", make_enemy("Harpy Harrier"))
  ], faction="Sa'ik Collective", description="Trio, they deal more damage from behind."),
  EnemySet("Evasive Skydancer", [
    EnemySpawn(2, "f", make_enemy("Evasive Skydancer"))
  ], faction="Sa'ik Collective", description="When attacked, doesn't attack, but gains sharp instead."),
  EnemySet("Sa'ik Descenders", [
    EnemySpawn(3, "f", make_enemy("Cocky Descender")),
    EnemySpawn(3, "b", make_enemy("Cocky Descender")),
  ], faction="Sa'ik Collective", description="High damage while at full health."),
  EnemySet("Screeching Fury", [
    EnemySpawn(3, "b", make_enemy("Screeching Fury")),
  ], faction="Sa'ik Collective", description="High damage while not at full health."),
]

house_of_imir = [
  # House of Imir
  EnemySet("Ravenous Hounds", [
    EnemySpawn(2, "f", make_enemy("Ravenous Hound")),
    EnemySpawn(3, "b", make_enemy("Ravenous Hound")),
    EnemySpawn(4, "f", make_enemy("Ravenous Hound"))
  ], faction="House of Imir", description="Trio, they deal more damage if you're surrounded."),
  EnemySet("Wanton Vampire", [
    EnemySpawn(3, "b", make_enemy("Bat")),
    EnemySpawn(4, "f", make_enemy("Vampire"))
  ], faction="House of Imir", description="Has a strong lifesteal attack."),
  EnemySet("Lurking Scavengers", [
    EnemySpawn(1, "b", make_enemy("Lurking Scavenger")),
    EnemySpawn(3, "b", make_enemy("Lurking Scavenger")),
    EnemySpawn(5, "b", make_enemy("Lurking Scavenger")),
  ], faction="House of Imir", description="Trio, if you're surrounded they lifesteal attack, otherwise they regen."),
  EnemySet("Vampire Lord", [
    EnemySpawn(3, "f", make_enemy("Vampire Lord")),
  ], faction="House of Imir", description="Starts damaged, can lifesteal. If you let him heal to full, he'll help you."),
]

movs_horde = [
  # Mov's Horde
  EnemySet("Zombie Mob", [
    EnemySpawn(3, "f", make_enemy("Zombie")),
    EnemySpawn(4, "f", make_enemy("Zombie")),
    EnemySpawn(5, "f", make_enemy("Zombie"))
  ], faction="Mov's Horde", description="Trio, first in line attacks you."),
  EnemySet("Decaying Corpse", [
    EnemySpawn(1, "f", make_enemy("Decaying Corpse"))
  ], faction="Mov's Horde", description="Early spawn, strong attacks, but starts poisoned."),
  EnemySet("Skittering Swarm", [
    EnemySpawn(1, "f", make_enemy("Skitterer")),
    EnemySpawn(2, "f", make_enemy("Skitterer")),
    EnemySpawn(3, "b", make_enemy("Skitterer")),
    EnemySpawn(4, "b", make_enemy("Skitterer")),
    EnemySpawn(5, "f", make_enemy("Skitterer")),
    EnemySpawn(5, "b", make_enemy("Skitterer")),
    EnemySpawn(6, "f", make_enemy("Skitterer")),
    EnemySpawn(6, "b", make_enemy("Skitterer")),
  ], faction="Mov's Horde", description="Swarm of low hp enemies. Attacks get stronger when many enemies present."),
  EnemySet("Necromancer Apprentice", [
    EnemySpawn(4, "f", make_enemy("Necromancer Apprentice")),
  ], faction="Mov's Horde", description="Gives enemies undying and regen."),
]

company_of_blades = [
  # Company of Blades
  EnemySet("Bandit Ambush", [
    EnemySpawn(2, "f", make_enemy("Bandit")),
    EnemySpawn(2, "b", make_enemy("Bandit"))
  ], faction="Company of Blades", description="Duo, they attack as long as there is a same or higher max hp enemy."),
  EnemySet("Hunter and Hawk", [
    EnemySpawn(3, "b", make_enemy("Hawk")),
    EnemySpawn(4, "f", make_enemy("Hunter"))
  ], faction="Company of Blades", description="Hawk inflicts vulnerable, hunter has heavy attacks from backline."),
  EnemySet("Insistent Duelist", [
    EnemySpawn(2, "f", make_enemy("Insistent Duelist"))
  ], faction="Company of Blades", description="Only attacks if he's alone on his side, otherwise powers up."),
  EnemySet("Crossbow Deadeyes", [
    EnemySpawn(2, "b", make_enemy("Crossbow Deadeye")),
    EnemySpawn(4, "f", make_enemy("Crossbow Deadeye")),
    EnemySpawn(6, "b", make_enemy("Crossbow Deadeye")),
  ], faction="Company of Blades", description="Trio, slow but heavy attacks."),
]

giantkin = [
  # Giantkin
  EnemySet("Charging Ogre", [
    EnemySpawn(4, "f", make_enemy("Charging Ogre"))
  ], faction="Giantkin", description="Charges to front and powers up, once in front does heavy attacks."),
  EnemySet("Injured Troll", [
    EnemySpawn(2, "f", make_enemy("Injured Troll"))
  ], faction="Giantkin", description="Starts damaged but with heavy regen."),
  EnemySet("Slumbering Giant", [
    EnemySpawn(1, "f", make_enemy("Slumbering Giant")),
  ], faction="Giantkin", description="High hp and massive attacks, but starts stunned."),
  EnemySet("The Executioner", [
    EnemySpawn(4, "b", make_enemy("Herald of Doom")),
    EnemySpawn(6, "f", make_enemy("The Executioner")),
  ], faction="Giantkin", description="Late spawning enemy with slow massive attacks."),
]

fae_realm = [
  # Fae Realm
  EnemySet("Faerie Assassins", [
    EnemySpawn(2, "b", make_enemy("Faerie Assassin")),
    EnemySpawn(4, "b", make_enemy("Faerie Assassin")),
    EnemySpawn(6, "b", make_enemy("Faerie Assassin")),
  ], faction="Fae Realm", description="Trio, poison you from behind, otherwise small attacks."),
  EnemySet("Midnight Court", [
      EnemySpawn(2, "f", make_enemy("Midnight Courtier")),
      EnemySpawn(3, "b", make_enemy("Midnight Courtier")),
  ], faction="Fae Realm", description="Duo, poison you if you have no energy, otherwise gain retaliate."),
  EnemySet("Fickle Witch-Queen", [
      EnemySpawn(2, "f", make_enemy("Fickle Witch-Queen"))
  ], faction="Fae Realm", description="Poisons you on entry. If you leave her be, she'll cure and heal you."),
  EnemySet("Tithetaker", [
      EnemySpawn(1, "b", make_enemy("Generous Sprite")),
      EnemySpawn(5, "f", make_enemy("Tithetaker"))
  ], faction="Fae Realm", description="Spawns late, does heavy attacks unless you have lots of energy."),
]

kingdom_of_amar = [
  # Kingdom of Amar
  EnemySet("Knifehand", [
    EnemySpawn(5, "f", make_enemy("Knifehand"))
  ], faction="Kingdom of Amar", description="Spawns late, does a triple attack."),
  EnemySet("Stoneguard Patrol", [
    EnemySpawn(3, "f", make_enemy("Stoneguard")),
    EnemySpawn(3, "f", make_enemy("Stoneguard")),
    EnemySpawn(5, "b", make_enemy("Stoneguard")),
    EnemySpawn(5, "b", make_enemy("Stoneguard")),
  ], faction="Kingdom of Amar", description="4 small enemies that start with armor."),
  EnemySet("Cloud of Daggers", [
    EnemySpawn(3, "f", make_enemy("Cloud of Daggers")),
    EnemySpawn(3, "b", make_enemy("Cloud of Daggers")),
  ], faction="Kingdom of Amar", description="Duo, multiple small attacks to everything."),
  EnemySet("Princess' Entourage", [
    EnemySpawn(2, "f", make_enemy("Stoneguard")),
    EnemySpawn(2, "f", make_enemy("Stoneguard")),
    EnemySpawn(5, "f", make_enemy("Artificer Princess")),
  ], faction="Kingdom of Amar", description="2 minions, 1 leader, she gives sharp to all."),
]

infernal_plane = [
  # Infernal Plane
  EnemySet("Blazing Eye", [
    EnemySpawn(3, "f", make_enemy("Blazing Eye"))
  ], faction="Infernal Plane", description="Inflicts heavy burn if you're facing it."),
  EnemySet("Conniving Impfiends", [
    EnemySpawn(4, "b", make_enemy("Conniving Impfiend")),
    EnemySpawn(4, "b", make_enemy("Conniving Impfiend")),
    EnemySpawn(4, "b", make_enemy("Conniving Impfiend")),
  ], faction="Infernal Plane", description="Trio, if you're Overwhelmed, they burn you, otherwise just attack."),
  EnemySet("Cult of the Inferno", [
    EnemySpawn(1, "b", make_enemy("Cultist")),
    EnemySpawn(2, "b", make_enemy("Cultist")),
    EnemySpawn(3, "b", make_enemy("Cultist")),
    EnemySpawn(11, "f", make_enemy("Demon of the Inferno")),
  ], faction="Infernal Plane", description="Trio of minions call the demon. If it spawns, you're probably dead."),
  EnemySet("Witch-Burner Devil", [
      EnemySpawn(2, "f", make_enemy("Witch-Burner Devil"))
  ], faction="Infernal Plane", description="If you have energy, inflicts heavy burn."),
]

dominion_of_drael = [
  # Dominion of Drael
  EnemySet("Zealous Battlemages", [
    EnemySpawn(1, "f", make_enemy("Zealous Battlemage")),
    EnemySpawn(2, "f", make_enemy("Zealous Battlemage")),
  ], faction="Dominion of Drael", description="Duo, start with heavy block and empower."),
  EnemySet("Draelish Patrol", [
    EnemySpawn(2, "f", make_enemy("Conscript")),
    EnemySpawn(3, "f", make_enemy("Conscript")),
    EnemySpawn(4, "f", make_enemy("Conscript")),
    EnemySpawn(5, "f", make_enemy("Draelish Captain"))
  ], faction="Dominion of Drael", description="Trio of minions, one leader that gives block and empower."),
  EnemySet("Draelish Bombsquad", [
    EnemySpawn(2, "f", make_enemy("Bomber Zealot")),
    EnemySpawn(4, "b", make_enemy("Bomber Zealot")),
  ], faction="Dominion of Drael", description="Duo, explode after one turn, damaging everything."),
  EnemySet("Shieldmage Squad", [
    EnemySpawn(3, "f", make_enemy("Grizzled Shieldmage")),
    EnemySpawn(4, "f", make_enemy("Grizzled Shieldmage")),
    EnemySpawn(5, "f", make_enemy("Grizzled Shieldmage")),
  ], faction="Dominion of Drael", description="Trio, give shield and retaliate to those in front."),
]

spirits = [
  # Spirits
  EnemySet("Lightning Elemental", [
    EnemySpawn(1, "f", make_enemy("Lightning Elemental"))
  ], faction="Spirits", description="Strong attacks, but they give you gold energy and empower."),
  EnemySet("Frost Elemental", [
    EnemySpawn(2, "f", make_enemy("Frost Elemental"))
  ], faction="Spirits", description="Inflicts slow, but gives you blue energy."),
  EnemySet("Fire Elemental", [
    EnemySpawn(3, "f", make_enemy("Fire Elemental"))
  ], faction="Spirits", description="Inflicts burn, but gives you red energy."),
  EnemySet("Font of Magic", [
      EnemySpawn(4, "f", make_enemy("Blue Spirit-Hunter")),
      EnemySpawn(4, "f", make_enemy("Red Spirit-Hunter")),
      EnemySpawn(4, "f", make_enemy("Gold Spirit-Hunter")),
      EnemySpawn(5, "b", make_enemy("Font of Magic"))
  ], faction="Spirits", description="Trio of minions who attack you if you have energy of their color."),
]

shadow_realm = [
  # Shadow Realm
  EnemySet("Creeping Shadow", [
    EnemySpawn(1, "b", make_enemy("Creeping Shadow"))
  ], faction="Shadow Realm", description="Grows stronger while you face away. Attacks when you face towards."),
  EnemySet("Nightmare Remnant", [
    EnemySpawn(2, "b", make_enemy("Nightmare Remnant")),
    EnemySpawn(2, "f", make_enemy("Nightmare Remnant")),
    EnemySpawn(3, "b", make_enemy("Nightmare Remnant")),
    EnemySpawn(3, "f", make_enemy("Nightmare Remnant")),
    EnemySpawn(4, "b", make_enemy("Nightmare Remnant")),
    EnemySpawn(4, "f", make_enemy("Nightmare Remnant")),
  ], faction="Shadow Realm", description="Disappear when you face them. Attack when you face away."),
  EnemySet("Dreamstalker", [
    EnemySpawn(3, "b", make_enemy("Dreamstalker"))
  ], faction="Shadow Realm", description="Slows you while you face away, otherwise attacks."),
  EnemySet("Shadow of a Doubt", [
    EnemySpawn(4, "b", make_enemy("Shadow of a Doubt"))
  ], faction="Shadow Realm", description="Inflicts vulnerable while you face towards, otherwise attacks."),
]

ancient_horrors = [
  # Ancient Horrors
  EnemySet("Vengeful Minefield", [
    EnemySpawn(1, "f", make_enemy("Vengeful Mine")),
    EnemySpawn(2, "b", make_enemy("Vengeful Mine")),
    EnemySpawn(3, "f", make_enemy("Vengeful Mine")),
    EnemySpawn(4, "b", make_enemy("Vengeful Mine")),
  ], faction="Ancient Horrors", description="Small enemies with retaliate. Explode when many are present."),
  EnemySet("Corrupting Spire", [
    EnemySpawn(2, "b", make_enemy("Incubated Fleshling")),
    EnemySpawn(3, "b", make_enemy("Incubated Fleshling")),
    EnemySpawn(4, "b", make_enemy("Incubated Fleshling")),
    EnemySpawn(5, "b", make_enemy("Corrupting Spire")),
  ], faction="Ancient Horrors", description="Trio of minions. All get empowered by the spire."),
  EnemySet("Mindless Maw", [
    EnemySpawn(4, "f", make_enemy("Mindless Maw")),
  ], faction="Ancient Horrors", description="Attacks whatever's in front of it and gets stronger every time."),
  EnemySet("The Vulture", [
    EnemySpawn(6, "b", make_enemy("The Vulture"))
  ], faction="Ancient Horrors", description="Consumes all enemies on entry, to strengthen itself."),
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
