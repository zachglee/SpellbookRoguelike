from typing import Any, Dict, Optional
from pydantic import BaseModel

from utils import colorize
from model.spellbook import SpellbookSpell
  
class Item(BaseModel):
  name: str
  charges: int
  max_charges: int
  description: str
  use_commands: list[str]
  generate_commands_pre: callable = lambda e, t: []
  time_cost: int = 1
  material_cost: Optional[int] = None
  rare: bool = False
  personal: bool = False
  belonged_to: Optional[str] = None

  class Config:
    arbitrary_types_allowed = True

  @classmethod
  def make(cls, name, charges, description, use_commands,
           generate_commands_pre=lambda e, t: [], time_cost=1, material_cost=None, rare=False, personal=False):
    """Literally just exists to make so we can pass one arg for charges and max charges."""
    return cls(name=name, charges=charges, max_charges=charges, description=description, use_commands=use_commands,
               generate_commands_pre=generate_commands_pre, time_cost=time_cost, material_cost=material_cost,
               rare=rare, personal=personal)
    

  def use(self, encounter):
    # generate commands pre-execution
    generated_commands_pre = self.generate_commands_pre(encounter, None)
    raw_commands = self.use_commands + generated_commands_pre

    for command in raw_commands:
      encounter.handle_command(command)
    self.charges -= 1

  def render(self):
    belonged_to_str = f"{self.belonged_to}'s " if self.belonged_to else ""
    return colorize(f"{belonged_to_str}{self.name} ({self.charges}): {self.description}")
