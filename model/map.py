import random
from termcolor import colored
from collections import defaultdict
from termcolor import colored
from model.safehouse import Safehouse
from model.spellbook import LibrarySpell
from model.encounter import Encounter
from utils import energy_colors, energy_color_map, numbered_list, choose_obj, choose_binary

class Node:
  def __init__(self, safehouse, guardian_enemy_sets, position):
    self.safehouse = safehouse
    self.guardian_enemy_sets = guardian_enemy_sets
    self.ambient_energy = random.choice(["red", "blue", "gold"])
    self.position = position
    self.passages = ["fail" for i in range(10)]

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
    for i in range(1, height + 1):
      row_of_nodes = []
      for j in range(width):
        library = [LibrarySpell(sp) for sp in self.spell_pool[spell_pool_cursor:spell_pool_cursor + 2]]
        unique_enemy_sets = self.enemy_set_pool[enemy_set_pool_cursor:enemy_set_pool_cursor + 1]
        guardian_enemy_sets = unique_enemy_sets + [random.choice(self.enemy_set_pool)]
        node = Node(Safehouse(library), guardian_enemy_sets, (i, j))
        row_of_nodes.append(node)
        spell_pool_cursor += 2
        enemy_set_pool_cursor += 1
      self.nodes.append(row_of_nodes)
    # generate starting layer
    starting_layer = [Node(Safehouse([]), [], (0, j)) for j in range(width)]
    self.nodes = [starting_layer] + self.nodes

    # generate boss layer
    boss_layer = []
    random.shuffle(self.enemy_set_pool)
    enemy_set_pool_cursor = 0
    for j in range(2):
      library = [LibrarySpell(sp) for sp in self.spell_pool[spell_pool_cursor:spell_pool_cursor + 2]]
      guardian_enemy_sets = self.enemy_set_pool[enemy_set_pool_cursor:enemy_set_pool_cursor + 3]
      boss_layer.append(Node(Safehouse(library), guardian_enemy_sets, (height + 1, j)))
      enemy_set_pool_cursor += 3
      spell_pool_cursor += 2
    self.nodes.append(boss_layer)
    
    # 
    self.current_node = random.choice(self.nodes[0])
    self.destination_node = None
    self.player = None

  def generate_route(self, drift=0):
    """Generates a route from the current node to the destination node."""
    current_layer_idx = self.current_node.position[0]
    if current_layer_idx >= len(self.nodes) - 1:
      raise ValueError("You are already at the top of the map.")
    next_layer = self.nodes[current_layer_idx + 1]
    destination_node_column = (self.current_node.position[1] + drift) % len(next_layer)
    destination_node = next_layer[destination_node_column]

    enemy_sets = destination_node.guardian_enemy_sets + [random.choice(self.enemy_set_pool)]
    encounter = Encounter(enemy_sets, self.player, ambient_energy=destination_node.ambient_energy)
    return destination_node, encounter


  def choose_route(self, player):
    """Prompts the user to choose a route to the next layer.

    Returns the encounter for that route and updates the destination node."""

    # generate available routes
    routes = []
    routes.append(self.generate_route(drift=0))
    routes.append(self.generate_route(drift=random.choice([-1, 1])))
    
    # prompt the player to choose a route
    print(player.render_library())
    for i, (node, encounter) in enumerate(routes):
      passes = node.passages.count("pass")
      total = len(node.passages)
      print(f"-------- Destination {i+1} : {node.position} : ({passes}/{total} passages) --------")
      print(encounter.render_preview(preview_enemy_sets=node.guardian_enemy_sets))
      print(numbered_list(node.safehouse.library))
      print()
    
    node, encounter = choose_obj(routes, colored("choose a route > ", "red"))
    self.destination_node = node
    fight = choose_binary("Fight or navigate?", ["fight", "navigate"])
    if fight:
      return encounter
    else:
      return "navigate"
  
  def render_layer(self, layer_idx):
    """Renders a layer of the map."""
    layer = self.nodes[layer_idx]
    node_overviews = [
      f"{colored('*', energy_color_map[node.ambient_energy])}"
      f"{node.passages.count('pass')}/{len(node.passages)}"
      for node in layer]
    enemy_preview_lines = []
    for i in range(len(layer[0].guardian_enemy_sets)):
      enemy_preview_line = [node.guardian_enemy_sets[i].name for node in layer]
      enemy_preview_lines.append(enemy_preview_line)
    # have to use a bigger format spacing to account for 'invisible' color code characters
    overview_render_template = " ".join("{" + str(i) + ":<31} " for i in range(len(layer)))
    rendered_overview_line = overview_render_template.format(*node_overviews)

    preview_render_template = " ".join("- {" + str(i) + ":<20} " for i in range(len(layer)))
    rendered_preview_lines = [preview_render_template.format(*line) for line in enemy_preview_lines]
    return "\n".join([rendered_overview_line] + rendered_preview_lines)
    

  def render(self):
    """Renders the map."""
    rendered_layers = [f"-------- Layer {i} --------\n{self.render_layer(i)}"
                       for i in reversed(range(1, len(self.nodes)))]
    return "\n\n".join(rendered_layers)





  
