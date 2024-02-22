""""""
from termcolor import colored

class Recipe:
  def __init__(self, item, material_cost, secret_cost, stock):
    self.item = item
    self.material_cost = material_cost
    self.secret_cost = secret_cost
    self.stock = stock
  
  def render(self):
    item_str = colored(self.item.name, "magenta") if self.item.rare else colored(self.item.render(), "cyan")
    material_cost_str = colored(f"{self.material_cost}⛁", "yellow")
    secrets_cost_str = ", ".join(colored(f"{secrets} {faction}", "magenta") for faction, secrets in self.secret_cost.items())
    return f"[{self.stock}] {item_str} - {material_cost_str}, {secrets_cost_str}"