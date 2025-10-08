from items.Item import Item
import random
from Constants import PlayerConfig


def random_item(center_x: float = 0, center_y: float = 0, quantity=None) -> Item:
    if not quantity:
        quantity = random.randint(0, PlayerConfig.MAX_ITEMS_CANT)
    item = Item(
        name=random.choice(list(Item._resources.keys())),
        quantity=quantity,
    )
    if center_x and center_y:
        item.center_x, item.center_y = center_x, center_y
    return item
