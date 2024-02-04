import dill
from termcolor import colored
from utils import choose_str, numbered_list, render_secrets_dict, ws_print
from content.enemy_factions import factions

class Haven:
  def __init__(self):
    self.material = 0
    self.supplies = 0
    self.secrets_dict = {}
    self.items = []
    self.grimoires = []
    self.library = []

  def save(self):
    with open(f"saves/haven.pkl", "wb") as f:
      dill.dump(self, f)

  async def pre_embark(self, player):
    choice = True
    while choice:
      await ws_print(player.render(), player.websocket)
      await ws_print(self.render(), player.websocket)
      choice = await choose_str(["heal"], "Would you like to spend 1♦ and 8⛁ to heal 8 hp? ", player.websocket)
      if choice == "heal":
        if self.supplies >= 1 and self.material >= 8:
          self.supplies -= 1
          self.material -= 8
          player.heal(8)
        else:
          await ws_print(colored("Not enough resources!", "red") , player.websocket)

  def render(self):
    material_part = colored(f"{self.material}⛁", "yellow")
    supplies_part = colored(f"{self.supplies}♦", "green")
    secrets_part = colored(render_secrets_dict(self.secrets_dict), "cyan")
    grimoires_part = self.grimoires[0].render_preview() if self.grimoires else ""
    return f"~~~~ HAVEN ({material_part} | {supplies_part}) ~~~~\n{secrets_part}\n{grimoires_part}"