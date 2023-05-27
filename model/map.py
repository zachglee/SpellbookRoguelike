import random
from copy import deepcopy
from termcolor import colored
from collections import defaultdict
from termcolor import colored
from drafting import draft_player_library
from model.safehouse import Safehouse
from model.spellbook import LibrarySpell
from model.encounter import Encounter, EnemyWave
from model.player import Player
from utils import energy_color_map, numbered_list, choose_obj, choose_idx, choose_binary, colorize, choose_str
from generators import generate_spell_pools, generate_enemy_set_pool, generate_library_spells, generate_rituals
from content.aspirations import aspirations
from content.items import starting_weapons

class Node:
  def __init__(self, safehouse, guardian_enemy_waves: EnemyWave, position, seen=False, difficulty=1):
    self.safehouse = safehouse
    self.guardian_enemy_waves = guardian_enemy_waves
    self.ambient_energy = random.choice(["red", "blue", "gold"])
    self.position = position
    self.passages = ["fail" for i in range(4)]
    self.seen = seen
    self.difficulty = difficulty

  @property
  def guardian_enemy_sets(self):
    return sum([wave.enemy_sets for wave in self.guardian_enemy_waves], [])

  @property
  def fail_passages(self):
    return self.passages.count("fail")
  
  @property
  def pass_passages(self):
    return self.passages.count("pass")

  def generate_encounter_waves(self, enemy_set_pool):
    encounter_waves = [deepcopy(wave) for wave in self.guardian_enemy_waves]
    for i in range(self.difficulty):
      wave_to_reinforce = encounter_waves[i % len(encounter_waves)]
      wave_to_reinforce.enemy_sets += [random.choice(enemy_set_pool)]
    return encounter_waves

  def render_preview(self):
    if not self.seen:
      return colored("???", "cyan")
    return (f"{colored('*', energy_color_map[self.ambient_energy])}"
            f"{self.pass_passages}/{len(self.passages)} "
            + ", ".join(character.name[:4] for character in self.safehouse.resting_characters))

  def render(self):
    total = len(self.passages)
    render_str = f"-------- Node {self.position} : ({self.pass_passages}/{total} passages) --------\n"
    guardian_enemy_set_names = ", ".join([es.name for es in self.guardian_enemy_sets])
    # render known enemy waves
    if self.seen:
      render_str += colorize(
        colored("Enemy Sets: ", "red") +
        f"{len(self.guardian_enemy_sets) + 1} | Waves: {len(self.guardian_enemy_waves)} ({guardian_enemy_set_names}), "
        f"Ambient {self.ambient_energy}") + "\n"
    else:
      render_str += colorize(
        f"{len(self.guardian_enemy_sets) + 1} | Waves: {len(self.guardian_enemy_waves)} (???), "
        f"Ambient {self.ambient_energy}") + "\n"
    # render safehouse library
    render_str += numbered_list(self.safehouse.library)
    if self.safehouse.resting_characters:
      render_str += colored("\nResting Characters:\n", "green")
      render_str += "\n".join([f"{i+1} - {c.render()} - \"{c.request}\""
                               for i, c in enumerate(self.safehouse.resting_characters)])
    return render_str

