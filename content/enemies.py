from copy import deepcopy
from typing import List
from model.encounter import EnemySet, Enemy, EnemySpawn
from model.event import Event
from model.action import Action
from content.enemy_actions import (
  AttackAction, BackstabAction, NearFarAction,
  PackTacticsAction, MoveAction, CowardlyAction,
  LifestealAttack, CallAction, MultiAction,
  NothingAction, CautiousAction, AddConditionAction,
  TheVultureEntryAction, OverwhelmAction)

#

enemies = {
  "Harpy Harrier": Enemy(10, "Harpy Harrier", BackstabAction(AttackAction(4), AttackAction(2))),
  "Ravenous Hound": Enemy(12, "Ravenous Hound", PackTacticsAction(AttackAction(5), AttackAction(3))),
  "Zombie": Enemy(15, "Zombie", NearFarAction(AttackAction(6), MoveAction(-1))),
  "Bandit": Enemy(15, "Bandit", CowardlyAction(MoveAction(1), AttackAction(4))),
  "Bat": Enemy(3, "Bat", AttackAction(1)),
  "Vampire": Enemy(20, "Vampire", LifestealAttack(7)),
  "Hawk": Enemy(3, "Hawk", CallAction("Hunter", 1)),
  "Hunter": Enemy(25, "Hunter", MultiAction([MoveAction(1), NearFarAction(AddConditionAction("armor", 1, "self"), AttackAction(10))])),
  "Charging Ogre": Enemy(30, "Charging Ogre", NearFarAction(AttackAction(8), MultiAction([MoveAction(-10), AddConditionAction("empower", 8, "self")]))),
  "Plated Drake": Enemy(15, "Plated Drake", CautiousAction(AddConditionAction("sharp", 1, "self"), AttackAction(5)), entry=AddConditionAction("durable", 5, "self")),
  "The Vulture": Enemy(30, "The Vulture", AttackAction(2), entry=TheVultureEntryAction()),
  #
  "Skitterer": Enemy(3, "Skitterer", OverwhelmAction(AttackAction(2), AttackAction(1))),
  "Dying Ghast": Enemy(20, "Dying Ghast", AttackAction(6), entry=AddConditionAction("poison", 5, "self")),
  "Faerie Assassin": Enemy(6, "Faerie Assassin", BackstabAction(AddConditionAction("poison", 2, "player"), AttackAction(3))),
  "Knifehand": Enemy(20, "Knifehand", MultiAction([AttackAction(4), AttackAction(5), AttackAction(6)])),
  "Blazing Eye": Enemy(16, "Blazing Eye", BackstabAction(AddConditionAction("burn", 1, "player"), AddConditionAction("burn", 5, "player"))),
  "Creeping Shadow": Enemy(10, "Creeping Shadow", BackstabAction(AddConditionAction("sharp", 3, "self"), AttackAction(1)), entry=AddConditionAction("durable", 2, "self")),
  "Stoneguard": Enemy(6, "Stoneguard", AttackAction(4), entry=AddConditionAction("armor", 3, "self")),
  # burst of 3 enemies, start out overwhelm...
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
    EnemySpawn(1, "b", enemies["Hawk"]),
    EnemySpawn(5, "f", enemies["Hunter"])
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
  EnemySet("Dying Ghast", [
    EnemySpawn(1, "f", enemies["Dying Ghast"])
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
]
