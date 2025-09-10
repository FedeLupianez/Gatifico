import arcade
from .Player import Player


class Seller(arcade.Sprite):
    Texture_path = "src/resources/Seller/"

    def __init__(self, items: dict[str, dict[str, int]]) -> None:
        # super().__init__(Seller.Texture_path, scale=1)
        self.items: dict[str, dict[str, int]] = items

    def sell_item(self, player: Player, item: str) -> None:
        if item not in self.items:
            return
        quantity = self.items[item].get("quantity", 1)
        price = self.items[item].get("price", 1)
        player.add_to_inventory(item, quantity)
        try:
            player.pay(price)
        except ValueError as e:
            print(e)
            return
