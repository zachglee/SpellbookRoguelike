from typing import List, Literal
from model.event import Event
from model.action import Action
from utils import energy_colors

# Event functions

def move_enemy(actor, encounter, movement):
  enemy_queue = actor.side_queue(encounter)

  from_idx = actor.position(encounter)
  to_idx = max(actor.position(encounter) + movement, 0)
  enemy_queue.insert(to_idx, enemy_queue.pop(from_idx))

def change_time_spawn(source, enemy_spawn, time_change):
  enemy_spawn.turn += time_change

# Basic Actions

class NothingAction(Action):
  def act(self, actor, enc):
    return []
  
  def __repr__(self):
    return f"..."

class SelfDamageAction(Action):
  def __init__(self, damage):
    self.damage = damage

  def act(self, actor, enc) -> List[Event]:
    events = [Event(["assign_damage"], actor, actor, lambda s, t: t.assign_damage(self.damage))]
    return events

  def __repr__(self):
    return f"Deal {self.damage} to self"

class AttackAction(Action):
  def __init__(self, damage, lifesteal=False):
    self.damage = damage
    self.lifesteal = lifesteal

  def act(self, actor, enc) -> List[Event]:
    events = [Event(["assign_damage"], actor, enc.player,
                    lambda a, t: a.attack(t, self.damage, lifesteal=self.lifesteal))]
    return events
  
  def __repr__(self):
    return f"{'Lifesteal ' if self.lifesteal else ''}Attack {self.damage}"
  
class AttackImmediate(Action):
  def __init__(self, damage, lifesteal=False):
    self.damage = damage
    self.lifesteal = lifesteal
  
  def act(self, actor, enc) -> List[Event]:
    events = [Event(["assign_damage"], actor, actor.get_immediate(enc),
                    lambda a, t: a.attack(t, self.damage, lifesteal=self.lifesteal))]
    return events
  
  def __repr__(self):
    return f"{'Lifesteal ' if self.lifesteal else ''}Attack {self.damage} to immediate"

class AttackSide(Action):
  def __init__(self, damage, lifesteal=False):
    self.damage = damage
    self.lifesteal = lifesteal

  def act(self, actor, enc) -> List[Event]:
    targets = actor.side_queue(enc)
    targets = [t for t in targets if t != actor]
    events = [Event(["assign_damage"], actor, target,
              lambda a, t: a.attack(t, self.damage, lifesteal=self.lifesteal))
              for target in targets]
    return events

  def __repr__(self):
    return f"{'Lifesteal ' if self.lifesteal else ''}Attack {self.damage} to side"
  
class AttackAll(Action):
  def __init__(self, damage, lifesteal=False):
    self.damage = damage
    self.lifesteal = lifesteal

  def act(self, actor, enc) -> List[Event]:
    targets = enc.enemies
    targets = [t for t in targets]
    events = [Event(["assign_damage"], actor, target,
              lambda a, t: a.attack(t, self.damage, lifesteal=self.lifesteal))
              for target in targets]
    return events
  
  def __repr__(self):
    return f"{'Lifesteal ' if self.lifesteal else ''}Attack {self.damage} to all"

class HealAction(Action):
  def __init__(self, magnitude, target):
    self.magnitude = magnitude
    self.target = target
  
  def act(self, actor, enc) -> List[Event]:
    def event_func_factory(combat_entity):
      def event_func(actor, encounter):
        combat_entity.heal(self.magnitude)
      return event_func

    if self.target == "player":
      return [Event(["condition"], actor, enc, event_func_factory(enc.player))]
    elif self.target == "self":
      return [Event(["condition"], actor, enc, event_func_factory(actor))]
    elif self.target == "all_enemies":
      return [Event(["condition"], actor, enc, event_func_factory(enemy)) for enemy in enc.enemies]
    elif self.target == "all":
      return [Event(["condition"], actor, enc, event_func_factory(ce)) for ce in enc.enemies + [enc.player]]
    elif self.target == "immediate":
      return [Event(["condition"], actor, enc, event_func_factory(actor.get_immediate(enc)))]
    elif self.target == "side":
      return [Event(["condition"], actor, enc, event_func_factory(enemy)) for enemy in actor.side_queue(enc)]
    else:
      raise ValueError(f"{self.target} is not a valid target...")
    
  def __repr__(self):
    return f"Heal {self.target} for {self.magnitude}"

