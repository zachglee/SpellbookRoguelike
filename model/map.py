import random
from copy import deepcopy
from typing import List, Literal, Tuple
from termcolor import colored
from collections import defaultdict
from termcolor import colored
from model.safehouse import Safehouse
from model.spellbook import LibrarySpell
from model.encounter import Encounter, EnemyWave
from model.player import Player
from utils import aligned_line, energy_color_map, numbered_list, choose_obj, choose_idx, choose_binary, colorize, choose_str
from generators import generate_spell_pools, generate_faction_sets, generate_enemy_set_pool, generate_library_spells, generate_rituals
from content.enemy_factions import factions

class Node:
  def __init__(self, safehouse, guardian_enemy_waves: List[EnemyWave], position, seen=False,
               difficulty=1, boss=False, page_capacity=3, num_pages=2):
    self.safehouse = safehouse
    self.guardian_enemy_waves = guardian_enemy_waves
    self.ambient_energy = random.choice(["red", "blue", "gold"])
    self.position = position
    self.passages = ["fail" for i in range(4)]
    self.seen = seen
    self.difficulty = difficulty
    self.boss = boss
    self.page_capacity = page_capacity
    self.num_pages = num_pages
    self.heat = 0
    self.blockaded = False

    # Flavor
    self.fight_flavor = ""
    self.navigate_flavor = ""
    self.name = None

  @property
  def column(self):
    return self.position[1]
  
  @property
  def layer(self):
    return self.position[0]

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
    passages_str = f"({self.pass_passages})" + colored("!" * self.heat, "red")
    if self.blockaded:
      passages_str = passages_str + " BLOCK  "
    name_str = colored(f" {self.name} ", "magenta") if self.name else ""
    return (f"{colored('*', energy_color_map[self.ambient_energy])}"
            + passages_str + name_str
            + ", ".join(character.name[:4] for character in self.safehouse.resting_characters))

  def prompt_flavor(self, player, traverse_type: Literal["fight", "navigate"]):
    if not self.name:
      new_name = input(colored(f"You leave this place. What shall you name it?\n > ", "magenta"))
      self.name = new_name
    elif not self.fight_flavor and traverse_type == "fight":
      new_flavor = input(colored(f"You leave this place. What does {player.name} write of this place that night?\n > ", "magenta"))
      self.fight_flavor = new_flavor + f"\n     - {player.name}"
    elif not self.navigate_flavor and traverse_type == "navigate":
      new_flavor = input(colored(f"You arrive at the safehouse. What does {player.name} write of this place that night?\n > ", "magenta"))
      self.navigate_flavor = new_flavor + f"\n     - {player.name}"

  def render_flavor(self, traverse_type: Literal["fight", "navigate"]):
    flavor_text_dict = {
      "fight": self.fight_flavor,
      "navigate": self.navigate_flavor
    }
    flavor_text = flavor_text_dict.get(traverse_type, "No words from delvers past are recorded here.")
    if flavor_text:
      rendered_str = f"~~~\n\n    Your journey continues...\n\n    {flavor_text}\n\n~~~"
      return colored(rendered_str, "magenta")

  def render(self):
    name_str = colored(self.name, "magenta") if self.name else "Node"
    blockaded_str = colored(" [BLOCKADED]", "red") if self.blockaded else ""
    passages_str = colored(f"{self.pass_passages} passages", "green") if self.pass_passages else ""
    heat_str = colored(f"{self.heat} heat", "red") if self.heat else ""
    state_str = "(" + ", ".join(s for s in [passages_str, heat_str] if s) + ")"
    render_str = f"-------- {name_str} {blockaded_str} {self.position} : {state_str} --------\n"
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
  def __init__(self, position, width, height, spell_pool, faction_set,
               enemy_set_pool_size=12, extra_boss_enemy_sets=1, explore_difficulty=4):
    # setup
    self.position = position
    self.spell_pool = spell_pool
    self.faction_set = faction_set
    self.explore_difficulty = explore_difficulty
    
    enemy_set_universe = sum([faction.enemy_sets for faction in faction_set], [])
    self.enemy_set_pool = enemy_set_universe[0:enemy_set_pool_size]
    random.shuffle(self.spell_pool)
    random.shuffle(self.enemy_set_pool)
    spell_pool_cursor = 0
    enemy_set_pool_cursor = 0
    self.corruption = 0
    self.dropped_items = []

    self.enemy_view = True

    # generate the nodes
    # TODO: Make helpers to generate boss / nonboss nodes
    # TODO: Make a persistent spell pool and enemy set pool objects
    self.nodes = []
    for i in range(1, height + 1):
      row_of_nodes = []
      for j in range(width):
        library = [LibrarySpell(sp) for sp in self.spell_pool[spell_pool_cursor:spell_pool_cursor + 2]]
        unique_enemy_sets = self.enemy_set_pool[enemy_set_pool_cursor:enemy_set_pool_cursor + 1] + [random.choice(self.enemy_set_pool)]
        guardian_enemy_wave = EnemyWave(unique_enemy_sets)
        node = Node(Safehouse(library), [guardian_enemy_wave], (i, j))
        row_of_nodes.append(node)
        spell_pool_cursor += 2
        enemy_set_pool_cursor += 1
      self.nodes.append(row_of_nodes)
    # generate starting layer
    starting_layer = [Node(Safehouse([]), [], (0, i), seen=True) for i in range(width)]
    self.nodes = [starting_layer] + self.nodes

    # generate boss layer
    boss_layer = []
    random.shuffle(self.enemy_set_pool)
    random.shuffle(self.spell_pool)
    enemy_set_pool_cursor = 0
    spell_pool_cursor = 0
    for j in range(2):
      library = [LibrarySpell(sp) for sp in self.spell_pool[spell_pool_cursor:spell_pool_cursor + 2]]
      guardian_enemy_wave1 = EnemyWave(self.enemy_set_pool[enemy_set_pool_cursor:enemy_set_pool_cursor + 2], 0)
      guardian_enemy_wave2 = EnemyWave(self.enemy_set_pool[enemy_set_pool_cursor + 2:enemy_set_pool_cursor + 2 + extra_boss_enemy_sets], 2)
      boss_layer.append(Node(Safehouse(library), [guardian_enemy_wave1, guardian_enemy_wave2], (height + 1, j), boss=True))
      enemy_set_pool_cursor += 2 + extra_boss_enemy_sets
      spell_pool_cursor += 2
    self.nodes.append(boss_layer)
    
    # 
    self.current_node = None
    self.destination_node = None
    self.player = None

  @property
  def starting_layer(self):
    return self.nodes[0]

  @property
  def boss_layer(self):
    return self.nodes[-1]

  @property
  def basic_items(self):
    return sum([faction.basic_items for faction in self.faction_set], [])
  
  @property
  def special_items(self):
    return sum([faction.special_items for faction in self.faction_set], [])

  def corrupt(self):
    self.corruption += 1
    # TODO: Maybe add back in later
    # eligible_nodes = [node for node in self.nodes[-2] if not node.blockaded and node.seen]
    # node_to_blockade = sorted(eligible_nodes, reverse=True, key=lambda n: n.pass_passages)[0]
    # node_to_blockade.blockaded = True
    # node_to_blockade.passages.append("fail")
    # new_enemy_set = random.choice(random.choice(self.faction_set).enemy_sets)
    # new_enemy_wave = EnemyWave([new_enemy_set], 2)
    # node_to_blockade.guardian_enemy_waves.append(new_enemy_wave)

  def choose_node(self):
    while True:
      print(self.render())
      try:
        raw_input = input(colored("choose node > ", "cyan"))
        if raw_input in ["back", "done"]:
          return None
        elif raw_input in ["view", "v"]:
          self.enemy_view = not self.enemy_view
        elif raw_input == "map":
          print(self.render())
          continue
        input_tokens = raw_input.split(",")
        layer_idx = int(input_tokens[0]) # there is a zeroth layer we don't render so no need to -1 here
        column_idx = int(input_tokens[1])
        node = self.nodes[layer_idx][column_idx]
        return node
      except (TypeError, ValueError, IndexError) as e:
        print(e)

  def get_route_for_node(self, i, j):
    """Generates a route to the node at the given position."""
    destination_node = self.nodes[i][j]
    encounter = Encounter(waves=destination_node.generate_encounter_waves(self.enemy_set_pool),
                          player=self.player,
                          ambient_energy=destination_node.ambient_energy,
                          basic_items=self.basic_items,
                          special_items=self.special_items,
                          unique_items=self.dropped_items,
                          boss=destination_node.boss)
    return destination_node, encounter

  def get_route_options(self, player) -> List[Tuple]:
    # generate available routes
    routes = []
    current_layer_idx = self.current_node.layer
    # current_column = player.current_column
    next_layer = self.nodes[current_layer_idx + 1]

    if current_layer_idx == len(self.nodes) - 2:
      #  Heading into boss layer case
      return [self.get_route_for_node(node.layer, node.column) for node in next_layer]
    else:
      #  Heading into normal layer case
      proximal_nodes = [next_layer[player.current_column + drift] for drift in [-1, 0, 1]
                        if player.current_column + drift >= 0 and player.current_column + drift < len(next_layer)]
      random.shuffle(proximal_nodes)
      routes = [self.get_route_for_node(node.layer, node.column) for node in  proximal_nodes[:2]]
    
    done_exploring = False
    while True:
      # render the routes
      print(player.render_library() + "\n")
      for node, encounter in routes:
        print(node.render())
        print()
      still_exploring = choose_binary(colored("Explore more? (Costs 1hp)", "red"))
      if still_exploring:
        route_nodes = [route[0] for route in  routes]
        discoverable_nodes = [node for node in next_layer if node not in route_nodes]
        route_node = random.choice(discoverable_nodes)
        routes.append(self.get_route_for_node(route_node.layer, route_node.column))
        player.hp -= 1
      else:
        break
    return routes


  def choose_route(self, player):
    """Prompts the user to choose a route to the next layer.

    Returns the encounter for that route and updates the destination node."""

    # show the region map
    print(self.render())

    routes = self.get_route_options(player)

    # render the routes
    print(player.render_library() + "\n")
    for node, encounter in routes:
      print(node.render())
      print()
    node, encounter = choose_obj(routes, colored("choose a route > ", "red"))
    
    self.destination_node = node
    if not node.seen:
      player.experience += 10
      print(colored("You gain 10 experience for exploring a new node!", "green"))
    node.seen = True

    if node.blockaded:
      input(colored("This node is blockaded. You must fight.", "red"))
      fight = True
    else:
      fight = choose_binary("Fight or navigate?", ["fight", "navigate"])
    print(f"\n{node.render_flavor('fight' if fight else 'navigate')}\n")

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
    content_preview_lines = []

    if self.enemy_view:
      max_content_length = max(len(n.guardian_enemy_sets) for n in layer)
      get_node_content = lambda node, i: (node.guardian_enemy_sets[i].name if node.seen else "???") if i < len(node.guardian_enemy_sets) else "   "
    else:
      max_content_length = max(len(n.safehouse.library) for n in layer)
      get_node_content = lambda node, i: (node.safehouse.library[i].spell.description if node.seen else "???") if i < len(node.safehouse.library) else "   "

    for i in range(max_content_length):
      content_preview_line = []
      for node in layer:
        content_preview_line.append(get_node_content(node, i))
      content_preview_lines.append(content_preview_line)

    rendered_overview_line = aligned_line(node_overviews)
    rendered_preview_lines = [aligned_line([f"  {s}" for s in line]) for line in content_preview_lines]
    character_section = "\n".join([f"{character.name}: \"{character.request}\"" for character in characters])
    return "\n".join([rendered_overview_line] + rendered_preview_lines) + "\n" + character_section
    

  def render(self):
    """Renders the region."""
    faction_names = [faction.name for faction in self.faction_set]
    faction_summary = colored(f"~~~~~~~~~~~~ {', '.join(faction_names)} ~~~~~~~~~~~~", "red")
    rendered_layers = [f"-------- Layer {i} --------\n{self.render_layer(i)}"
                       for i in reversed(range(1, len(self.nodes)))]
    corruption_str = colored(f"\nCorruption: {self.corruption}", "red") if self.corruption > 0 else ""
    return faction_summary + "\n" + "\n\n".join(rendered_layers) + corruption_str
  
  def inspect(self):
    while True:
      node = self.choose_node()
      if node is None:
        break
      print(node.render())

