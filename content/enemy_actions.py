from typing import List, Literal
from model.event import Event
from model.action import Action

# Event functions

def move_enemy(actor, encounter, movement):
  if actor.side(encounter) == "back":
    enemy_queue = encounter.back
  elif actor.side(encounter) == "front":
    enemy_queue = encounter.front
  else:
    raise ValueError(f"Cannot perform move action when enemy {actor.name} has no side info.")
  
  from_idx = actor.position(encounter)
  to_idx = max(actor.position(encounter) + movement, 0)
  enemy_queue.insert(to_idx, enemy_queue.pop(from_idx))

def change_time_spawn(source, enemy_spawn, time_change):
  enemy_spawn.turn += time_change

# Basic Actions

class NothingAction(Action):
  def act(self, actor, enc):
    return []

class SelfDamageAction(Action):
  def __init__(self, damage):
    self.damage = damage

  def act(self, actor, enc) -> List[Event]:
    events = [Event(["assign_damage"], self, actor, lambda s, t: t.assign_damage(self.damage))]
    return events

class AttackAction(Action):
  def __init__(self, damage):
    self.damage = damage

  def act(self, actor, enc) -> List[Event]:
    events = [Event(["assign_damage"], actor, enc.player, lambda a, t: a.attack(t, self.damage))]
    return events

class LifestealAttack(Action):
  def __init__(self, damage):
    self.damage = damage

  def act(self, actor, enc) -> List[Event]:
    events = [Event(["assign_damage"], actor, enc.player, lambda a, t: a.heal(t.assign_damage(self.damage)))]
    return events

class MoveAction(Action):
  def __init__(self, movement):
    self.movement = movement

  def act(self, actor, enc) -> List[Event]:
    events = [Event(["move"], actor, enc, lambda a, e: move_enemy(a, e, self.movement))]
    return events

class CallAction(Action):
  def __init__(self, call_name, call_amount):
    self.call_name = call_name
    self.call_amount = call_amount

  def act(self, actor, enc):
    name_match = [es for es in enc.enemy_spawns
                          if es.enemy.name == self.call_name]
    if name_match:
      enemy_spawn = name_match[0]
      events = [Event(["call"], actor, enemy_spawn, lambda a, es: change_time_spawn(a, es, -1*self.call_amount))]
      return events
    else:
      return []

class AddConditionAction(Action):
  def __init__(self, condition, magnitude, target: Literal["self", "player"]):
    self.condition = condition
    self.magnitude = magnitude
    self.target = target

  def act(self, actor, enc):
    if self.target == "player":
      def event_func(actor, encounter):
        current_magnitude = encounter.player.conditions[self.condition] or 0
        encounter.player.conditions[self.condition] = current_magnitude + self.magnitude
    elif self.target == "self":
      def event_func(actor, encounter):
        current_magnitude = actor.conditions[self.condition] or 0
        actor.conditions[self.condition] = current_magnitude + self.magnitude
    else:
      raise ValueError(f"{self.target} is not a valid target...")

    events = [Event(["condition"], actor, enc, event_func)]
    return events

class SetConditionAction(Action):
  def __init__(self, condition, magnitude, target: Literal["self", "player"]):
    self.condition = condition
    self.magnitude = magnitude
    self.target = target

  def act(self, actor, enc):
    if self.target == "player":
      def event_func(actor, encounter):
        encounter.player.conditions[self.condition] = self.magnitude
    elif self.target == "self":
      def event_func(actor, encounter):
        actor.conditions[self.condition] = self.magnitude
    else:
      raise ValueError(f"{self.target} is not a valid target...")

    events = [Event(["condition"], actor, enc, event_func)]
    return events


# Branching Actions

class WindupAction(Action):
  def __init__(self, payoff_action, windup):
    self.payoff_action = payoff_action
    self.windup = windup

  def act(self, actor, enc) -> List[Event]:
    if actor.conditions["charge"] < self.windup:
      actor.conditions["charge"] += 1
      return []
    else:
      actor.conditions["charge"] = 0
      return self.payoff_action.act(actor, enc)

