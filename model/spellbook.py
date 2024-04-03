import os
from typing import Any, Dict, Literal
from pydantic import BaseModel
from termcolor import colored
from utils import Color, numbered_list, get_combat_entities, energy_color_map, energy_pip_symbol, ws_input
from sound_utils import play_sound

class Spell(BaseModel):
  rules_text: str
  color: Color
  type: Literal["Producer", "Converter", "Consumer", "Passive"]
  conversion_color: Color = None
  raw_commands: list[str] = []
  targets: list[str] = []
  generate_commands_pre: callable = lambda e, t: []
  generate_commands_post: callable = lambda e, t: []
  triggers_on: callable = lambda encounter, event: False
  sound_file: str = None
  id: int = None

  class Config:
    arbitrary_types_allowed = True
  
  # -------- Methods --------

  async def cast(self, encounter, cost_energy=True, cost_charges=True, trigger_output=None):
    if cost_energy:
      if self.type == "Producer":
        await encounter.handle_command(f"{self.color} p 1")
      if self.type == "Converter" and self.conversion_color is not None:
        await encounter.handle_command(f"{self.color} to {self.conversion_color}")
      if self.type == "Consumer":
        file_stem = f"{self.color}-consumer-cast"
        self.sound_file = f"{file_stem}.mp3" if os.path.isfile(f"assets/sounds/{file_stem}.mp3") else f"{file_stem}.wav"
        await encounter.handle_command(f"{self.color} p -1")
    
    # choose targets
    chosen_targets = {}
    for target_placeholder in self.targets:
      if target_placeholder in ["_"]:
        # FIXME: Add error handling for invalid targets
        target_ref = await ws_input(f"Choose a target for {target_placeholder} > ", websocket=encounter.player.websocket)
      else:
        target_ref = target_placeholder
      target_entities = await get_combat_entities(encounter, target_ref, websocket=encounter.player.websocket)
      if len(target_entities) > 1:
        raise ValueError("Targeting more than one entity is not yet supported.")
      else:
        target_entities = target_entities[0]
      chosen_targets[target_placeholder] = (target_ref, target_entities) 

    # generate commands pre-execution
    generated_commands_pre = self.generate_commands_pre(encounter, chosen_targets)
    cast_commands = self.raw_commands + generated_commands_pre

    # main execution
    for cmd in cast_commands:
      processed_command = cmd
      for placeholder, (target, _) in chosen_targets.items():
        processed_command = processed_command.replace(placeholder, target)
      if trigger_output != None:
        processed_command = processed_command.replace("^", str(trigger_output))
      await encounter.handle_command(processed_command)

    # generate and execute commands post main execution (for effects like 'if this kills')
    generated_commands_post = self.generate_commands_post(encounter, chosen_targets)
    for cmd in generated_commands_post:
      await encounter.handle_command(cmd)

    if sound_file := self.sound_file:
      play_sound(sound_file, channel=3)

  @property
  def description(self):
    color_pip = colored(energy_pip_symbol, energy_color_map[self.color.lower()])
    if self.type == "Consumer":
      return f"({color_pip}): {self.rules_text}"
    elif self.type == "Producer":
      producer_color_marker = colored("^", energy_color_map[self.color.lower()])
      return f"{producer_color_marker} {self.rules_text}"
    elif self.type == "Converter":
      convert_to_pip = colored(energy_pip_symbol, energy_color_map[self.conversion_color.lower()])
      return f"{color_pip}➜{convert_to_pip}: {self.rules_text}"
    elif self.type == "Passive":
      passive_marker = colored("#", energy_color_map[self.color.lower()])
      return f"{passive_marker} {self.rules_text}"

  def preview(self, length=24):
    return self.description[:length] + ("..." if len(self.description) > length else "")

  def __repr__(self):
    return self.description
  
  def render(self, **kwargs):
    return self.description