class Region:
  def __init__(self, position, width, height, spell_pool, enemy_set_pool):
    # setup
    self.position = position
    self.spell_pool = spell_pool
    self.enemy_set_pool = enemy_set_pool
    random.shuffle(self.spell_pool)
    random.shuffle(self.enemy_set_pool)
    spell_pool_cursor = 0
    enemy_set_pool_cursor = 0
    self.corruption = 0

    # generate the nodes
    # TODO: Make helpers to generate boss / nonboss nodes
    # TODO: Make a persistent spell pool and enemy set pool objects
    self.nodes = []
    for i in range(1, height + 1):
      row_of_nodes = []
      for j in range(width):
        library = [LibrarySpell(sp) for sp in self.spell_pool[spell_pool_cursor:spell_pool_cursor + 2]]
        unique_enemy_sets = self.enemy_set_pool[enemy_set_pool_cursor:enemy_set_pool_cursor + 1]
        guardian_enemy_wave = EnemyWave(unique_enemy_sets + [random.choice(self.enemy_set_pool)])
        node = Node(Safehouse(library), [guardian_enemy_wave], (i, j))
        row_of_nodes.append(node)
        spell_pool_cursor += 2
        enemy_set_pool_cursor += 1
      self.nodes.append(row_of_nodes)
    # generate starting layer
    starting_layer = [Node(Safehouse([]), [], (0, 0), seen=True)]
    self.nodes = [starting_layer] + self.nodes

    # generate boss layer
    boss_layer = []
    random.shuffle(self.enemy_set_pool)
    enemy_set_pool_cursor = 0
    for j in range(2):
      library = [LibrarySpell(sp) for sp in self.spell_pool[spell_pool_cursor:spell_pool_cursor + 2]]
      guardian_enemy_wave1 = EnemyWave(self.enemy_set_pool[enemy_set_pool_cursor:enemy_set_pool_cursor + 2], 0)
      guardian_enemy_wave2 = EnemyWave(self.enemy_set_pool[enemy_set_pool_cursor + 2:enemy_set_pool_cursor + 3], 2)
      boss_layer.append(Node(Safehouse(library), [guardian_enemy_wave1, guardian_enemy_wave2], (height + 1, j), seen=True))
      enemy_set_pool_cursor += 3
      spell_pool_cursor += 2
    self.nodes.append(boss_layer)
    
    # 
    self.current_node = self.nodes[0][0]
    self.destination_node = None
    self.player = None

  def corrupt(self):
    self.corruption += 1
    # make one node harder in each layer
    # TODO: this is a bit too punishing for now
    # for layer in self.nodes:
    #   most_passes_node = max(layer, key=lambda node: node.pass_passages)
    #   most_passes_node.passages += ["fail"] * self.corruption * 3
    pass

  def choose_node(self):
    print(self.render())
    while True:
      try:
        raw_input = input(colored("choose node > ", "cyan"))
        if raw_input == "done":
          return None
        elif raw_input == "map":
          print(self.render())
          continue
        input_tokens = raw_input.split(",")
        layer_idx = int(input_tokens[0]) # there is a zeroth layer we don't render so no need to -1 here
        column_idx = int(input_tokens[1]) - 1
        node = self.nodes[layer_idx][column_idx]
        return node
      except (TypeError, ValueError, IndexError) as e:
        print(e)

  def get_route_for_node(self, i, j):
    """Generates a route to the node at the given position."""
    destination_node = self.nodes[i][j]
    encounter = Encounter(waves=destination_node.generate_encounter_waves(self.enemy_set_pool),
                          player=self.player,
                          ambient_energy=destination_node.ambient_energy)
    return destination_node, encounter


  def choose_route(self, player):
    """Prompts the user to choose a route to the next layer.

    Returns the encounter for that route and updates the destination node."""

    # show the region map
    print(self.render())

    # generate available routes
    routes = []
    current_layer_idx = self.current_node.position[0]
    current_node_idx = self.current_node.position[1]
    next_layer = self.nodes[current_layer_idx + 1]
    if current_layer_idx == len(self.nodes) - 2:
      # heading into boss layer
      which_boss = int(current_node_idx / 2)
      routes.append(self.get_route_for_node(current_layer_idx + 1, which_boss))
    elif current_layer_idx == 0:
      # heading into first layer
      idx_choices = list(range(len(next_layer)))
      random.shuffle(idx_choices)
      routes.append(self.get_route_for_node(current_layer_idx + 1, idx_choices[0]))
      routes.append(self.get_route_for_node(current_layer_idx + 1, idx_choices[1]))
    else:
      routes.append(self.get_route_for_node(current_layer_idx + 1, current_node_idx))
      side_indices = [current_node_idx - 1, current_node_idx + 1]
      side_routes = [self.get_route_for_node(current_layer_idx + 1, i)
                     for i in side_indices if i >= 0 and i < len(next_layer)]
      routes.append(random.choice(side_routes))
    
    # prompt the player to choose a route
    print(player.render_library())
    for i, (node, encounter) in enumerate(routes):
      print(node.render())
      print()
    
    node, encounter = choose_obj(routes, colored("choose a route > ", "red"))
    self.destination_node = node
    node.seen = True
    fight = choose_binary("Fight or navigate?", ["fight", "navigate"])
    if fight:
      return encounter
    else:
      return "navigate"
  
  # Rendering

  def render_layer(self, layer_idx):
    """Renders a layer of the map."""
    layer = self.nodes[layer_idx]
    characters = sum([node.safehouse.resting_characters for node in layer], [])
    node_overviews = [node.render_preview() for node in layer]
    enemy_preview_lines = []
    for i in range(len(layer[0].guardian_enemy_sets)):
      enemy_preview_line = [node.guardian_enemy_sets[i].name if node.seen else "???" for node in layer]
      enemy_preview_lines.append(enemy_preview_line)
    # have to use a bigger format spacing to account for 'invisible' color code characters
    overview_render_template = " ".join("{" + str(i) + ":<31} " for i in range(len(layer)))
    rendered_overview_line = overview_render_template.format(*node_overviews)

    preview_render_template = " ".join("- {" + str(i) + ":<20} " for i in range(len(layer)))
    rendered_preview_lines = [preview_render_template.format(*line) for line in enemy_preview_lines]
    character_section = "\n".join([f"{character.name}: \"{character.request}\"" for character in characters])
    return "\n".join([rendered_overview_line] + rendered_preview_lines) + "\n" + character_section
    

  def render(self):
    """Renders the region."""
    rendered_layers = [f"-------- Layer {i} --------\n{self.render_layer(i)}"
                       for i in reversed(range(1, len(self.nodes)))]
    corruption_str = colored(f"\nCorruption: {self.corruption}", "red") if self.corruption > 0 else ""
    return "\n\n".join(rendered_layers) + corruption_str
  
  def inspect(self):
    print(self.render())
    while True:
      node = self.choose_node()
      if node is None:
        break
      print(node.render())