class BackstabAction(Action):
  def __init__(self, backstab_action, non_backstab_action):
    self.backstab_action = backstab_action
    self.non_backstab_action = non_backstab_action

  def act(self, actor, enc) -> List[Event]:
    enc.update_enemy_self_knowledge()
    if (enc.player.facing != actor.side(enc)):
      return self.backstab_action.act(actor, enc)
    else:
      return self.non_backstab_action.act(actor, enc)

class PackTacticsAction(Action):
  def __init__(self, pack_action, non_pack_action):
    self.pack_action = pack_action
    self.non_pack_action = non_pack_action

  def act(self, actor, enc) -> Event:
    enc.update_enemy_self_knowledge()
    if (actor.side(enc) == "back" and enc.front) or (actor.side(enc) == "front" and enc.back):
      return self.pack_action.act(actor, enc)
    else:
      return self.non_pack_action.act(actor, enc)

class NearFarAction(Action):
  def __init__(self, near_action, far_action):
    self.near_action = near_action
    self.far_action = far_action

  def act(self, actor, enc) -> Event:
    enc.update_enemy_self_knowledge()
    print(f"-------- {actor.name} current position is {actor.position(enc)}")
    if actor.position(enc) == 0:
      return self.near_action.act(actor, enc)
    else:
      return self.far_action.act(actor, enc)

class CowardlyAction(Action):
  def __init__(self, cowardly_action, non_cowardly_action):
    self.cowardly_action = cowardly_action
    self.non_cowardly_action = non_cowardly_action

  def act(self, actor, enc) -> List[Event]:
    if any(True for enemy in enc.all_other_enemies(actor) if enemy.max_hp >= actor.max_hp):
      print(f"Not Cowardly!")
      return self.non_cowardly_action.act(actor, enc)
    else:
      print(f"Cowardly!")
      return self.cowardly_action.act(actor, enc)

class CautiousAction(Action):
  def __init__(self, cautious_action, non_cautious_action):
    self.cautious_action = cautious_action
    self.non_cautious_action = non_cautious_action

  def act(self, actor, enc) -> List[Event]:
    if actor.damage_taken_this_turn > 0:
      return self.cautious_action.act(actor, enc)
    else:
      return self.non_cautious_action.act(actor, enc)

class OverwhelmAction(Action):
  def __init__(self, overwhelm_action, non_overwhelm_action, threshold):
    self.overwhelm_action = overwhelm_action
    self.non_overwhelm_action = non_overwhelm_action
    self.threshold = threshold

  def act(self, actor, enc) -> List[Event]:
    if len(enc.enemies) >= self.threshold:
      return self.overwhelm_action.act(actor, enc)
    else:
      return self.non_overwhelm_action.act(actor, enc)

class SideOverwhelmAction(Action):
  def __init__(self, overwhelm_action, non_overwhelm_action, threshold):
    self.overwhelm_action = overwhelm_action
    self.non_overwhelm_action = non_overwhelm_action
    self.threshold = threshold

  def act(self, actor, enc) -> List[Event]:
    side = enc.get_containing_side_queue(actor)
    if len(side) >= self.threshold:
      return self.overwhelm_action.act(actor, enc)
    else:
      return self.non_overwhelm_action.act(actor, enc)

# Multi Actions

class MultiAction(Action):
  def __init__(self, action_list):
    self.action_list = action_list

  def act(self, actor, enc) -> List[Event]:
    events = []
    for action in self.action_list:
      events += action.act(actor, enc)
    return events

# Enemy-specific Actions

class TheVultureEntryAction(Action):
  def act(self, actor, enc) -> List[Event]:
    other_enemies = enc.all_other_enemies(actor)
    total_sacrificed_health = 0
    events = []
    for enemy in other_enemies:
      total_sacrificed_health += enemy.hp
      events.append(Event(["enemy_death"], enemy, enc, lambda a, e: e.move_to_grave(a)))
    
    events += AttackAction(len(other_enemies) * 2).act(actor, enc)
    events += AddConditionAction("sharp", int(total_sacrificed_health / 2), "self").act(actor, enc)
    return events