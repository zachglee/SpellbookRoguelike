from utils import colorize, choose_obj
from termcolor import colored

class RestAction:
  def __init__(self, cost, effect, description):
    self.cost = cost
    self.effect = effect
    self.description = description

  def render_cost(self):
    render_str = ", ".join(f"{v} {k}" for k, v in self.cost.items())
    return colorize(render_str)

  def render(self):
    return f"{self.render_cost()} -> {self.description}"

class RestSite:
  def __init__(self, rest_actions, player):
    self.rest_actions = rest_actions
    self.player = player
    self.researching = []
    self.library = []

  def pick_rest_action(self):
    return choose_obj(self.rest_actions, "pick rest action > ")

  def render(self):
    render_str = f"-------- {colored('Rest', 'cyan')} Site --------\n"
    render_str += "\n".join(f"{i+1}) {ra.render()}" for i, ra in enumerate(self.rest_actions))
    if self.player:
      render_str += f"\n-------- Player {colored('Loot', 'yellow')} --------\n"
      render_str += self.player.render_loot() + "\n"
      render_str += self.player.render()
    return render_str

