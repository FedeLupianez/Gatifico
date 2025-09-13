from logging import exception
from typing import Callable
import arcade
from .View import View
from characters.Player import Player
from .utils import add_containers_to_list
from items.Item import Item
from items.Container import Container
import random


class Sell(View):
    def __init__(
        self,
        callback: Callable,
        player: Player,
    ) -> None:
        super().__init__(background_url=None, tilemap_url=None)
        self.player = player
        self.window.set_mouse_visible(True)
        self.callback = callback
        self.next_item_id = 0

        all_minerals = list(Item.MineralsResources.keys())
        num_seller_items = random.randint(1, len(all_minerals))
        seller_item_names = random.sample(all_minerals, num_seller_items)
        self.seller_items = {
            name: random.randint(1, 20) for name in seller_item_names
        }

        self.item_to_sell: Item | None = None
        self.setup()

    def setup(self) -> None:
        self._setup_lists()
        self._setup_containers()
        self._setup_items()

    def _setup_lists(self) -> None:
        self.seller_containers = arcade.SpriteList()
        self.seller_item_sprites = arcade.SpriteList()
        self.player_containers = arcade.SpriteList()
        self.player_item_sprites = arcade.SpriteList()
        self.item_texts: list[arcade.Text] = []

    def _setup_containers(self) -> None:
        # Contenedores del jugador
        player_positions = [
            (100 + 75 * i, 100) for i in range(len(self.player.get_inventory().items()))
        ]
        cant_containers = len(player_positions)
        screen_center_x = self.window.width * 0.5
        mid_container = cant_containers // 2

        if cant_containers > 0:
            player_positions[mid_container] = (screen_center_x, 100)
            for i in range(mid_container - 1, -1, -1):
                last_pos = player_positions[i + 1]
                player_positions[i] = (last_pos[0] - 75, 100)

            for i in range(mid_container + 1, cant_containers):
                last_pos = player_positions[i - 1]
                player_positions[i] = (last_pos[0] + 75, 100)

        add_containers_to_list(
            point_list=player_positions,
            list_to_add=self.player_containers,
            container_size=50,
        )
        # Contenedores del vendedor :
        positions = [(400 + 75 * i, 500) for i in range(len(self.seller_items))]
        add_containers_to_list(
            point_list=positions,
            list_to_add=self.seller_containers,
            container_size=50,
        )

    def _setup_items(self) -> None:
        # Items del jugador
        for index, (name, quantity) in enumerate(self.player.get_inventory().items()):
            container: Container = self.player_containers[index]
            container.item_placed = True
            new_item = Item(name=name, quantity=quantity, scale=3)
            new_item.id = self.next_item_id
            self.next_item_id += 1
            new_item.change_container(container.id)
            new_item.change_position(container.center_x, container.center_y)
            self.item_texts.append(self._create_item_text(new_item))
            self.player_item_sprites.append(new_item)
        # Items del vendedor
        for index, (name, quantity) in enumerate(self.seller_items.items()):
            container: Container = self.seller_containers[index]
            container.item_placed = True
            new_item = Item(name=name, quantity=quantity, scale=3)
            new_item.id = self.next_item_id
            self.next_item_id += 1
            new_item.change_container(container.id)
            new_item.change_position(container.center_x, container.center_y)
            self.item_texts.append(self._create_item_text(new_item))
            self.seller_item_sprites.append(new_item)

    def _create_item_text(self, item: Item, fontSize: int = 11) -> arcade.Text:
        content = f"{item.quantity} ${item.price}"
        text_sprite = arcade.Text(
            text=content,
            font_size=fontSize,
            x=item.center_x,
            y=item.center_y - ((item.height * 0.5) + 15),
            anchor_x="center",
            anchor_y="baseline",
        )
        text_sprite.id = item.id
        return text_sprite

    def on_draw(self) -> None:
        self.clear()
        self.seller_containers.draw(pixelated=True)
        self.seller_item_sprites.draw(pixelated=True)
        self.player_containers.draw(pixelated=True)
        self.player_item_sprites.draw(pixelated=True)
        for text in self.item_texts:
            text.draw()

    def player_sell_item(self, item: Item) -> None:
        # El jugador vende
        try:
            self.player.pay(item.price)
            self.player.add_to_inventory(item.name, item.quantity)
            self.seller_items.pop(item.name)
            print(f"item vendido : {item.name} | {item.price}")
        except ValueError as e:
            print(e)
            return
        self.item_to_sell = None
        self.setup()

    def on_mouse_press(
        self, x: int, y: int, button: int, modifiers: int
    ) -> bool | None:
        if button == arcade.MOUSE_BUTTON_LEFT:
            temp = arcade.get_sprites_at_point((x, y), self.seller_item_sprites)
            if not temp:
                self.item_to_sell = None
                return

            assert isinstance(temp[-1], Item), "No se encontró el item"
            self.item_to_sell = temp[-1]
            self.player_sell_item(self.item_to_sell)
