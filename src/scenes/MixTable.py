import arcade
import arcade.gui
from scenes.View import View
from characters.Player import Player
import DataManager
from typing import Callable, Dict
from Constants import SignalCodes
from items.Container import Container
from items.Item import Item
from .utils import add_containers_to_list, get_result

Combinations: Dict[str, Dict[str, str]] = DataManager.loadData("CombinationsTest.json")


# centros de los contenedores
ITEMS_POSITIONS: list[tuple[int, int]] = [(100, 100), (175, 100), (250, 100)]
MIXING_ITEMS_POSITIONS: list[tuple[int, int]] = [(300, 300), (400, 300)]
CONTAINER_SIZE = 50

ITEMS_INIT: tuple[int, int] = (100, 100)


class MixTable(View):
    def __init__(self, callback: Callable[[int, str], None], player: Player):
        backgroundUrl = ":resources:Background/Texture/TX Plant.png"
        super().__init__(backgroundUrl=backgroundUrl, tileMapUrl=None)

        # Init de la clase
        self.callback = callback
        self.player = player
        self.items: dict = player.getInventory() or {"rubi": 4, "rock": 3, "water": 5}
        self.nextItemId: int = 0

        # Configuraciones de cámara
        self.window.set_mouse_visible(True)
        self.camera.zoom = 1
        # Listas de sprites
        self.backgroundSprites = arcade.SpriteList()
        self.itemSprites = arcade.SpriteList()
        self.containerSprites: arcade.SpriteList = arcade.SpriteList()
        self.itemTextSprites: list[arcade.Text] = []

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
        self.itemToMove: Item | None = None
        self.resultPlace: Container

    def _find_item_with_containerId(self, container_id: int, sprite_index: int = 0):
        if sprite_index == len(self.itemSprites):
            return None
        sprite: Item = self.itemSprites[sprite_index]
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
            pointList=positions,
            listToAdd=self.containerSprites,
            containerSize=CONTAINER_SIZE,
        )
        add_containers_to_list(
            pointList=MIXING_ITEMS_POSITIONS,
            listToAdd=self.containerSprites,
            containerSize=CONTAINER_SIZE,
        )

        # Container del resultado :
        result_x, result_y = MIXING_ITEMS_POSITIONS[-1]

        self.resultPlace = Container(
            width=CONTAINER_SIZE,
            height=CONTAINER_SIZE,
            center_x=result_x + 100,
            center_y=result_y,
            color=arcade.color.BABY_BLUE,
        )
        self.resultPlace.id = len(self.containerSprites)
        self.containerSprites.append(self.resultPlace)

    def _generate_item_sprites(self) -> None:
        for index, (name, quantity) in enumerate(self.items.items()):
            container: Container = self.containerSprites[index]
            newItem = Item(name=name, quantity=quantity, scale=3)
            newItem.id = self.nextItemId
            self.nextItemId += 1
            newItem.change_container(container.id)
            newItem.change_position(container.center_x, container.center_y)
            self.itemTextSprites.append(self._create_item_text(newItem))
            self.itemSprites.append(newItem)

    def _create_item_text(self, item: Item) -> arcade.Text:
        content = f"{item.name} x {item.quantity}"
        textSprite = arcade.Text(
            text=content,
            font_size=11,
            x=item.center_x,
            y=item.center_y - ((item.height / 2) + 15),
            anchor_x="center",
            anchor_y="baseline",
        )
        textSprite.id = item.id
        return textSprite

    def _update_texts_position(self) -> None:
        for item in self.itemSprites:
            actualText: arcade.Sprite | None = self._find_item_with_id(
                item.id, self.itemTextSprites
            )
            if not (actualText):
                return
            actualText.x = item.center_x
            actualText.y = item.center_y - (item.height / 2 + 15)

    def _sync_item_text(self) -> None:
        for textSprite in self.itemTextSprites:
            item = self._find_item_with_id(textSprite.id, self.itemSprites)
            if item is None:
                print("item no encontrado")
                continue
            expected = f"{item.name} x {item.quantity}"
            if textSprite.text != expected:
                textSprite.text = expected

    def _load_item_result(self) -> None:
        input_1, input_2 = self.containerSprites[-3:-1]
        item_1 = self._find_item_with_containerId(input_1.id)
        item_2 = self._find_item_with_containerId(input_2.id)

        if not (item_1 and item_2):
            return

        result = get_result(item_1, item_2, Combinations)
        if not result:
            return

        oldResult: arcade.Sprite | None = self._find_item_with_containerId(
            self.resultPlace.id
        )
        if not oldResult:
            sprite: Item = Item(result, quantity=1, scale=3)
            sprite.change_position(self.resultPlace.center_x, self.resultPlace.center_y)
            sprite.id = self.nextItemId
            self.nextItemId += 1
            sprite.change_container(self.resultPlace.id)
            self.itemTextSprites.append(self._create_item_text(sprite))
            self.itemSprites.append(sprite)
        else:
            oldResult.quantity += 1

        for item, container in zip((item_1, item_2), (input_1, input_2)):
            item.quantity -= 1
            if item.quantity == 0:
                self.itemTextSprites.remove(
                    self._find_item_with_id(item.id, self.itemTextSprites)
                )
                self.itemSprites.remove(item)
                container.item_placed = False

    def _reset_sprite_position(self, sprite: Item) -> None:
        originalContainer = self.containerSprites[sprite.container_id]
        sprite.change_position(originalContainer.center_x, originalContainer.center_y)

    def _move_sprite_to_container(self, sprite: Item, container: Container) -> None:
        sprite.change_position(container.center_x, container.center_y)
        sprite.change_container(container.id)

    def on_show_view(self) -> None:
        self._setup_containers()
        self._generate_item_sprites()
        super().on_show_view()

    def on_draw(self):
        self.clear()  # limpia la pantalla
        self.camera.use()
        self.backgroundSprites.draw(pixelated=True)
        self.containerSprites.draw(pixelated=True)
        self.itemSprites.draw(pixelated=True)
        self._sync_item_text()
        self._update_texts_position()
        for text in self.itemTextSprites:
            text.draw()
        self.UIManager.draw(pixelated=True)

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.SPACE:
            self.callback(SignalCodes.CHANGE_VIEW, "MENU")

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.is_mouse_active = True
            sprites = arcade.get_sprites_at_point((x, y), self.itemSprites)
            self.itemToMove = sprites[-1] if sprites else None

    def on_mouse_release(
        self, x: int, y: int, button: int, modifiers: int
    ) -> bool | None:
        if button != arcade.MOUSE_BUTTON_LEFT or not self.is_mouse_active:
            return

        self.is_mouse_active = False  # desactivo el click

        if not self.itemToMove:
            return

        collisions: list[Container] = arcade.check_for_collision_with_list(
            self.itemToMove, self.containerSprites
        )

        if not collisions:
            self._reset_sprite_position(self.itemToMove)
            self.itemToMove = None
            return

        newContainer: Container = collisions[0]
        lastContainerIndex: int = self.itemToMove.container_id
        oldContainer: Container = self.containerSprites[lastContainerIndex]

        if newContainer.id == oldContainer.id:
            self._reset_sprite_position(self.itemToMove)
            self.itemToMove = None
            return

        if not (newContainer.item_placed):
            self._move_sprite_to_container(self.itemToMove, newContainer)
            oldContainer.item_placed = False
            newContainer.item_placed = True
        else:
            item: Item = self._find_item_with_containerId(newContainer.id)
            if item.name == self.itemToMove.name:
                text: arcade.Sprite = self._find_item_with_id(
                    item.id, self.itemTextSprites
                )
                self._move_sprite_to_container(self.itemToMove, newContainer)
                oldContainer.item_placed = False
                newContainer.item_placed = True
                self.itemToMove.quantity += item.quantity
                self.itemSprites.remove(item)
                self.itemTextSprites.remove(text)

            self._reset_sprite_position(self.itemToMove)

        self.itemToMove = None  # Pongo que no hay nngún sprite qe mover

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> bool | None:
        if self.itemToMove:
            # Cambio la posición del sprite a la del mouse
            self.itemToMove.change_position(x, y)