class Map:
  def __init__(self, n_regions=3):
    spell_pools = generate_spell_pools(n_pools=n_regions)
    faction_sets = generate_faction_sets(n_sets=n_regions, set_size=3)
    self.regions = [Region(i, 6, 2, spell_pool, faction_set, extra_boss_enemy_sets=i+1, explore_difficulty=4+i)
                    for i, spell_pool, faction_set in zip(range(n_regions), spell_pools, faction_sets)]
    for node in self.regions[1].boss_layer:
      node.page_capacity = 4
    for node in self.regions[2].boss_layer:
      node.page_capacity = 4
      node.num_pages = 3

    self.current_region_idx = 0
    self.active_ritual = None
    self.runs = 0
    self.log_entries: List[Tuple[str, str]] = []
  
  @property
  def current_region(self):
    return self.regions[self.current_region_idx]
  
  def get_random_location_tuple(self):
    region_idx = random.randint(0, len(self.regions) - 1)
    layer_idx = random.randint(1, len(self.regions[region_idx].nodes) - 1)
    node = random.choice(self.regions[region_idx].nodes[layer_idx])
    return (region_idx, layer_idx, node.column)

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
    print(f"~~~~ Run {self.runs + 1} ~~~~")
    region, starting_node = self.inspect()
    if character and starting_node:
      player = character
      self.current_region_idx = region.position
      self.current_region.current_node = starting_node
      if region.position == 0 and starting_node.position == (0, 0):
        player.init(spell_pool=self.current_region.spell_pool)
    elif starting_node:
      character_idx = choose_idx(starting_node.safehouse.resting_characters, colored("Choose a character > ", "green"))
      if character_idx is not None:
        player = starting_node.safehouse.resting_characters.pop(character_idx)
        player.inspect()
        self.current_region_idx = region.position
        self.current_region.current_node = starting_node
        if region.position == 0 and starting_node.position == (0, 0):
          player.init(spell_pool=self.current_region.spell_pool)
    else:
      print("Starting a new character...")
      signature_spell_options = generate_library_spells(2, spell_pool=region.spell_pool)
      print(numbered_list(signature_spell_options))
      chosen_spell = choose_obj(signature_spell_options, colored("Choose signature spell > ", "red"))
      chosen_color = choose_str(["red", "blue", "gold"], "choose an energy color > ")
      name = input("What shall they be called? > ")
      library = ([LibrarySpell(chosen_spell.spell, copies=3, signature=True)])
      player = Player(hp=30, name=name,
                      spellbook=None,
                      inventory=[],
                      library=library,
                      signature_spell=chosen_spell,
                      signature_color=chosen_color,
                      personal_destination=self.get_random_location_tuple(),
                      home_column=random.choice(range(len(self.regions[0].starting_layer))))
      print(player.render_rituals())
      player.init(spell_pool=self.current_region.spell_pool, new_character=True)
      self.current_region_idx = 0
      self.current_region.current_node = self.current_region.nodes[0][player.home_column]
    self.current_region.player = player
    return player

  def end_run(self):
    self.runs += 1
    # TODO: Maybe remove this if we move away from corruption
    # if self.runs % 3 == 0:
    #   corruption_progress = int(self.runs / 3)
    #   print(colored(f"Corruption has progressed to level {corruption_progress}", "red"))
    #   for region in self.regions[0:corruption_progress]:
    #     region.corrupt()

  def inspect(self):
    print(self.current_region.render())
    last_inspected = self.current_region
    while (cmd := input("inspect the map > ")) != "done":
      cmd_tokens = cmd.split(" ")
      try:
        if cmd_tokens[0] == "region":
          idx = int(cmd_tokens[1]) - 1
          print(self.regions[idx].render())
          last_inspected = self.regions[idx]
        elif cmd_tokens[0] == "node":
          region = last_inspected
          layer_idx = int(cmd_tokens[1])
          column_idx = int(cmd_tokens[2])
          print(region.nodes[layer_idx][column_idx].render())
        elif cmd_tokens[0] == "start":
          region = last_inspected
          layer_idx = int(cmd_tokens[1])
          column_idx = int(cmd_tokens[2])
          node = region.nodes[layer_idx][column_idx]
          return region, node
        elif cmd == "log":
          print(self.render_log())
        elif cmd in ["view", "v"] and isinstance(last_inspected, Region):
          last_inspected.enemy_view = not last_inspected.enemy_view
          print(last_inspected.render())
        elif cmd == "new character":
          return self.regions[0], None
      except (KeyError, IndexError, ValueError, TypeError) as e:
        print(e)
    
  def render_log(self) -> str:
    render_str = "-------- World Log --------"
    render_str += "\n\n".join([f"{i+1} - {entry[0]}: {entry[1]}" for i, entry in enumerate(self.log_entries)])
    return colored(render_str, "magenta")
