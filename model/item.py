from typing import Any, Dict, Optional
from pydantic import BaseModel

from utils import colorize
from termcolor import colored
  
class Item(BaseModel):
  name: str
  charges: int
  max_charges: int
  description: str
  use_commands: list[str]
  generate_commands_pre: callable = lambda e, t: []
  time_cost: int = 1
  material_cost: Optional[int] = None
  weight: float = 1
  rare: bool = False
  faction: str = ""
  craftable: bool = True
  personal: bool = False
  belonged_to: Optional[str] = None

  class Config:
    arbitrary_types_allowed = True

  @classmethod
  def make(cls, name, charges, description, use_commands,
           generate_commands_pre=lambda e, t: [], time_cost=1, material_cost=None, weight=1, rare=False, faction="", personal=False, craftable=True):
    """Literally just exists to make so we can pass one arg for charges and max charges."""
    return cls(name=name, charges=charges, max_charges=charges, description=description, use_commands=use_commands,
               generate_commands_pre=generate_commands_pre, time_cost=time_cost, material_cost=material_cost, weight=weight,
               rare=rare, faction=faction, personal=personal, craftable=craftable)
    

  async def use(self, encounter):
    # generate commands pre-execution
    generated_commands_pre = self.generate_commands_pre(encounter, None)
    raw_commands = self.use_commands + generated_commands_pre

    for command in raw_commands:
      await encounter.handle_command(command)
    self.charges -= 1

  def render(self):
    belonged_to_str = f"{self.belonged_to}'s " if self.belonged_to else ""
    charges_str = f"({self.charges})" if self.max_charges > 0 else colored(f"({self.charges})", "red")
    return colorize(f"{belonged_to_str}{self.name} {charges_str}: {self.description}")
