import arcade
import arcade.gui
import Constants
from scenes.View import View
from characters.Player import Player
import DataManager
from typing import Dict
from Constants import Filter, Game
from items.Container import Container
from items.Item import Item
from .utils import add_containers_to_list, del_references_list, get_result, apply_filter

Combinations: Dict[str, Dict[str, str]] = DataManager.loadData("CombinationsTest.json")


class MixTable(View):
    # centros de los contenedores
    MIXING_Y = 240
    MIXING_ITEMS_POSITIONS: list[tuple[int, int]] = [
        (475, MIXING_Y),
        (786, MIXING_Y),
    ]
    RESULT_CONTAINER_POSITION = (530, 448)
    CONTAINER_SIZE = 50

    ITEMS_INIT: tuple[int, int] = (400, 145)
    ITEM_SCALE = 2

    def __init__(self, background_scene: View):
        super().__init__(background_url=None, tilemap_url=None)
        background_image = background_scene.get_screenshot()

        self.background_image = arcade.texture.Texture.create_empty(
            "table_bg", size=(background_image.width, background_image.height)
        )
        self.background_image.image = apply_filter(background_image, Filter.DARK)

        bg_image = arcade.Sprite(DataManager.get_path("mix_table.png"))
        bg_image.center_x = Constants.Game.SCREEN_CENTER_X
        bg_image.center_y = Constants.Game.SCREEN_CENTER_Y
        bg_image.width = int(Game.SCREEN_CENTER_X + (Game.SCREEN_CENTER_X / 4))
        bg_image.height = Game.SCREEN_HEIGHT - 200
        self.background_sprites.append(bg_image)
        del bg_image

        # Init de la clase
        self.background_scene = background_scene
        self.player = Player()
        self.items: dict = self.player.get_inventory()
        self.next_item_id: int = 0

        # Configuraciones de cámara
        self.window.set_mouse_visible(True)
        self.camera.zoom = 1
        # Listas de sprites
        self.item_sprites = arcade.SpriteList()
        self.container_sprites: arcade.SpriteList = arcade.SpriteList()
        self.item_texts: list[arcade.Text] = []

        self.inventory_sprite = arcade.Sprite(
            DataManager.get_path("inventory_tools.png"), scale=3
        )
        self.inventory_sprite.scale_y = 3.2
        self.inventory_sprite.center_x = Game.SCREEN_CENTER_X
        self.inventory_sprite.center_y = self.ITEMS_INIT[1]
        self.background_sprites.append(self.inventory_sprite)

        self.rect_table = arcade.rect.Rect(
            left=Game.SCREEN_CENTER_X - (Game.SCREEN_CENTER_X / 3),
            right=Game.SCREEN_CENTER_X + (Game.SCREEN_CENTER_X / 3),
            top=Game.SCREEN_CENTER_Y + (Game.SCREEN_CENTER_Y * 0.5),
            bottom=Game.SCREEN_CENTER_Y - (Game.SCREEN_CENTER_Y * 0.5),
            width=int(Game.SCREEN_CENTER_X + (Game.SCREEN_CENTER_X / 3)),
            height=Game.SCREEN_CENTER_Y,
            x=Game.SCREEN_CENTER_X,
            y=Game.SCREEN_CENTER_Y,
        )
        self.background_rect = arcade.rect.Rect(
            left=0,
            right=0,
            top=0,
            bottom=0,
            width=Game.SCREEN_WIDTH,
            height=Game.SCREEN_HEIGHT,
            x=Game.SCREEN_CENTER_X,
            y=Game.SCREEN_CENTER_Y,
        )

        # cosas de la UI
        self.UIManager = arcade.gui.UIManager(self.window)
        self.UIManager.enable()
        result_x, result_y = self.RESULT_CONTAINER_POSITION
        self.mix_button = arcade.gui.UIFlatButton(
            x=result_x + 50,
            y=result_y - 160,
            text="Combinar",
        )
        self.mix_button.style["normal"].bg = arcade.color.BLACK
        self.mix_button.style["hover"].bg = arcade.color.GRAY

        @self.mix_button.event("on_click")
        def on_click(event):
            self._load_item_result()

        self.UIManager.add(self.mix_button)

        self.is_mouse_active: bool = False
        self.item_to_move: Item | None = None
        self.result_place: Container

    def _find_element(self, list_to_find, attr: str, target):
        """
        Función para buscar un elemento de una lista que cumpla con un requisito
        Args:
            func (Callable): Función que devuelve True si el elemento cumple con el requisito
            list_to_find (list): Lista de elementos donde buscar
        """
        result = list(
            filter(self.item_contains_attr(attr=attr, target=target), list_to_find)
        )
        if result:
            return result[0]

    def item_contains_attr(self, attr: str, target):
        def is_item(sprite):
            if hasattr(sprite, attr):
                return getattr(sprite, attr) == target
            else:
                return False

        return is_item

    def _setup_containers(self) -> None:
        positions = [
            ((self.ITEMS_INIT[0] + 75 * i), self.ITEMS_INIT[1])
            for i in range(len(self.items))
        ]
        # Centrar los containers con la pantalla :
        # centro de la pantalla
        cant_containers = len(positions)
        mid_container = int(cant_containers * 0.5)
        positions[mid_container] = (
            int(Constants.Game.SCREEN_CENTER_X),
            self.ITEMS_INIT[1] + 5,
        )

        for i in range(mid_container - 1, -1, -1):
            last_pos = positions[i + 1]
            positions[i] = (last_pos[0] - 60, self.ITEMS_INIT[1] + 5)

        for i in range(mid_container + 1, cant_containers):
            last_pos = positions[i - 1]
            positions[i] = (last_pos[0] + 60, self.ITEMS_INIT[1] + 5)

        add_containers_to_list(
            point_list=positions,
            list_to_add=self.container_sprites,
            container_size=self.CONTAINER_SIZE,
        )
        add_containers_to_list(
            point_list=self.MIXING_ITEMS_POSITIONS,
            list_to_add=self.container_sprites,
            container_size=self.CONTAINER_SIZE,
        )

        # Container del resultado :
        result_x, result_y = self.RESULT_CONTAINER_POSITION

        self.result_place = Container(
            width=self.CONTAINER_SIZE,
            height=self.CONTAINER_SIZE,
            center_x=result_x + 100,
            center_y=result_y,
            color=arcade.color.BABY_BLUE,
        )
        self.result_place.id = len(self.container_sprites)
        self.container_sprites.append(self.result_place)

    def _generate_item_sprites(self) -> None:
        for index, (name, quantity) in enumerate(self.items.items()):
            container: Container = self.container_sprites[index]
            newItem = Item(name=name, quantity=quantity, scale=self.ITEM_SCALE)
            newItem.id = self.next_item_id
            self.next_item_id += 1
            newItem.change_container(container.id)
            newItem.change_position(container.center_x, container.center_y)
            self.item_texts.append(self._create_item_text(newItem))
            self.item_sprites.append(newItem)

    def _create_item_text(self, item: Item) -> arcade.Text:
        content = f"{item.quantity}"
        text_sprite = arcade.Text(
            text=content,
            font_size=11,
            x=item.center_x,
            y=item.center_y - ((item.height * 0.5) + 15),
            anchor_x="center",
            anchor_y="baseline",
            color=arcade.color.BLACK,
        )
        setattr(text_sprite, "id", item.id)
        return text_sprite

    def _update_texts_position(self) -> None:
        for item in self.item_sprites:
            actual_text = self._find_element(
                attr="id",
                target=item.id,
                list_to_find=self.item_texts,
            )
            if not (actual_text):
                return
            actual_text.position = (
                item.center_x,
                item.center_y - (item.height * 0.5 + 15),
            )

    def _sync_item_text(self) -> None:
        for text_sprite in self.item_texts:
            item = self._find_element(
                attr="id",
                target=text_sprite.id,
                list_to_find=self.item_sprites,
            )
            if not item:
                continue
            expected = f"{item.quantity}"
            if text_sprite.text != expected:
                text_sprite.text = expected

    def _load_item_result(self) -> None:
        input_1, input_2 = self.container_sprites[-3:-1]

        item_1 = self._find_element(
            attr="container_id",
            target=input_1.id,
            list_to_find=self.item_sprites,
        )
        item_2 = self._find_element(
            attr="container_id",
            target=input_2.id,
            list_to_find=self.item_sprites,
        )

        if not (item_1 and item_2):
            return

        result = get_result(item_1, item_2, Combinations)
        if not result:
            return

        old_result = self._find_element(
            attr="container_id",
            target=self.result_place.id,
            list_to_find=self.item_sprites,
        )
        if not old_result:
            sprite: Item = Item(result, quantity=1, scale=self.ITEM_SCALE)
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
            if item.quantity != 0:
                return
            if item_text := self._find_element(
                list_to_find=self.item_texts, attr="id", target=item.id
            ):
                self.item_texts.remove(item_text)
                self.item_sprites.remove(item)
                container.item_placed = False

    def save_result(self) -> None:
        # Guardo los items generados por el jugador
        # Veo si hay items en las casillas de resultados
        new_inventory: dict[str, int] = {}

        for container in self.container_sprites:
            item = self._find_element(
                self.item_sprites, attr="container_id", target=container.id
            )
            if not item:
                continue
            if not new_inventory.get(item.name):
                new_inventory[item.name] = item.quantity
            else:
                new_inventory[item.name] += item.quantity
        self.player.inventory = new_inventory

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

    def draw_background(self) -> None:
        if self.background_image:
            arcade.draw_texture_rect(
                self.background_image,
                rect=self.background_rect,
                pixelated=True,
            )

    def on_draw(self):
        self.clear()  # limpia la pantalla
        self.camera.use()
        self.draw_background()

        self.background_sprites.draw(pixelated=True)
        self.item_sprites.draw(pixelated=True)
        self.ui_sprites.draw(pixelated=True)
        for text in self.item_texts:
            text.draw()
        if self._item_mouse_text.text:
            self._item_mouse_text.draw()
        self.UIManager.draw(pixelated=True)

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.ESCAPE:
            self.save_result()
            self.clean_up()
            self.window.show_view(self.background_scene)
            del self.background_scene

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
        assert new_container, "No hay container"
        assert old_container, "no tenia container"

        if new_container.id == old_container.id:
            self._reset_sprite_position(self.item_to_move)
            self.item_to_move = None
            return

        if not (new_container.item_placed):
            self._move_sprite_to_container(self.item_to_move, new_container)
            old_container.item_placed = False
            new_container.item_placed = True
            self.item_to_move = None
            return

        other_item = self._find_element(
            self.item_sprites, attr="container_id", target=new_container.id
        )
        if not other_item:
            return

        if not self.item_to_move.__equals__(other_item):
            self._reset_sprite_position(self.item_to_move)
            self.item_to_move = None
            return

        self.item_to_move.quantity += other_item.quantity
        other_item.__del__()
        if text := self._find_element(
            list_to_find=self.item_texts, attr="id", target=other_item.id
        ):
            self.item_texts.remove(text)
            self.item_to_move.change_container(newContainerId=other_item.container_id)
            self._move_sprite_to_container(self.item_to_move, new_container)
            self.item_to_move = None

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> bool | None:
        if self.item_to_move:
            # Cambio la posición del sprite a la del mouse
            self.item_to_move.change_position(x, y)
        self.item_hover((x, y), self.item_sprites)

    def clean_up(self) -> None:
        del self.background_image
        del_references_list(self.container_sprites)
        del self.container_sprites
        del_references_list(self.item_sprites)
        del self.item_sprites
        del self.item_to_move
        del self.is_mouse_active
        del self.UIManager
        del self.item_texts
