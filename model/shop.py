from sound_utils import play_sound
from termcolor import colored
from copy import deepcopy
from utils import choose_obj, numbered_list


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
  
  def play(self, player):
    while True:
      print(player.render_state())
      print()
      print(self.render())
      print()
      print(colored(f"You have {player.material}⛁", "yellow"))
      chosen_item = choose_obj(self.shop_items, "Choose an item to buy > ")
      if chosen_item is None:
        break
      if player.material >= chosen_item.cost:
        play_sound("inventory.mp3")
        player.material -= chosen_item.cost
        player.inventory.append(deepcopy(chosen_item.item))
        chosen_item.stock -= 1
        print(f"You bought {chosen_item.item.render()}")
      else:
        print("You cannot afford that item")
      self.shop_items = [item for item in self.shop_items if item.stock > 0]