import arcade
import arcade.gui
from arcade.types import RGBA
from scenes.View import View
from characters.Player import Player
import DataManager
from typing import Callable, Dict, Literal
from Constants import SignalCodes

# Cargo los datos de los sprites de los minerales
MineralsResources: Dict[
    str,
    Dict[
        Literal["big", "mid", "small", "item"],
        Dict[Literal["path", "touches"], str | int],
    ],
] = DataManager.loadData("Minerals.json")

Combinations: Dict[str, Dict[str, str]] = DataManager.loadData("CombinationsTest.json")


# centros de los contenedores
ITEMS_POSITIONS: list[tuple[int, int]] = [(100, 100), (175, 100), (250, 100)]
MIXING_ITEMS_POSITIONS: list[tuple[int, int]] = [(300, 300), (400, 300)]
CONTAINER_SIZE = 50

ITEMS_INIT: list[tuple[int, int]] = [(100, 100)]


def add_containers_to_list(
    pointList: list[tuple[int, int]], listToAdd: arcade.SpriteList
) -> None:
    for x, y in pointList:
        tempSprite = Container(
            width=CONTAINER_SIZE,
            height=CONTAINER_SIZE,
            center_x=x,
            center_y=y,
            color=arcade.color.GRAY,
        )
        tempSprite.item_placed = ""
        tempSprite.container_id = len(listToAdd)
        listToAdd.append(tempSprite)


class Container(arcade.SpriteSolidColor):
    def __init__(
        self,
        width: int,
        height: int,
        center_x: float,
        center_y: float,
        color: RGBA = arcade.color.GRAY,
    ) -> None:
        super().__init__(
            width=width,
            height=height,
            center_x=center_x,
            center_y=center_y,
            color=color,
        )
        self.type: str = ""
        self.item_placed: str = ""
        self.item_cant: int = 0
        self.container_id: int = -1

    def setItem(self, itemName: str, count: int) -> None:
        self.item_placed = itemName
        self.item_cant = count

    def clear_item(self) -> None:
        self.item_placed = ""
        self.item_cant = 0

    def add_quantity(self, cant: int) -> None:
        self.item_cant += cant


