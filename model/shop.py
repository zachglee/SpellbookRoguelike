from model.item import Item
from sound_utils import play_sound, ws_play_sound
from termcolor import colored
from copy import deepcopy
from utils import choose_obj, numbered_list, ws_input, ws_print

class ShopItem:
  def __init__(self, item, cost, stock, immediate_effect=None):
    self.item = item
    self.cost = cost
    self.stock = stock
    self.immediate_effect = immediate_effect
  
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
  
  async def play(self, player, game_state):
    while True:
      await ws_print(player.render_state(), player.websocket)
      await ws_print("\n", player.websocket)
      await ws_print(self.render(), player.websocket)
      await ws_print("\n", player.websocket)
      await ws_print(colored(f"You have {player.material}⛁", "yellow"), player.websocket)
      chosen_item = await choose_obj(self.shop_items, "Choose an item to buy > ", player.websocket)
      if chosen_item is None:
        break
      elif chosen_item == "~":
        continue

      if (player.material >= chosen_item.cost and
          player.inventory_weight < player.inventory_capacity and
          chosen_item.stock > 0):
        await ws_play_sound("inventory.mp3", player.websocket)
        player.material -= chosen_item.cost
        player.inventory.append(deepcopy(chosen_item.item))
        player.seen_items.append(deepcopy(chosen_item.item))
        chosen_item.stock -= 1
        await ws_print(f"You bought {chosen_item.item.render()}", player.websocket)
        if chosen_item.immediate_effect:
          chosen_item.immediate_effect(player)
      else:
        await ws_input(colored("You cannot afford that item, or don't have space.", "red"), player.websocket)
      self.shop_items = [item if (item != "~" and item.stock > 0) else "~" for item in self.shop_items]
