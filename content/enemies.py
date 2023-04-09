from copy import deepcopy
from typing import List
from model.encounter import EnemySet, Enemy, EnemySpawn
from model.event import Event
from model.action import Action
from content.enemy_actions import (
  AttackAction, AttackSide, SelfDamageAction, AttackImmediate,
  BackstabAction, NearFarAction, PackTacticsAction, MoveAction, CowardlyAction,
  CallAction, MultiAction, WindupAction,
  NothingAction, CautiousAction, AddConditionAction, SetConditionAction,
  TheVultureEntryAction, OverwhelmAction, SideOverwhelmAction)

#

enemies = {
  "Harpy Harrier": Enemy(10, "Harpy Harrier", BackstabAction(AttackAction(4), AttackAction(2))),
  "Ravenous Hound": Enemy(10, "Ravenous Hound", PackTacticsAction(AttackAction(4), AttackAction(2))),
  "Zombie": Enemy(16, "Zombie", NearFarAction(AttackAction(6), MoveAction(-1))),
  "Bandit": Enemy(15, "Bandit", CowardlyAction(MoveAction(1), AttackAction(4))),
  "Bat": Enemy(3, "Bat", AttackAction(1)),
  "Vampire": Enemy(20, "Vampire", AttackAction(7, lifesteal=True)),
  "Hawk": Enemy(3, "Hawk", AddConditionAction("vulnerable", 1, "player"), entry=AddConditionAction("vulnerable", 1, "player")),
  "Hunter": Enemy(20, "Hunter", MultiAction([MoveAction(1), NearFarAction(AddConditionAction("armor", 1, "self"), AttackAction(10))])),
  "Charging Ogre": Enemy(30, "Charging Ogre", NearFarAction(AttackAction(8), MultiAction([MoveAction(-10), AddConditionAction("empower", 8, "self")]))),
  "Plated Drake": Enemy(15, "Plated Drake", CautiousAction(AddConditionAction("sharp", 2, "self"), AttackAction(5)), entry=AddConditionAction("enduring", 5, "self")),
  "The Vulture": Enemy(30, "The Vulture", AttackAction(2), entry=TheVultureEntryAction()),
  #
  "Skitterer": Enemy(3, "Skitterer", OverwhelmAction(AttackAction(2), AttackAction(1), 3)),
  "Decaying Corpse": Enemy(20, "Decaying Corpse", AttackAction(6), entry=AddConditionAction("poison", 4, "self")),
  "Faerie Assassin": Enemy(6, "Faerie Assassin", BackstabAction(AddConditionAction("poison", 2, "player"), AttackAction(3))),
  "Knifehand": Enemy(20, "Knifehand", MultiAction([AttackAction(4), AttackAction(5), AttackAction(6)])),
  "Blazing Eye": Enemy(16, "Blazing Eye", BackstabAction(AddConditionAction("burn", 1, "player"), AddConditionAction("burn", 5, "player"))),
  "Creeping Shadow": Enemy(10, "Creeping Shadow", BackstabAction(AddConditionAction("sharp", 5, "self"), AttackAction(1)), entry=AddConditionAction("enduring", 2, "self"), exp=10),
  "Stoneguard": Enemy(6, "Stoneguard", AttackAction(3), entry=AddConditionAction("armor", 3, "self")),
  "Conniving Impfiend": Enemy(5, "Conniving Impfiend", OverwhelmAction(AddConditionAction("burn", 2, "player"), AttackAction(2), 3)),
  "Insistent Duelist": Enemy(20, "Insistent Duelist",
                              SideOverwhelmAction(
                                MultiAction([AddConditionAction("sharp", 1, "self"), AddConditionAction("armor", 1, "self")]),
                                MultiAction([SetConditionAction("armor", 0, "self"), AttackAction(4), AttackAction(4)]), 2
                              ), entry=AddConditionAction("ward", 1, "player")),
  "Cultist": Enemy(10, "Cultist", CallAction("Demon of the Inferno", 1), entry=AddConditionAction("burn", 4, "self"), exp=3),
  "Demon of the Inferno": Enemy(66, "Demon of the Inferno", AttackAction(13, lifesteal=True), entry=AddConditionAction("burn", 6, "player")),
  "Injured Troll": Enemy(35, "Injured Troll", AttackAction(4), entry=MultiAction([SelfDamageAction(15), AddConditionAction("regen", 5, "self")]), exp=14),
  "Crossbow Deadeye": Enemy(12, "Crossbow Deadeye", WindupAction(AttackAction(10), 1)),
  "Herald of Doom": Enemy(5, "Herald of Doom", SelfDamageAction(5)),
  "The Executioner": Enemy(40, "The Executioner", WindupAction(AttackAction(25), 1)),
  "Cloud of Daggers": Enemy(6, "Cloud of Daggers",
                            MultiAction([AttackAction(2), AttackAction(2), AttackAction(2),
                                        AttackSide(1), AttackSide(1), AttackSide(1)]),
                            entry=AddConditionAction("durable", 3, "self"), exp=6),
  "Slumbering Giant": Enemy(45, "Slumbering Giant", AttackAction(20), entry=AddConditionAction("stun", 4, "self")),
  "Mindless Maw": Enemy(50, "Mindless Maw", MultiAction([AttackImmediate(5, lifesteal=True), AddConditionAction("sharp", 5, "self")]), entry=SelfDamageAction(30), exp=20),
  "Shaman of Withering": Enemy(12, "Shaman of Withering", AddConditionAction("poison", 1, "all"), entry=AddConditionAction("poison", 2, "all")),
  "Shaman of Rebirth": Enemy(12, "Shaman of Rebirth", AddConditionAction("regen", 2, "all"), entry=AddConditionAction("regen", 3, "all_enemies")),
  "Zealous Battlemage": Enemy(8, "Zealous Battlemage", AttackAction(1), entry=MultiAction([AddConditionAction("block", 8, "self"), AddConditionAction("empower", 8, "self")])),
  "Draelish Captain": Enemy(7, "Draelish Captain", AttackAction(0), entry=MultiAction([AddConditionAction("block", 4, "all_enemies"), AddConditionAction("empower", 4, "all_enemies")])),
  "Conscript": Enemy(6, "Conscript", CowardlyAction(NothingAction(), AttackAction(2), hp_threshold=7)),
  # "Misfiring Automaton": Enemy(16, "Misfiring Automaton", WindupAction(AttackSide(6)), entry=MultiAction(AddConditionAction("armor", 2, "self"), AddConditionAction("retaliate", 2, "self"))),
  # enemy that rewards you for full blocking its attacks
  # another 1-turn spawn enemy
  # elder one
  # energy vampire -- rylie ellam
  # enemies where damage is not the best option
  # enemies that make doing defense survival mode fun and feel powerful
  # 4 armor 12 hp
  # another backstab enemy?
}

