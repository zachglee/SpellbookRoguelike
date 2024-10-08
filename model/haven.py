from collections import defaultdict
from copy import deepcopy
import dill
from termcolor import colored
from utils import choose_str, numbered_list, render_secrets_dict, ws_print
from content.enemy_factions import faction_rituals_dict

RITUAL_PROGRESS_PRICE = 20

class Haven:
  def __init__(self, library):
    self.material = 0
    self.keys = 0
    self.secrets_dict = defaultdict(int)
    self.items = []
    self.rituals = []
    self.runs = 0
    self.season = 0

    self.library = library

  def save(self):
    with open(f"saves/haven.pkl", "wb") as f:
      dill.dump(self, f)

  async def pre_embark(self, player):
    
    choice = True
    prepared_rituals = {}
    while choice and self.rituals:
      await ws_print(player.render(), player.websocket)
      await ws_print(self.render(), player.websocket)
      choices = [ritual.faction for ritual in self.rituals]
      choice = await choose_str(choices, "Choose a ritual to prepare > ", player.websocket)

      if choice and self.secrets_dict[choice] >= RITUAL_PROGRESS_PRICE:
        if prepared_rituals.get(choice):
          prepared_rituals[choice].progress += prepared_rituals[choice].required_progress
        else:
          prepared_rituals[choice] = deepcopy(faction_rituals_dict[choice])
          prepared_rituals[choice].progress += prepared_rituals[choice].required_progress

        self.secrets_dict[choice] -= RITUAL_PROGRESS_PRICE
        player.rituals = list(prepared_rituals.values())
        await ws_print(player.render_rituals(), player.websocket)
      else:
        await ws_print(colored(f"Not enough secrets to progress ritual of faction {choice}!", "red"), player.websocket)

  def render_rituals(self) -> str:
    secrets_part = colored(render_secrets_dict(self.secrets_dict), "cyan")
    rituals_part = "-------- HAVEN RITUALS --------\n" + numbered_list(self.rituals)
    return f"{secrets_part}\n{rituals_part}"

  def render(self, player=None):
    # material_part = colored(f"{self.material}⛁", "yellow")
    keys_part = colored(f"{self.keys}♦", "green")
    rituals_part = self.render_rituals()
    library_spells = self.library if player is None else self.library + player.personal_spells
    library_part = "-------- HAVEN LIBRARY --------\n" + numbered_list(library_spells)
    return f"~~~~ HAVEN {keys_part} ~~~~\n{rituals_part}\n{library_part}"