class MixTable(View):
    def __init__(self, callback: Callable[[int, str], None], player: Player):
        backgroundUrl = ":resources:Background/Texture/TX Plant.png"
        super().__init__(backgroundUrl=backgroundUrl, tileMapUrl=None)

        # Init de la clase
        self.callback = callback
        self.player = player
        self.items: dict = player.getInventory() or {"rubi": 4, "rock": 3, "water": 5}

        # Configuraciones de cámara
        self.window.set_mouse_visible(True)
        self.camera.zoom = 1

        # Listas de sprites
        self.spriteList = arcade.SpriteList()
        self.inventorySrites = arcade.SpriteList()
        self.itemContainers: arcade.SpriteList = arcade.SpriteList()
        self.textList: arcade.SpriteList = arcade.SpriteList()

        # cosas de la UI
        self.UIManager = arcade.gui.UIManager(self.window)
        self.UIManager.enable()
        result_x, result_y = MIXING_ITEMS_POSITIONS[-1]
        self.mixButton = arcade.gui.UIFlatButton(
            x=result_x + 50,
            y=result_y - 100,
            text="Combinar",
        )

        @self.mixButton.event("on_click")
        def on_click(event):
            self._load_item_result()

        self.UIManager.add(self.mixButton)

        self.is_mouse_active: bool = False
        self.spriteToMove = None
        self.resultPlace: Container

    def _setup_containers(self) -> None:
        for i in range(len(self.items) - 1):
            x, y = ITEMS_INIT[-1]
            ITEMS_INIT.append((x + 75, y))

        add_containers_to_list(ITEMS_INIT, self.itemContainers)
        add_containers_to_list(MIXING_ITEMS_POSITIONS, self.itemContainers)

        # Container del resultado :
        result_x, result_y = MIXING_ITEMS_POSITIONS[-1]

        self.resultPlace = Container(
            width=CONTAINER_SIZE,
            height=CONTAINER_SIZE,
            center_x=result_x + 100,
            center_y=result_y,
            color=arcade.color.BABY_BLUE,
        )
        self.resultPlace.container_id = len(self.itemContainers)
        self.itemContainers.append(self.resultPlace)

    def _load_inventory(self) -> None:
        for index, (item, quantity) in enumerate(self.items.items()):
            container = self.itemContainers[index]
            # Guardo el indice de su container para después volverlo a su lugar
            container.setItem(item, quantity)

    def _generate_item_sprites(self) -> None:
        for container in self.itemContainers:
            if not container.item_placed:
                continue
            path: str = str(MineralsResources[container.item_placed]["item"]["path"])
            sprite = arcade.Sprite(
                path, scale=3, center_x=container.center_x, center_y=container.center_y
            )
            sprite.container_index = container.container_id
            sprite.name = container.item_placed
            sprite.quantity = container.item_cant
            self.inventorySrites.append(sprite)

    def _update_items_texts(self) -> None:
        self.textList.clear()
        for container in self.itemContainers:
            if container.item_placed:
                textSprite = arcade.create_text_sprite(
                    text=f"{container.item_placed} x {container.item_cant}",
                    font_size=11,
                )
                textSprite.center_x = container.center_x
                textSprite.center_y = container.center_y - (container.height + 5)
                self.textList.append(textSprite)

    def _load_item_result(self):
        input_1, input_2 = self.itemContainers[-3:-1]
        item_1, item_2 = input_1.item_placed, input_2.item_placed

        if not (item_1 and item_2):
            return

        result = Combinations.get(item_1, {}).get(item_2, None)
        if not result:
            return

        path = str(MineralsResources[result]["item"]["path"])
        sprite = arcade.Sprite(
            path,
            center_x=self.resultPlace.center_x,
            center_y=self.resultPlace.center_y,
            scale=3,
        )

        sprite.name = result
        sprite.container_index = self.resultPlace.container_id
        sprite.quantity = 1

        self.resultPlace.setItem(result, 1)
        self.inventorySrites.append(sprite)

        for container in (input_1, input_2):
            container.item_cant -= 1
            if container.item_cant == 0:
                container.clear_item()
                self._remove_sprite_for_container(container.container_id)

    def _remove_sprite_for_container(self, container_id: int):
        for sprite in self.inventorySrites:
            if getattr(sprite, "container_index", None) == container_id:
                self.inventorySrites.remove(sprite)
                return

    def _reset_sprite_position(self, sprite: arcade.Sprite) -> None:
        originalContainer = self.itemContainers[sprite.container_index]
        sprite.center_x = originalContainer.center_x
        sprite.center_y = originalContainer.center_y

    def _move_sprite_to_container(
        self, sprite: arcade.Sprite, container: Container
    ) -> None:
        oldContainer: Container = self.itemContainers[sprite.container_index]
        sprite.center_x = container.center_x
        sprite.center_y = container.center_y
        sprite.container_index = container.container_id
        container.setItem(sprite.name, oldContainer.item_cant)
        sprite.container_index = container.container_id

    def on_show_view(self) -> None:
        self._setup_containers()
        self._load_inventory()
        self._generate_item_sprites()
        self._update_items_texts()
        super().on_show_view()

    def on_draw(self):
        self.clear()  # limpia la pantalla
        self.camera.use()
        self.spriteList.draw(pixelated=True)
        self.textList.draw(pixelated=True)
        self.itemContainers.draw(pixelated=True)
        self.inventorySrites.draw(pixelated=True)
        self.UIManager.draw(pixelated=True)

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.SPACE:
            self.callback(SignalCodes.CHANGE_VIEW, "MENU")

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.is_mouse_active = True
            sprites = arcade.get_sprites_at_point((x, y), self.inventorySrites)
            self.spriteToMove = sprites[-1] if sprites else None

    def on_mouse_release(
        self, x: int, y: int, button: int, modifiers: int
    ) -> bool | None:
        if button != arcade.MOUSE_BUTTON_LEFT or not self.is_mouse_active:
            return

        self.is_mouse_active = False  # desactivo el click

        if not self.spriteToMove:
            return

        collisions: list[Container] = arcade.check_for_collision_with_list(
            self.spriteToMove, self.itemContainers
        )

        if not collisions:
            self._reset_sprite_position(self.spriteToMove)
            self.spriteToMove = None  # Pongo que no hay nngún sprite qe mover
            return

        newContainer: Container = collisions[0]
        lastContainerIndex: int = self.spriteToMove.container_index
        oldContainer = self.itemContainers[lastContainerIndex]

        if not (newContainer.item_placed):
            self._move_sprite_to_container(self.spriteToMove, newContainer)
            oldContainer.clear_item()
        elif newContainer.item_placed == oldContainer.item_placed:
            newContainer.add_quantity(oldContainer.item_cant)
            self.inventorySrites.remove(self.spriteToMove)
        else:
            self._reset_sprite_position(self.spriteToMove)

        oldContainer.clear_item()
        self._update_items_texts()
        self.spriteToMove = None  # Pongo que no hay nngún sprite qe mover

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> bool | None:
        if self.spriteToMove:
            # Cambio la posición del sprite a la del mouse
            self.spriteToMove.center_x = x
            self.spriteToMove.center_y = y