class MoveAction(Action):
  def __init__(self, movement):
    self.movement = movement

  def act(self, actor, enc) -> List[Event]:
    events = [Event(["move"], actor, enc, lambda a, e: move_enemy(a, e, self.movement))]
    return events

  def __repr__(self):
    return f"Move {self.movement}"

class CallAction(Action):
  def __init__(self, call_name, call_amount):
    self.call_name = call_name
    self.call_amount = call_amount

  def act(self, actor, enc):
    if self.call_name is None:
      return [Event(["call"], actor, enc, lambda a, enc: enc.call(self.call_amount))]

    name_match = [es for es in enc.enemy_spawns
                          if es.enemy.name == self.call_name]
    if name_match:
      enemy_spawn = name_match[0]
      events = [Event(["call"], actor, enemy_spawn, lambda a, es: change_time_spawn(a, es, -1*self.call_amount))]
      return events
    else:
      return []
  
  def __repr__(self):
    return f"Call {self.call_name if self.call_name else 'next enemy'} {self.call_amount}"

class AddConditionAction(Action):
  def __init__(self, condition, magnitude, target: Literal["self", "player", "all_enemies", "all", "immediate", "side"]):
    self.condition = condition
    self.magnitude = magnitude
    self.target = target

  def act(self, actor, enc):
    def event_func_factory(combat_entity):
      def event_func(actor, encounter):
        current_magnitude = combat_entity.conditions[self.condition] or 0
        combat_entity.conditions[self.condition] = current_magnitude + self.magnitude
      return event_func

    if self.target == "player":
      return [Event(["condition"], actor, enc, event_func_factory(enc.player))]
    elif self.target == "self":
      return [Event(["condition"], actor, enc, event_func_factory(actor))]
    elif self.target == "all_enemies":
      return [Event(["condition"], actor, enc, event_func_factory(enemy)) for enemy in enc.enemies]
    elif self.target == "all":
      return [Event(["condition"], actor, enc, event_func_factory(ce)) for ce in enc.enemies + [enc.player]]
    elif self.target == "immediate":
      return [Event(["condition"], actor, enc, event_func_factory(actor.get_immediate(enc)))]
    elif self.target == "side":
      return [Event(["condition"], actor, enc, event_func_factory(enemy)) for enemy in actor.side_queue(enc)]
    else:
      raise ValueError(f"{self.target} is not a valid target...")
    
  def __repr__(self):
    return f"Add {self.magnitude} {self.condition} to {self.target}"

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

  def __repr__(self):
    return f"Set {self.condition} to {self.magnitude} on {self.target}"


# Branching Actions

class WindupAction(Action):
  def __init__(self, payoff_action, windup, windup_action=NothingAction()):
    self.payoff_action = payoff_action
    self.windup_action = windup_action
    self.windup = windup

  def act(self, actor, enc) -> List[Event]:
    if actor.conditions["charge"] < self.windup:
      actor.conditions["charge"] += 1
      return self.windup_action.act(actor, enc)
    else:
      actor.conditions["charge"] = 0
      return self.payoff_action.act(actor, enc)
    
  def __repr__(self):
    return f"Charge up for {self.windup} turns, then: {self.payoff_action}"

class HealthThresholdAction(Action):
  def __init__(self, meet_threshold_action, below_threshold_action, threshold):
    self.meet_threshold_action = meet_threshold_action
    self.below_threshold_action = below_threshold_action
    self.threshold = threshold

  def act(self, actor, enc) -> List[Event]:
    if self.threshold <= 1 and (actor.hp / actor.max_hp) >= self.threshold:
      # if threshold is less than 1 it's a proportion of max hp
      return self.meet_threshold_action.act(actor, enc)
    elif self.threshold > 1 and actor.hp >= self.threshold:
      # if threshold is greater than 1 it's a raw hp value
      return self.meet_threshold_action.act(actor, enc)
    else:
      return self.below_threshold_action.act(actor, enc)
  
  def __repr__(self):
    threshold_part = f"{self.threshold} hp" if self.threshold > 1 else f"{self.threshold * 100}% hp"
    return f"If below {threshold_part}: {self.below_threshold_action} else {self.meet_threshold_action}"

class EnergyThresholdAction(Action):
  def __init__(self, meet_threshold_action, below_threshold_action, threshold,
               colors=energy_colors):
    self.meet_threshold_action = meet_threshold_action
    self.below_threshold_action = below_threshold_action
    self.threshold = threshold
    self.colors = colors
  
  def act(self, actor, enc) -> List[Event]:
    if enc.player.total_energy(colors=self.colors) >= self.threshold:
      return self.meet_threshold_action.act(actor, enc)
    else:
      return self.below_threshold_action.act(actor, enc)
    
  def __repr__(self):
    return f"If you have >= {self.threshold} [{', '.join(self.colors)}]: {self.meet_threshold_action} else {self.below_threshold_action}"

