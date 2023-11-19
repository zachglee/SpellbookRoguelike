from sound_utils import play_sound
from termcolor import colored
from copy import deepcopy
from utils import choose_obj, numbered_list, ws_print


class ShopItem:
  def __init__(self, item, cost, stock):
    self.item = item
    self.cost = cost
    self.stock = stock
  
  def render(self):
    item_str = colored(self.item.render(), "magenta") if self.item.rare else colored(self.item.render(), "cyan")
    cost_str = colored(f"{self.cost}⛁", "yellow")
    return f"[{self.stock}] {item_str} - {cost_str}"

class Shop:
  def __init__(self, shop_items):
    self.shop_items = shop_items

  def render(self):
    render_str = "-------- SHOP --------\n"
    render_str += numbered_list(self.shop_items)
    return render_str
  
  async def play(self, player):
    while True:
      await ws_print(player.render_state(), player.websocket)
      await ws_print("\n", player.websocket)
      await ws_print(self.render(), player.websocket)
      await ws_print("\n", player.websocket)
      await ws_print(colored(f"You have {player.material}⛁", "yellow"), player.websocket)
      chosen_item = await choose_obj(self.shop_items, "Choose an item to buy > ", player.websocket)
      if chosen_item is None:
        break
      if player.material >= chosen_item.cost:
        play_sound("inventory.mp3")
        player.material -= chosen_item.cost
        player.inventory.append(deepcopy(chosen_item.item))
        chosen_item.stock -= 1
        await ws_print(f"You bought {chosen_item.item.render()}", player.websocket)
      else:
        await ws_print("You cannot afford that item", player.websocket)
      self.shop_items = [item for item in self.shop_items if item.stock > 0]