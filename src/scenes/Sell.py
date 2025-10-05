import arcade

import Constants
from .View import View
from characters.Player import Player
from .utils import add_containers_to_list, apply_filter
from items.Item import Item
from items.Container import Container
import random


class Sell(View):
    CONTAINER_SIZE = 50
    ITEM_SCALE = 3
    DISTANCE_BETWEEN_CONTAINERS = 75

    def __init__(self, antique_view) -> None:
        super().__init__(background_url=None, tilemap_url=None)
        self.player = Player()
        self.window.set_mouse_visible(True)
        self.antique_view: View = antique_view
        self.next_item_id = 0

        background_image = antique_view.get_screenshot()
        self.background_image = arcade.texture.Texture.create_empty(
            "world", size=(background_image.width, background_image.height)
        )
        self.background_image.image = apply_filter(
            background_image, Constants.Filter.DARK
        )
        self.background_rect = arcade.rect.Rect(
            left=0,
            top=0,
            bottom=0,
            right=0,
            width=Constants.Game.SCREEN_WIDTH,
            height=Constants.Game.SCREEN_HEIGHT,
            x=Constants.Game.SCREEN_CENTER_X,
            y=Constants.Game.SCREEN_CENTER_Y,
        )

        all_minerals = list(Item._resources.keys())
        num_seller_items = random.randint(1, len(all_minerals))
        seller_item_names = random.sample(all_minerals, num_seller_items)
        self.seller_items = {name: random.randint(1, 20) for name in seller_item_names}

        self.item_to_sell: Item | None = None
        self._item_mouse_text = arcade.Text(
            text="",
            x=0,
            y=0,
            anchor_x="center",
            anchor_y="center",
            align="center",
        )
        self._item_mouse_bg = arcade.rect.Rect(0, 0, 0, 0, 0, 0, 0, 0)
        self.setup()

    def setup(self) -> None:
        self._setup_lists()
        self._setup_containers()
        self._setup_seller_items()
        self._setup_player_items()

    def _setup_lists(self) -> None:
        self.seller_containers = arcade.SpriteList()
        self.seller_item_sprites = arcade.SpriteList()
        self.player_containers = arcade.SpriteList()
        self.player_item_sprites = arcade.SpriteList()
        self.item_texts: list[arcade.Text] = []

    def _setup_containers(self) -> None:
        # Contenedores del jugador
        player_positions = [
            (100 + Sell.DISTANCE_BETWEEN_CONTAINERS * i, 100)
            for i in range(Constants.PlayerConfig.MAX_ITEMS_IN_INVENTORY)
        ]
        cant_containers = len(player_positions)
        screen_center_x = self.window.width * 0.5
        mid_container = cant_containers // 2

        if cant_containers > 0:
            player_positions[mid_container] = (screen_center_x, 100)
            for i in range(mid_container - 1, -1, -1):
                last_pos = player_positions[i + 1]
                player_positions[i] = (
                    last_pos[0] - Sell.DISTANCE_BETWEEN_CONTAINERS,
                    100,
                )

            for i in range(mid_container + 1, cant_containers):
                last_pos = player_positions[i - 1]
                player_positions[i] = (
                    last_pos[0] + Sell.DISTANCE_BETWEEN_CONTAINERS,
                    100,
                )

        add_containers_to_list(
            point_list=player_positions,
            list_to_add=self.player_containers,
            container_size=Sell.CONTAINER_SIZE,
        )
        # Contenedores del vendedor :
        positions = [
            (400 + Sell.DISTANCE_BETWEEN_CONTAINERS * i, 500)
            for i in range(len(self.seller_items))
        ]
        add_containers_to_list(
            point_list=positions,
            list_to_add=self.seller_containers,
            container_size=Sell.CONTAINER_SIZE,
        )

    def _setup_player_items(self) -> None:
        # Items del jugador
        for index, (name, quantity) in enumerate(self.player.get_inventory().items()):
            container: Container = self.player_containers[index]
            container.item_placed = True
            new_item = Item(name=name, quantity=quantity, scale=Sell.ITEM_SCALE)
            new_item.id = self.next_item_id
            self.next_item_id += 1
            new_item.change_container(container.id)
            new_item.change_position(container.center_x, container.center_y)
            self.item_texts.append(self._create_item_text(new_item))
            self.player_item_sprites.append(new_item)

    def _setup_seller_items(self) -> None:
        # Items del vendedor
        for index, (name, quantity) in enumerate(self.seller_items.items()):
            container: Container = self.seller_containers[index]
            container.item_placed = True
            new_item = Item(name=name, quantity=quantity, scale=Sell.ITEM_SCALE)
            new_item.price = new_item.price * new_item.quantity
            new_item.id = self.next_item_id
            self.next_item_id += 1
            new_item.change_container(container.id)
            new_item.change_position(container.center_x, container.center_y)
            self.item_texts.append(self._create_item_text(new_item, owner="seller"))
            self.seller_item_sprites.append(new_item)

    def _find_element(self, list_to_find, attr: str, target):
        for element in list_to_find:
            if getattr(element, attr) == target:
                return element
        return None

    def _create_item_text(
        self, item: Item, fontSize: int = 11, owner: str = "player"
    ) -> arcade.Text:
        content = (
            f"{item.quantity} ${item.price}"
            if owner == "seller"
            else f"{item.quantity}"
        )
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

    def _update_texts(self) -> None:
        # Items del jugador
        for item in self.player_item_sprites:
            text = self._find_element(self.item_texts, attr="id", target=item.id)
            if text:
                text.text = f"{item.quantity}"

    def remove_player_item(self, item: Item) -> None:
        self.player_item_sprites.remove(item)
        text = self._find_element(self.item_texts, attr="id", target=item.id)
        if text:
            self.item_texts.remove(text)
        container = self._find_element(
            self.player_containers, attr="id", target=item.container_id
        )
        if container:
            self.player_containers.remove(container)
        del container, text

    def player_purchase_item(self, item: Item) -> None:
        # El jugador compra
        try:
            self.player.pay(item.price)
            self.player.add_to_inventory(item.name, item.quantity)
            self.seller_items.pop(item.name)
            print(f"item comprado por el jugador : {item.name} | {item.price}")
        except ValueError as e:
            print(e)
            return
        self.item_to_sell = None
        self.setup()

    def player_sell_item(self, item: Item) -> None:
        # El jugadr vende
        if not self.player.remove_from_inventory(item.name, 1):
            print("El jugador no tenía ese item")
            return
        print(f"item vendido por el jugador : {item.name} | {item.price}")
        item.quantity -= 1
        self.player.add_coins(item.price)
        if item.quantity == 0:
            self.remove_player_item(item)
        self._update_texts()
        if item.name not in self.seller_items:
            print("ese item no lo tenia el vendedor")
            self.seller_items[item.name] = 0
        self.seller_items[item.name] += 1

    def draw_background(self) -> None:
        if self.background_image:
            arcade.draw_texture_rect(
                self.background_image, self.background_rect, pixelated=True
            )

    def on_draw(self) -> None:
        self.camera.use()
        self.clear()
        self.draw_background()
        self.seller_containers.draw(pixelated=True)
        self.seller_item_sprites.draw(pixelated=True)
        self.player_containers.draw(pixelated=True)
        self.player_item_sprites.draw(pixelated=True)
        for text in self.item_texts:
            text.draw()
        if self._item_mouse_text.text:
            arcade.draw_rect_filled(self._item_mouse_bg, arcade.color.BLACK)
            self._item_mouse_text.draw()

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
            self.player_purchase_item(self.item_to_sell)
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            temp = arcade.get_sprites_at_point((x, y), self.player_item_sprites)
            if not temp:
                return
            assert isinstance(temp[-1], Item), "No se encontró el item"
            item: Item = temp[-1]
            self.player_sell_item(item)

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        if sprites := arcade.get_sprites_at_point((x, y), self.seller_item_sprites):
            text_width = len(sprites[0].name) * self._item_mouse_text.font_size
            self._item_mouse_text.text = sprites[0].name or ""
            self._item_mouse_text.x = x
            self._item_mouse_text.y = y + 15
            self._item_mouse_bg = arcade.rect.Rect(
                width=text_width,
                height=self._item_mouse_text.font_size + 5,
                x=x,
                y=y + 15,
                left=0,
                right=0,
                top=0,
                bottom=0,
            )
            return
        if sprites := arcade.get_sprites_at_point((x, y), self.player_item_sprites):
            text_width = len(sprites[0].name) * self._item_mouse_text.font_size
            self._item_mouse_text.text = sprites[0].name or ""
            self._item_mouse_text.x = x
            self._item_mouse_text.y = y + 15
            self._item_mouse_bg = arcade.rect.Rect(
                width=text_width,
                height=self._item_mouse_text.font_size + 5,
                x=x,
                y=y + 15,
                left=0,
                right=0,
                top=0,
                bottom=0,
            )
            return
        self._item_mouse_text.text = ""

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.ESCAPE:
            self.window.show_view(self.antique_view)
            self.clean_up()

    def clean_up(self) -> None:
        del self.item_to_sell
        del self.item_texts
        del self.player_item_sprites
        del self.player_containers
        del self.seller_item_sprites
        del self.seller_containers
        del self.seller_items
        del self.player