class SpellcastThresholdAction(Action):
  def __init__(self, meet_threshold_action, below_threshold_action, threshold):
    self.meet_threshold_action = meet_threshold_action
    self.below_threshold_action = below_threshold_action
    self.threshold = threshold
  
  def act(self, actor, enc) -> List[Event]:
    if len(enc.spells_cast_this_turn) >= self.threshold:
      return self.meet_threshold_action.act(actor, enc)
    else:
      return self.below_threshold_action.act(actor, enc)
    
  def __repr__(self):
    return f"If player cast >= {self.threshold} spells this turn: {self.meet_threshold_action} else {self.below_threshold_action}"

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

  def __repr__(self):
    return f"If player facing away: {self.backstab_action} else {self.non_backstab_action}"

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
    
  def __repr__(self):
    return f"If surrounded: {self.pack_action} else {self.non_pack_action}"

class NearFarAction(Action):
  def __init__(self, near_action, far_action):
    self.near_action = near_action
    self.far_action = far_action

  def act(self, actor, enc) -> Event:
    enc.update_enemy_self_knowledge()
    if actor.position(enc) == 0:
      return self.near_action.act(actor, enc)
    else:
      return self.far_action.act(actor, enc)
    
  def __repr__(self):
    return f"If near: {self.near_action} else {self.far_action}"

class CowardlyAction(Action):
  def __init__(self, cowardly_action, non_cowardly_action, hp_threshold=None):
    self.cowardly_action = cowardly_action
    self.non_cowardly_action = non_cowardly_action
    self.hp_threshold = hp_threshold

  def act(self, actor, enc) -> List[Event]:
    hp_threshold = self.hp_threshold or actor.max_hp
    if any(True for enemy in enc.all_other_enemies(actor) if enemy.max_hp >= hp_threshold):
      print(f"Not Cowardly!")
      return self.non_cowardly_action.act(actor, enc)
    else:
      print(f"Cowardly!")
      return self.cowardly_action.act(actor, enc)

  def __repr__(self):
    return f"If there is another enemy with max hp >= {self.hp_threshold}: {self.non_cowardly_action} else {self.cowardly_action}"

class CautiousAction(Action):
  def __init__(self, cautious_action, non_cautious_action):
    self.cautious_action = cautious_action
    self.non_cautious_action = non_cautious_action

  def act(self, actor, enc) -> List[Event]:
    if actor.damage_taken_this_turn > 0:
      return self.cautious_action.act(actor, enc)
    else:
      return self.non_cautious_action.act(actor, enc)
  
  def __repr__(self):
    return f"If took damage this turn: {self.cautious_action} else {self.non_cautious_action}"

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
  
  def __repr__(self):
    return f"If >= {self.threshold} enemies present: {self.overwhelm_action} else {self.non_overwhelm_action}"

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
  
  def __repr__(self):
    return f"If >= {self.threshold} enemies on this side: {self.overwhelm_action} else {self.non_overwhelm_action}"

# Multi Actions

class MultiAction(Action):
  def __init__(self, action_list):
    self.action_list = action_list

  @property
  def non_undying_action_list(self):
    return [action for action in self.action_list if not involves_add_undying(action)]

  def act(self, actor, enc) -> List[Event]:
    events = []
    for action in self.action_list:
      events += action.act(actor, enc)
    return events
  
  def __repr__(self):
    return f"[{', '.join([str(action) for action in self.action_list])}]"

# Enemy-specific Actions

class TheVultureEntryAction(Action):
  def act(self, actor, enc) -> List[Event]:
    dead_enemies = len(enc.dead_enemies)
    events = []
    
    events += AddConditionAction("sharp", 2*dead_enemies, "self").act(actor, enc)
    events += AddConditionAction("regen", dead_enemies, "self").act(actor, enc)
    events += AddConditionAction("retaliate", dead_enemies, "self").act(actor, enc)
    return events
  
# Utils

def involves_add_undying(action):
  if isinstance(action, AddConditionAction) and action.condition == "undying":
    return True
  elif isinstance(action, MultiAction):
    return any(involves_add_undying(a) for a in action.action_list)
