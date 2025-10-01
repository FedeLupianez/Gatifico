from items.Item import Item
import random


def random_item(center_x: float = 0, center_y: float = 0) -> Item:
    item = Item(
        name=random.choice(list(Item._resources.keys())),
        quantity=random.randint(0, 64),
    )
    if center_x and center_y:
        item.center_x, item.center_y = center_x, center_y
    return item
