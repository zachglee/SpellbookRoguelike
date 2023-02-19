import random
from collections import defaultdict
from termcolor import colored
from model.safehouse import Safehouse
from model.spellbook import LibrarySpell
from model.encounter import Encounter
from utils import energy_colors, numbered_list, choose_obj

class Node:
  def __init__(self, safehouse, guardian_enemy_sets, position):
    self.safehouse = safehouse
    self.guardian_enemy_sets = guardian_enemy_sets
    self.ambient_energy = random.choice(["red", "blue", "gold"])
    self.position = position

class Map:
  def __init__(self, width, height, spell_pool, enemy_set_pool):
    # setup
    self.spell_pool = spell_pool
    self.enemy_set_pool = enemy_set_pool
    random.shuffle(self.spell_pool)
    random.shuffle(self.enemy_set_pool)
    spell_pool_cursor = 0
    enemy_set_pool_cursor = 0

    # generate the nodes
    self.nodes = []
    for i in range(height):
      row_of_nodes = []
      for j in range(width):
        library = [LibrarySpell(sp) for sp in self.spell_pool[spell_pool_cursor:spell_pool_cursor + 2]]
        guardian_enemy_sets = self.enemy_set_pool[enemy_set_pool_cursor:enemy_set_pool_cursor + 2]
        node = Node(Safehouse(library), guardian_enemy_sets, (i, j))
        row_of_nodes.append(node)
        spell_pool_cursor += 3
        enemy_set_pool_cursor += 1
      self.nodes.append(row_of_nodes)
    
    # 
    self.current_node = random.choice(self.nodes[0])
    self.destination_node = None
    self.player = None
    # keys are pairs of to/from node positions and values are counts of traversals:
    self.traversal_counts = defaultdict(lambda: [])

  def generate_route(self, drift=0):
    """Generates a route from the current node to the destination node."""
    current_layer_idx = self.current_node.position[0]
    if current_layer_idx >= len(self.nodes) - 1:
      raise ValueError("You are already at the top of the map.")
    next_layer = self.nodes[current_layer_idx + 1]
    destination_node_column = (self.current_node.position[1] + drift) % len(next_layer)
    destination_node = next_layer[destination_node_column]

    enemy_sets = destination_node.guardian_enemy_sets + self.enemy_set_pool[0:1]
    encounter = Encounter(enemy_sets, self.player, ambient_energy=destination_node.ambient_energy)
    return destination_node, encounter


  def choose_route(self):
    """Prompts the user to choose a route to the next layer.

    Returns the encounter for that route and updates the destination node."""

    # generate available routes
    routes = []
    routes.append(self.generate_route(drift=0))
    routes.append(self.generate_route(drift=random.choice([-1, 1])))
    
    # prompt the player to choose a route
    for i, (node, encounter) in enumerate(routes):
      print(f"-------- Destination {i+1} : {node.position} --------")
      print(encounter.render_preview(preview_enemy_sets=node.guardian_enemy_sets))
      print(numbered_list(node.safehouse.library))
      print()
    
    node, encounter = choose_obj(routes, colored("choose a route > ", "red"))
    self.destination_node = node
    return encounter





  
