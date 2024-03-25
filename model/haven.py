from collections import defaultdict
import dill
from termcolor import colored
from utils import choose_str, numbered_list, render_secrets_dict, ws_print
from content.enemy_factions import factions

RITUAL_PROGRESS_PRICE = 3

class Haven:
  def __init__(self):
    self.material = 0
    self.supplies = 0
    self.secrets_dict = defaultdict(int)
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
      choices = ["heal"] + [ritual.faction for ritual in player.known_rituals]
      choice = await choose_str(choices, "Would you like to spend 1♦ and 5⛁ to heal 50% missing hp? ", player.websocket)
      if choice == "heal":
        if self.supplies >= 1 and self.material >= 5:
          self.supplies -= 1
          self.material -= 5
          heal_amount = int((player.max_hp - player.hp) * 0.5)
          player.heal(heal_amount)
        else:
          await ws_print(colored("Not enough resources!", "red") , player.websocket)
      elif choice:
        targets = [r for r in player.known_rituals if r.faction == choice]
        if targets and self.secrets_dict[choice] >= RITUAL_PROGRESS_PRICE:
          target_ritual = targets[0]
          target_ritual.progress += 1
          self.secrets_dict[choice] -= RITUAL_PROGRESS_PRICE
          await ws_print(player.render_rituals(), player.websocket)
        else:
          await ws_print(colored(f"Not enough secrets to progress ritual of faction {choice}!", "red"), player.websocket)


  def render(self):
    material_part = colored(f"{self.material}⛁", "yellow")
    supplies_part = colored(f"{self.supplies}♦", "green")
    secrets_part = colored(render_secrets_dict(self.secrets_dict), "cyan")
    grimoires_part = self.grimoires[0].render_preview() if self.grimoires else ""
    return f"~~~~ HAVEN ({material_part} | {supplies_part}) ~~~~\n{secrets_part}\n{grimoires_part}"