class Map:
  def __init__(self, n_regions=3):
    enemy_set_pool = generate_enemy_set_pool(n=27)
    spell_pools = generate_spell_pools(n_pools=n_regions)
    self.regions = [Region(i, 4, 2, spell_pool, enemy_set_pool[i*9:(i+1)*9])
                    for i, spell_pool in enumerate(spell_pools)]
    self.current_region_idx = 0
    self.active_ritual = None # random.choice(rituals)
    self.runs = 0
  
  @property
  def current_region(self):
    return self.regions[self.current_region_idx]
  
  def choose_region(self) -> Region:
    while True:
      try:
        region_idx = choose_idx(self.regions, "Choose a region > ")
        if region_idx is None:
          return None
        return self.regions[region_idx]
      except (TypeError, ValueError, IndexError) as e:
        print(e)

  def init(self, character=None) -> Player:
    print(f"Active Ritual: {self.render_active_ritual()}")
    print(f"~~~~ Run {self.runs + 1} ~~~~")
    region = self.choose_region()
    starting_node = region.choose_node()
    print(starting_node.render())
    if character:
      player = character
      self.current_region_idx = region.position
      self.current_region.current_node = starting_node
      if region.position == 0 and starting_node.position == (0, 0):
        player.init(spell_pool=self.current_region.spell_pool)
    else:
      character_idx = choose_idx(starting_node.safehouse.resting_characters, colored("Choose a character > ", "green"))
      if character_idx is not None:
        player = starting_node.safehouse.resting_characters.pop(character_idx)
        self.current_region_idx = region.position
        self.current_region.current_node = starting_node
        if region.position == 0 and starting_node.position == (0, 0):
          player.init(spell_pool=self.current_region.spell_pool)
      else:
        self.current_region_idx = 0
        self.current_region.current_node = self.current_region.nodes[0][0]
        print("Starting a new character...")
        # TODO: let player choose spell color and type of their signature!
        signature_spell_options = generate_library_spells(1, spell_pool=region.spell_pool)
        print(numbered_list(signature_spell_options))
        chosen_spell = choose_obj(signature_spell_options, colored("Choose signature spell > ", "red"))
        chosen_color = choose_str(["red", "blue", "gold"], "choose an energy color > ")
        # NOTE: not currently using aspirations
        # chosen_aspiration = choose_str(aspirations, f"choose an aspiration ({', '.join(aspirations)}) > ")
        chosen_aspiration = random.choice(aspirations)
        name = input("What shall they be called? > ")
        library = ([LibrarySpell(chosen_spell.spell, copies=4, signature=True)])
        player = Player(hp=30, name=name,
                        spellbook=None,
                        inventory=[],
                        library=library,
                        signature_spell=chosen_spell,
                        signature_color=chosen_color,
                        aspiration=chosen_aspiration)
        # TODO: possibly remove this later
        print(player.render_rituals())
        draft_player_library(player, self.current_region.spell_pool)
        player.init(spell_pool=self.current_region.spell_pool)
    self.current_region.player = player
    return player

  def end_run(self):
    self.runs += 1
    if self.runs % 3 == 0:
      corruption_progress = int(self.runs / 3)
      print(colored(f"Corruption has progressed to level {corruption_progress}", "red"))
      for region in self.regions[0:corruption_progress]:
        region.corrupt()

  def inspect(self):
    while True:
      region = self.choose_region()
      if region is None:
        return None
      region.inspect()
  
  def render_active_ritual(self):
    if self.active_ritual is None:
      return "No active ritual."
    else:
      return self.active_ritual.render()