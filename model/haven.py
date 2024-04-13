from collections import defaultdict
from copy import deepcopy
import dill
from termcolor import colored
from utils import choose_str, numbered_list, render_secrets_dict, ws_print
from content.enemy_factions import faction_rituals_dict

RITUAL_PROGRESS_PRICE = 50

class Haven:
  def __init__(self, library):
    self.material = 0
    self.supplies = 0
    self.secrets_dict = defaultdict(int)
    self.items = []
    self.rituals = []

    self.library = library

  def save(self):
    with open(f"saves/haven.pkl", "wb") as f:
      dill.dump(self, f)

  async def pre_embark(self, player):
    
    choice = True
    while choice and self.rituals:
      await ws_print(player.render(), player.websocket)
      await ws_print(self.render(), player.websocket)
      choices = [ritual.faction for ritual in self.rituals]
      choice = await choose_str(choices, "Choose > ", player.websocket)

      prepared_rituals = {}
      if choice and self.secrets_dict[choice] >= RITUAL_PROGRESS_PRICE:
        if prepared_rituals.get(choice):
          prepared_rituals[choice].progress += prepared_rituals[choice].required_progress
        else:
          prepared_rituals[choice] = deepcopy(faction_rituals_dict[choice])
          prepared_rituals[choice].progress += prepared_rituals[choice].required_progress

        self.secrets_dict[choice] -= RITUAL_PROGRESS_PRICE
        await ws_print(player.render_rituals(), player.websocket)
      else:
        await ws_print(colored(f"Not enough secrets to progress ritual of faction {choice}!", "red"), player.websocket)


  def render(self):
    # material_part = colored(f"{self.material}⛁", "yellow")
    # supplies_part = colored(f"{self.supplies}♦", "green")
    secrets_part = colored(render_secrets_dict(self.secrets_dict), "cyan")
    rituals_part = "-------- HAVEN RITUALS --------\n" + numbered_list(self.rituals)
    library_part = "-------- HAVEN LIBRARY --------\n" + numbered_list(self.library)
    return f"~~~~ HAVEN ~~~~\n{secrets_part}\n{rituals_part}\n{library_part}"