enemy_sets = [
  EnemySet("Harpy Harriers", [
    EnemySpawn(1, "b", enemies["Harpy Harrier"]),
    EnemySpawn(2, "f", enemies["Harpy Harrier"]),
    EnemySpawn(3, "b", enemies["Harpy Harrier"])
  ]),
  EnemySet("Ravenous Hounds", [
    EnemySpawn(2, "f", enemies["Ravenous Hound"]),
    EnemySpawn(3, "b", enemies["Ravenous Hound"]),
    EnemySpawn(4, "f", enemies["Ravenous Hound"])
  ]),
  EnemySet("Zombie Mob", [
    EnemySpawn(3, "f", enemies["Zombie"]),
    EnemySpawn(4, "f", enemies["Zombie"]),
    EnemySpawn(5, "f", enemies["Zombie"])
  ]),
  EnemySet("Bandit Ambush", [
    EnemySpawn(2, "f", enemies["Bandit"]),
    EnemySpawn(2, "b", enemies["Bandit"])
  ]),
  EnemySet("Hunter and Hawk", [
    EnemySpawn(3, "b", enemies["Hawk"]),
    EnemySpawn(4, "f", enemies["Hunter"])
  ]),
  EnemySet("Wanton Vampire", [
    EnemySpawn(3, "b", enemies["Bat"]),
    EnemySpawn(4, "f", enemies["Vampire"])
  ]),
  EnemySet("Plated Drake", [
    EnemySpawn(2, "f", enemies["Plated Drake"])
  ]),
  EnemySet("The Vulture", [
    EnemySpawn(6, "b", enemies["The Vulture"])
  ]),
  EnemySet("Charging Ogre", [
    EnemySpawn(4, "f", enemies["Charging Ogre"])
  ]),
  #
  EnemySet("Skittering Swarm", [
    EnemySpawn(1, "f", enemies["Skitterer"]),
    EnemySpawn(2, "f", enemies["Skitterer"]),
    EnemySpawn(3, "b", enemies["Skitterer"]),
    EnemySpawn(4, "b", enemies["Skitterer"]),
    EnemySpawn(5, "f", enemies["Skitterer"]),
    EnemySpawn(6, "b", enemies["Skitterer"]),
  ]),
  EnemySet("Decaying Corpse", [
    EnemySpawn(1, "f", enemies["Decaying Corpse"])
  ]),
  EnemySet("Faerie Assassins", [
    EnemySpawn(2, "b", enemies["Faerie Assassin"]),
    EnemySpawn(4, "b", enemies["Faerie Assassin"]),
  ]),
  EnemySet("Knifehand", [
    EnemySpawn(5, "f", enemies["Knifehand"])
  ]),
  EnemySet("Blazing Eye", [
    EnemySpawn(3, "f", enemies["Blazing Eye"])
  ]),
  EnemySet("Creeping Shadow", [
    EnemySpawn(1, "b", enemies["Creeping Shadow"])
  ]),
  EnemySet("Stoneguard Patrol", [
    EnemySpawn(3, "f", enemies["Stoneguard"]),
    EnemySpawn(3, "f", enemies["Stoneguard"]),
    EnemySpawn(5, "b", enemies["Stoneguard"]),
    EnemySpawn(5, "b", enemies["Stoneguard"]),
  ]),
  EnemySet("Insistent Duelist", [
    EnemySpawn(2, "f", enemies["Insistent Duelist"])
  ]),
  EnemySet("Injured Troll", [
    EnemySpawn(2, "f", enemies["Injured Troll"])
  ]),
  EnemySet("Conniving Impfiends", [
    EnemySpawn(4, "b", enemies["Conniving Impfiend"]),
    EnemySpawn(4, "b", enemies["Conniving Impfiend"]),
    EnemySpawn(4, "b", enemies["Conniving Impfiend"]),
  ]),
  EnemySet("Cult of the Inferno", [
    EnemySpawn(1, "b", enemies["Cultist"]),
    EnemySpawn(2, "b", enemies["Cultist"]),
    EnemySpawn(3, "b", enemies["Cultist"]),
    EnemySpawn(11, "f", enemies["Demon of the Inferno"]),
  ]),
  EnemySet("Crossbow Deadeyes", [
    EnemySpawn(2, "b", enemies["Crossbow Deadeye"]),
    EnemySpawn(4, "f", enemies["Crossbow Deadeye"]),
    EnemySpawn(6, "b", enemies["Crossbow Deadeye"]),
  ]),
  EnemySet("The Execution", [
    EnemySpawn(4, "b", enemies["Herald of Doom"]),
    EnemySpawn(6, "f", enemies["The Executioner"]),
  ]),
  EnemySet("Cloud of Daggers", [
    EnemySpawn(3, "f", enemies["Cloud of Daggers"]),
    EnemySpawn(3, "b", enemies["Cloud of Daggers"]),
  ]),
  EnemySet("Slumbering Giant", [
    EnemySpawn(1, "f", enemies["Slumbering Giant"]),
  ]),
  EnemySet("Mindless Maw", [
    EnemySpawn(4, "f", enemies["Mindless Maw"]),
  ]),
  EnemySet("Shamans of the Cycle", [
    EnemySpawn(3, "b", enemies["Shaman of Withering"]),
    EnemySpawn(5, "f", enemies["Shaman of Rebirth"]),
  ]),
  EnemySet("Zealous Battlemages", [
    EnemySpawn(1, "f", enemies["Zealous Battlemage"]),
    EnemySpawn(2, "f", enemies["Zealous Battlemage"]),
  ]),
  EnemySet("Draelish Patrol", [
    EnemySpawn(3, "f", enemies["Conscript"]),
    EnemySpawn(4, "f", enemies["Conscript"]),
    EnemySpawn(5, "f", enemies["Draelish Captain"])
  ]),
  # EnemySet("Vengeful Mites", [
  #   EnemySpawn(1, "b")

]
