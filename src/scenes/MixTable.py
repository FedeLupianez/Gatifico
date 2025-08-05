import arcade
import arcade.gui
from scenes.View import View
from characters.Player import Player
import DataManager
from typing import Callable, Dict
from Constants import SignalCodes
from items.Container import Container
from items.Item import Item
from .utils import add_containers_to_list, del_references_list, get_result

Combinations: Dict[str, Dict[str, str]] = DataManager.loadData("CombinationsTest.json")


# centros de los contenedores
ITEMS_POSITIONS: list[tuple[int, int]] = [(100, 100), (175, 100), (250, 100)]
MIXING_ITEMS_POSITIONS: list[tuple[int, int]] = [(300, 300), (400, 300)]
CONTAINER_SIZE = 50

ITEMS_INIT: tuple[int, int] = (100, 100)


class MixTable(View):
    def __init__(self, callback: Callable[[int, str], None], player: Player):
        backgroundUrl = ":resources:Background/Texture/TX Plant.png"
        super().__init__(background_url=backgroundUrl, tilemap_url=None)

        # Init de la clase
        self.callback = callback
        self.player = player
        self.items: dict = player.get_inventory() or {"rubi": 4, "stone": 3, "water": 5}
        self.next_item_id: int = 0

        # Configuraciones de cámara
        self.window.set_mouse_visible(True)
        self.camera.zoom = 1
        # Listas de sprites
        self.background_sprites = arcade.SpriteList()
        self.item_sprites = arcade.SpriteList()
        self.container_sprites: arcade.SpriteList = arcade.SpriteList()
        self.item_texts: list[arcade.Text] = []

        # cosas de la UI
        self.UIManager = arcade.gui.UIManager(self.window)
        self.UIManager.enable()
        result_x, result_y = MIXING_ITEMS_POSITIONS[-1]
        self.mix_button = arcade.gui.UIFlatButton(
            x=result_x + 50,
            y=result_y - 100,
            text="Combinar",
        )

        @self.mix_button.event("on_click")
        def on_click(event):
            self._load_item_result()

        self.UIManager.add(self.mix_button)

        self.is_mouse_active: bool = False
        self.item_to_move: Item | None = None
        self.result_place: Container

    def _find_item_with_containerId(self, container_id: int, sprite_index: int = 0):
        if sprite_index == len(self.item_sprites):
            return None
        sprite: Item = self.item_sprites[sprite_index]
        if sprite.container_id == container_id:
            return sprite
        return self._find_item_with_containerId(container_id, sprite_index + 1)

    def _find_item_with_id(self, id: int, listToFind: list, sprite_index: int = 0):
        if sprite_index == len(listToFind):
            return None
        sprite = listToFind[sprite_index]
        if sprite.id == id:
            return sprite
        return self._find_item_with_id(id, listToFind, sprite_index + 1)

    def _setup_containers(self) -> None:
        positions = [
            (ITEMS_INIT[0] + 75 * i, ITEMS_INIT[1]) for i in range(len(self.items))
        ]

        add_containers_to_list(
            point_list=positions,
            list_to_add=self.container_sprites,
            container_size=CONTAINER_SIZE,
        )
        add_containers_to_list(
            point_list=MIXING_ITEMS_POSITIONS,
            list_to_add=self.container_sprites,
            container_size=CONTAINER_SIZE,
        )

        # Container del resultado :
        result_x, result_y = MIXING_ITEMS_POSITIONS[-1]

        self.result_place = Container(
            width=CONTAINER_SIZE,
            height=CONTAINER_SIZE,
            center_x=result_x + 100,
            center_y=result_y,
            color=arcade.color.BABY_BLUE,
        )
        self.result_place.id = len(self.container_sprites)
        self.container_sprites.append(self.result_place)

    def _generate_item_sprites(self) -> None:
        for index, (name, quantity) in enumerate(self.items.items()):
            container: Container = self.container_sprites[index]
            newItem = Item(name=name, quantity=quantity, scale=3)
            newItem.id = self.next_item_id
            self.next_item_id += 1
            newItem.change_container(container.id)
            newItem.change_position(container.center_x, container.center_y)
            self.item_texts.append(self._create_item_text(newItem))
            self.item_sprites.append(newItem)

    def _create_item_text(self, item: Item) -> arcade.Text:
        content = f"{item.name} x {item.quantity}"
        text_sprite = arcade.Text(
            text=content,
            font_size=11,
            x=item.center_x,
            y=item.center_y - ((item.height / 2) + 15),
            anchor_x="center",
            anchor_y="baseline",
        )
        text_sprite.id = item.id
        return text_sprite

    def _update_texts_position(self) -> None:
        for item in self.item_sprites:
            actual_text: arcade.Sprite | None = self._find_item_with_id(
                item.id, self.item_texts
            )
            if not (actual_text):
                return
            actual_text.x = item.center_x
            actual_text.y = item.center_y - (item.height / 2 + 15)

    def _sync_item_text(self) -> None:
        for text_sprite in self.item_texts:
            item = self._find_item_with_id(text_sprite.id, self.item_sprites)
            if item is None:
                print("item no encontrado")
                continue
            expected = f"{item.name} x {item.quantity}"
            if text_sprite.text != expected:
                text_sprite.text = expected

    def _load_item_result(self) -> None:
        input_1, input_2 = self.container_sprites[-3:-1]
        item_1 = self._find_item_with_containerId(input_1.id)
        item_2 = self._find_item_with_containerId(input_2.id)

        if not (item_1 and item_2):
            return

        result = get_result(item_1, item_2, Combinations)
        if not result:
            return

        old_result: arcade.Sprite | None = self._find_item_with_containerId(
            self.result_place.id
        )
        if not old_result:
            sprite: Item = Item(result, quantity=1, scale=3)
            sprite.change_position(
                self.result_place.center_x, self.result_place.center_y
            )
            sprite.id = self.next_item_id
            self.next_item_id += 1
            sprite.change_container(self.result_place.id)
            self.item_texts.append(self._create_item_text(sprite))
            self.item_sprites.append(sprite)
        else:
            old_result.quantity += 1

        for item, container in zip((item_1, item_2), (input_1, input_2)):
            item.quantity -= 1
            if item.quantity == 0:
                self.item_texts.remove(
                    self._find_item_with_id(item.id, self.item_texts)
                )
                self.item_sprites.remove(item)
                container.item_placed = False

    def _reset_sprite_position(self, sprite: Item) -> None:
        original_container = self.container_sprites[sprite.container_id]
        sprite.change_position(original_container.center_x, original_container.center_y)

    def _move_sprite_to_container(self, sprite: Item, container: Container) -> None:
        sprite.change_position(container.center_x, container.center_y)
        sprite.change_container(container.id)

    def on_show_view(self) -> None:
        self._setup_containers()
        self._generate_item_sprites()
        super().on_show_view()

    def on_update(self, delta_time: float):
        self._sync_item_text()
        self._update_texts_position()

    def on_draw(self):
        self.clear()  # limpia la pantalla
        self.camera.use()
        self.background_sprites.draw(pixelated=True)
        self.container_sprites.draw(pixelated=True)
        self.item_sprites.draw(pixelated=True)
        for text in self.item_texts:
            text.draw()
        self.UIManager.draw(pixelated=True)

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.SPACE:
            self.callback(SignalCodes.CHANGE_VIEW, "MENU")

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.is_mouse_active = True
            sprites = arcade.get_sprites_at_point((x, y), self.item_sprites)
            self.item_to_move = sprites[-1] if sprites else None

    def on_mouse_release(
        self, x: int, y: int, button: int, modifiers: int
    ) -> bool | None:
        if button != arcade.MOUSE_BUTTON_LEFT or not self.is_mouse_active:
            return

        self.is_mouse_active = False  # desactivo el click

        if not self.item_to_move:
            return

        collisions: list[Container] = arcade.check_for_collision_with_list(
            self.item_to_move, self.container_sprites
        )

        if not collisions:
            self._reset_sprite_position(self.item_to_move)
            self.item_to_move = None
            return

        new_container: Container = collisions[0]
        old_container: Container = self.container_sprites[
            self.item_to_move.container_id
        ]

        if new_container.id == old_container.id:
            self._reset_sprite_position(self.item_to_move)
            self.item_to_move = None
            return

        if not (new_container.item_placed):
            self._move_sprite_to_container(self.item_to_move, new_container)
            old_container.item_placed = False
            new_container.item_placed = True
        else:
            item: Item = self._find_item_with_containerId(new_container.id)
            if item.name == self.item_to_move.name:
                text: arcade.Sprite = self._find_item_with_id(item.id, self.item_texts)
                self._move_sprite_to_container(self.item_to_move, new_container)
                old_container.item_placed = False
                new_container.item_placed = True
                self.item_to_move.quantity += item.quantity
                self.item_sprites.remove(item)
                self.item_texts.remove(text)

            self._reset_sprite_position(self.item_to_move)

        self.item_to_move = None  # Pongo que no hay nngún sprite qe mover

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> bool | None:
        if self.item_to_move:
            # Cambio la posición del sprite a la del mouse
            self.item_to_move.change_position(x, y)

    def clean_up(self) -> None:
        del_references_list(self.background_sprites)
        del self.background_sprites
        del_references_list(self.container_sprites)
        del self.container_sprites
        del_references_list(self.item_sprites)
        del self.item_sprites
        del self.item_to_move
        del self.is_mouse_active
        del self.callback
        del self.UIManager
        del self.item_texts