class LibrarySpell:
  def __init__(self, spell: Spell, copies=3, material_cost=5, signature=False):
    self.spell = spell
    self.signature = signature
    self.copies_remaining = copies
    self.max_copies_remaining = copies
    self.material_cost = material_cost
    
  
  def render(self):
    rendered_str = self.spell.description.replace("Red", colored("Red", "red"))
    rendered_str = rendered_str.replace("Gold", colored("Gold", "yellow"))
    rendered_str = rendered_str.replace("Blue", colored("Blue", "blue"))
    rendered_str = rendered_str.replace("Green", colored("Green", "green"))
    rendered_str = rendered_str.replace("Purple", colored("Purple", "magenta"))
    rendered_str = rendered_str.replace("Consumer", colored("Consumer", "magenta"))
    rendered_str = rendered_str.replace("Producer", colored("Producer", "green"))
    rendered_str = rendered_str.replace("Converter", colored("Converter", "cyan"))
    rendered_str = rendered_str.replace("Passive", colored("Passive", "yellow"))
    copies_remaining_part = f"[{self.copies_remaining}/{self.max_copies_remaining}]"
    material_cost_part = colored(f"({self.material_cost}⛁)", "yellow")
    if self.signature:
      copies_remaining_part = colored(copies_remaining_part, "magenta")
    if self.copies_remaining <= 0:
      copies_remaining_part = colored(copies_remaining_part, "red")
    return f"{copies_remaining_part} {material_cost_part} {rendered_str}"

class SpellbookSpell:
  def __init__(self, spell: Spell):
    self.spell = spell
    self.charges = 2
    self.max_charges = 3
    self.echoing = None
    self.exhausted = False

  def recharge(self):
    self.charges = min(self.charges + 1, self.max_charges)

  async def cast(self, encounter, cost_energy=True, cost_charges=True):
    if cost_charges:
      self.charges -= 1
    self.exhausted = True
    await self.spell.cast(encounter, cost_energy=cost_energy, cost_charges=cost_charges)

  def render(self):
    rendered_str = self.spell.description.replace("Red", colored("Red", "red"))
    rendered_str = rendered_str.replace("Gold", colored("Gold", "yellow"))
    rendered_str = rendered_str.replace("Blue", colored("Blue", "blue"))
    rendered_str = rendered_str.replace("Green", colored("Green", "green"))
    rendered_str = rendered_str.replace("Purple", colored("Purple", "magenta"))
    rendered_str = rendered_str.replace("Consumer", colored("Consumer", "magenta"))
    rendered_str = rendered_str.replace("Producer", colored("Producer", "green"))
    rendered_str = rendered_str.replace("Converter", colored("Converter", "cyan"))

    if self.spell.type == "Passive":
      charges_prefix = ""
    else:
      charges_prefix = f"({self.charges}/{self.max_charges})"
    if self.exhausted: charges_prefix = colored(f"~{charges_prefix}", "red")

    return f"{charges_prefix} {rendered_str}"

class SpellbookPage:
  def __init__(self, spells):
    self.spells = spells
    self.spent = False

  def render(self):
    return numbered_list(self.spells)

class Spellbook:
  def __init__(self, pages: SpellbookPage):
    self.pages = pages
    self.current_page_idx = 0

  @property
  def spells(self):
    spells = []
    for page in self.pages:
      spells += page.spells
    return spells

  @property
  def current_page(self) -> SpellbookPage:
    return self.pages[self.current_page_idx] if self.pages else SpellbookPage([])

  def switch_page(self):
    self.current_page_idx = (self.current_page_idx + 1) % len(self.pages)
    play_sound("page-flip-1.mp3")

  def render(self, editing_page_idx=None):
    rendered = ""
    for i, page in enumerate(self.pages):
      header = f"Page {i + 1}:"
      if editing_page_idx is not None and i == editing_page_idx:
        header = header + colored(" [EDITING]", "magenta")
      rendered += f"{header}\n" + page.render() + "\n"
    return rendered
  
  def render_current_page(self):
    return f"Current Page ({self.current_page_idx + 1}):\n" + self.current_page.render()

