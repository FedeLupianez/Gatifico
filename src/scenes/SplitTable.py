from typing import Callable
import arcade.gui
from items.Container import Container
from items.Item import Item
import arcade
from scenes.View import View
import DataManager
from Constants import SignalCodes
from characters.Player import Player
from scenes.utils import add_containers_to_list

RSC = DataManager.loadData("SplitTableResources.json")
# Centros de los contenedores
INPUT_POSITION: tuple[int, int] = (150, 300)
RESULT_INIT_POSITION: tuple[int, int] = (300, 300)
SPLIT_ITEMS_POSITIONS: list[tuple[int, int]] = [(150, 300), (300, 300), (400, 300)]
CONTAINER_SIZE = 50

ITEMS_INIT: tuple[int, int] = (100, 100)


class SplitTable(View):
    def __init__(
        self,
        callback: Callable[[int, str], None],
        player: Player,
    ) -> None:
        backgroundUrl = ":resources:Background/Texture/TX Plant.png"
        super().__init__(backgroundUrl, None)
        self.window.set_mouse_visible(True)

        self.callback = callback
        self.player = player
        self.items: dict = player.getInventory() or {"rubi": 4, "rock": 3, "water": 5}
        self.nextItemId: int = 0
        self.camera.zoom = 1
        self.is_mouse_active: bool = False
        self.itemToMove: Item | None = None
        self.UIManager = arcade.gui.UIManager(self.window)
        self.UIManager.enable()
        self.setup()

    def setup(self) -> None:
        self._setup_lists()
        self._setup_containers()
        self._setup_items()
        self.setupUI()

    def _setup_lists(self) -> None:
        self.backgroundSprites = arcade.SpriteList()
        self.itemSprites = arcade.SpriteList()
        self.containerSprites = arcade.SpriteList()
        self.itemTexts: list[arcade.Text] = []
        self.inputContainer: Container
        self.resultContainers: list[Container] = []

    def _setup_containers(self) -> None:
        positions = [
            (ITEMS_INIT[0] + 75 * i, ITEMS_INIT[1]) for i in range(len(self.items))
        ]
        add_containers_to_list(
            pointList=positions,
            listToAdd=self.containerSprites,
            containerSize=CONTAINER_SIZE,
        )
        self.inputContainer = Container(
            width=CONTAINER_SIZE,
            height=CONTAINER_SIZE,
            center_x=INPUT_POSITION[0],
            center_y=INPUT_POSITION[1],
        )
        self.inputContainer.id = len(self.containerSprites)
        self.containerSprites.append(self.inputContainer)

    def _setup_items(self) -> None:
        for index, (name, quantity) in enumerate(self.items.items()):
            container: Container = self.containerSprites[index]
            newItem = Item(name=name, quantity=quantity, scale=3)
            newItem.id = self.nextItemId
            self.nextItemId += 1
            newItem.change_container(container.id)
            newItem.change_position(container.center_x, container.center_y)
            self.itemTexts.append(self._create_item_text(newItem))
            self.itemSprites.append(newItem)

    def setupUI(self) -> None:
        input_x, input_y = INPUT_POSITION
        self.mixButton = arcade.gui.UIFlatButton(
            x=input_x + CONTAINER_SIZE, y=input_y - CONTAINER_SIZE * 2, text="Separar"
        )

        @self.mixButton.event("on_click")
        def on_click(event):
            self.load_result()

        self.UIManager.add(self.mixButton)

    def _create_item_text(self, item: Item, fontSize: int = 11) -> arcade.Text:
        content = f"{item.name} x {item.quantity}"
        textSprite = arcade.Text(
            text=content,
            font_size=fontSize,
            x=item.center_x,
            y=item.center_y - ((item.height / 2) + 15),
            anchor_x="center",
            anchor_y="baseline",
        )
        textSprite.id = item.id
        return textSprite

    def _reset_sprite_position(self, sprite: Item) -> None:
        originalContainer = self.containerSprites[sprite.container_id]
        sprite.change_position(originalContainer.center_x, originalContainer.center_y)

    def _move_sprite_to_container(self, sprite: Item, container: Container) -> None:
        sprite.change_position(container.center_x, container.center_y)
        sprite.change_container(container.id)

    def _find_item_with_attr(
        self,
        attr: str,
        value_to_find: int | str,
        list_to_find: list | arcade.SpriteList,
        actualIndex: int = 0,
    ):
        if actualIndex == len(list_to_find):
            return None
        item = list_to_find[actualIndex]
        if (getattr(item, attr)) == value_to_find:
            return item
        return self._find_item_with_attr(
            attr, value_to_find, list_to_find, actualIndex + 1
        )

    def _sync_item_text(self) -> None:
        for textSprite in self.itemTexts:
            item = self._find_item_with_attr("id", textSprite.id, self.itemSprites)
            if not item:
                continue
            expected = f"{item.name} x {item.quantity}"
            if textSprite.text != expected:
                textSprite.text = expected

    def _update_text_position(self) -> None:
        for item in self.itemSprites:
            actualText = self._find_item_with_attr("id", item.id, self.itemTexts)
            if not (actualText):
                return
            actualText.x = item.center_x
            actualText.y = item.center_y - (item.height / 2 + 15)

    def load_result(self) -> None:
        inputItem: Item | None = self._find_item_with_attr(
            "container_id", self.inputContainer.id, self.itemSprites
        )
        if not inputItem:
            return
        print("nombre del item de input : ", inputItem.name)
        file = DataManager.loadData("SplitTableResources.json")
        result = file.get(inputItem.name, {}).items()
        if not (result):
            return
        print("Resultados : ", result)
        for name, quantity in result:
            pos_x, pos_y = RESULT_INIT_POSITION[0], RESULT_INIT_POSITION[1]
            if len(self.resultContainers) > 0:
                pos_x = self.resultContainers[-1].center_x + CONTAINER_SIZE * 2

            newContainer = Container(
                width=CONTAINER_SIZE,
                height=CONTAINER_SIZE,
                center_x=pos_x,
                center_y=pos_y,
            )
            newContainer.id = len(self.containerSprites)

            self.resultContainers.append(newContainer)
            newItem = Item(name=name, quantity=quantity, scale=3)
            newItem.id = self.nextItemId
            self._move_sprite_to_container(newItem, newContainer)
            self.nextItemId += 1
            self.containerSprites.append(newContainer)
            self.itemTexts.append(self._create_item_text(newItem))
            self.itemSprites.append(newItem)
        del file

    def on_update(self, delta_time: float) -> bool | None:
        self._sync_item_text()
        self._update_text_position()

    def on_draw(self) -> None:
        self.clear()
        self.camera.use()
        self.backgroundSprites.draw(pixelated=True)
        self.containerSprites.draw(pixelated=True)
        self.itemSprites.draw(pixelated=True)
        for text in self.itemTexts:
            text.draw()
        self.UIManager.draw()

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.SPACE:
            self.callback(SignalCodes.CHANGE_VIEW, "MENU")

    def on_mouse_press(
        self, x: int, y: int, button: int, modifiers: int
    ) -> bool | None:
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.is_mouse_active = True
            sprites = arcade.get_sprites_at_point((x, y), self.itemSprites)
            self.itemToMove = sprites[-1] if sprites else None
            if self.itemToMove:
                print(self.itemToMove.id)

    def on_mouse_release(
        self, x: int, y: int, button: int, modifiers: int
    ) -> bool | None:
        if button != arcade.MOUSE_BUTTON_LEFT or not self.is_mouse_active:
            return
        self.is_mouse_active = False
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
        oldContainer: Container = self.containerSprites[self.itemToMove.container_id]

        if newContainer.id == oldContainer.id:
            self._reset_sprite_position(self.itemToMove)
            self.itemToMove = None
            return

        if not (newContainer.item_placed):
            self._move_sprite_to_container(self.itemToMove, newContainer)
            oldContainer.item_placed = False
            newContainer.item_placed = True
        else:
            item: Item | None = self._find_item_with_attr(
                "container_id", newContainer.id, self.itemSprites
            )
            if not (item):
                return
            if item.name == self.itemToMove.name:
                text = self._find_item_with_attr("id", item.id, self.itemTexts, item.id)
                if not text:
                    return
                self._move_sprite_to_container(self.itemToMove, newContainer)
                oldContainer.item_placed = False
                newContainer.item_placed = True
                self.itemToMove.quantity += item.quantity
                self.itemSprites.remove(item)
                self.itemTexts.remove(text)

            self._reset_sprite_position(self.itemToMove)
        self.itemToMove = None

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> bool | None:
        if self.itemToMove and self.is_mouse_active:
            # Cambio la posición del sprite a la del mouse
            self.itemToMove.change_position(x, y)
