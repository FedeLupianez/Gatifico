import arcade
import Constants
from .View import View

from items.Container import Container
from items.Item import Item
from .utils import add_containers_to_list


CONTAINER_SIZE = 40
ITEMS_INIT = (300, 300)


class Chest(View):
    def __init__(
        self, chestId: str, playerInventory: dict, previusScene, backgroundImage
    ) -> None:
        backgroundUrl = ":resources:Background/Texture/TX Plant.png"
        super().__init__(backgroundUrl=backgroundUrl, tileMapUrl=None)
        self.backgroundImage = backgroundImage
        self.backgroundImage
        self.chests: dict[str, dict[str, int]] = {
            "chest_1": {"rubi": 4, "rock": 3},
            "chest_2": {},
            "chest_3": {},
        }
        self.window.set_mouse_visible(True)
        self.itemSprites: arcade.SpriteList = arcade.SpriteList()
        self.containerSprites = arcade.SpriteList()
        self.containerPlayerSprites = arcade.SpriteList()
        self.itemTextSprites = arcade.SpriteList()
        self.nextItemId: int = 0
        self.actualChest: str = chestId
        self.playerInventory = playerInventory
        self.is_mouse_active = False
        self.itemToMove: Item | None = None
        self.previusScene = previusScene

        self.playerContainerIndex = 0

    def addItem(self, newItem: str, amount: int):
        if self.chests[self.actualChest].get(newItem, None):
            self.chests[self.actualChest][newItem] += amount
        else:
            self.chests[self.actualChest][newItem] = amount

    def _setup_containers(self) -> None:
        positions_1 = [(ITEMS_INIT[0] + 45 * i, ITEMS_INIT[1]) for i in range(4)]
        positions_2 = [(ITEMS_INIT[0] + 45 * i, ITEMS_INIT[1] + 45) for i in range(4)]
        playerItems = [
            (ITEMS_INIT[0] + 45 * i, ITEMS_INIT[1] - 90)
            for i in range(len(self.playerInventory.items()))
        ]
        add_containers_to_list(
            pointList=positions_1,
            listToAdd=self.containerSprites,
            containerSize=CONTAINER_SIZE,
            containerType="chest",
            lastId=0,
        )
        add_containers_to_list(
            pointList=positions_2,
            listToAdd=self.containerSprites,
            containerSize=CONTAINER_SIZE,
            containerType="chest",
            lastId=len(self.containerSprites),
        )
        self.playerContainerIndex = len(self.containerSprites)
        add_containers_to_list(
            pointList=playerItems,
            listToAdd=self.containerPlayerSprites,
            containerSize=CONTAINER_SIZE,
            containerType="inventory",
            lastId=len(self.containerSprites),
        )

    def _find_item_with_id(
        self, id: int, listToFind: arcade.SpriteList, sprite_index: int = 0
    ):
        if sprite_index == len(listToFind):
            return None
        sprite = listToFind[sprite_index]
        if sprite.id == id:
            return sprite
        return self._find_item_with_id(id, listToFind, sprite_index + 1)

    def _find_item_with_containerId(self, container_id: int, sprite_index: int = 0):
        if sprite_index == len(self.itemSprites):
            return None
        sprite: Item = self.itemSprites[sprite_index]
        if sprite.container_id == container_id:
            return sprite
        return self._find_item_with_containerId(container_id, sprite_index + 1)

    def _update_texts_position(self) -> None:
        for item in self.itemSprites:
            actualText: arcade.Sprite | None = self._find_item_with_id(
                item.id, self.itemTextSprites
            )
            if not (actualText):
                return
            actualText.center_x = item.center_x
            actualText.center_y = item.center_y - (item.height / 2 + 15)

    def _create_item_text(self, item: Item) -> arcade.Sprite:
        content = f"{item.name} x {item.quantity}"
        textSprite = arcade.create_text_sprite(text=content, font_size=9)
        textSprite.center_x = item.center_x
        textSprite.center_y = item.center_y - (item.height / 2 + 15)
        textSprite.id = item.id
        textSprite.content = content
        return textSprite

    def _generate_item_sprites(self):
        for index, (item, quantity) in enumerate(self.chests[self.actualChest].items()):
            container: Container = self.containerSprites[index]
            newItem = Item(name=item, quantity=quantity, scale=2)
            newItem.id = self.nextItemId
            self.nextItemId += 1
            newItem.change_container(container.id)
            newItem.change_position(container.center_x, container.center_y)
            container.item_placed = True
            self.itemTextSprites.append(self._create_item_text(newItem))
            self.itemSprites.append(newItem)

        for index, (item, quantity) in enumerate(self.playerInventory.items()):
            container: Container = self.containerPlayerSprites[index]
            newItem = Item(name=item, quantity=quantity, scale=2)
            newItem.id = self.nextItemId
            self.nextItemId += 1
            newItem.change_container(container.id)
            newItem.change_position(container.center_x, container.center_y)
            container.item_placed = True
            self.itemTextSprites.append(self._create_item_text(newItem))
            self.itemSprites.append(newItem)

    def _sync_item_text(self) -> None:
        for textSprite in self.itemTextSprites:
            item = self._find_item_with_id(textSprite.id, self.itemSprites)
            if item is None:
                continue
            if textSprite.content != f"{item.name} x {item.quantity}":
                print("\nNuevo texto : ")
                print("item ID : ", item.id)
                print("Contenido anterior : ", textSprite.content)
                print("Contenido nuevo : ", f"{item.name} x {item.quantity}")
                self.itemTextSprites.remove(textSprite)
                self.itemTextSprites.append(self._create_item_text(item))

    def _reset_sprite_position(self, sprite: Item) -> None:
        if sprite.container_id < self.playerContainerIndex:
            originalContainer = self._find_item_with_id(
                sprite.container_id, self.containerSprites
            )
        else:
            originalContainer = self._find_item_with_id(
                sprite.container_id, self.containerPlayerSprites
            )

        assert originalContainer is not None
        sprite.change_position(originalContainer.center_x, originalContainer.center_y)

    def _move_sprite_to_container(self, sprite: Item, container: Container) -> None:
        sprite.change_position(container.center_x, container.center_y)
        sprite.change_container(container.id)

    def _setup(self) -> None:
        self._setup_containers()
        self._generate_item_sprites()

    def on_draw(self) -> None:
        self.clear()
        self.camera.use()
        if self.backgroundImage:
            arcade.draw_texture_rect(
                self.backgroundImage,
                rect=arcade.rect.Rect(
                    left=0,
                    right=0,
                    top=0,
                    bottom=0,
                    width=Constants.Game.SCREEN_WIDTH,
                    height=Constants.Game.SCREEN_HEIGHT,
                    x=Constants.Game.SCREEN_WIDTH / 2,
                    y=Constants.Game.SCREEN_HEIGHT / 2,
                ),
            )
        self.containerSprites.draw(pixelated=True)
        self.containerPlayerSprites.draw(pixelated=True)
        self.itemSprites.draw(pixelated=True)
        self.itemTextSprites.draw(pixelated=True)
        self._sync_item_text()
        self._update_texts_position()

    def on_show_view(self) -> None:
        self._setup()
        super().on_show_view()

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

        chestContainersCollisions: list[Container] = (
            arcade.check_for_collision_with_list(self.itemToMove, self.containerSprites)
        )
        playerContainersCollisions: list[Container] = (
            arcade.check_for_collision_with_list(
                self.itemToMove, self.containerPlayerSprites
            )
        )

        if not chestContainersCollisions and not playerContainersCollisions:
            self._reset_sprite_position(self.itemToMove)
            self.itemToMove = None
            return
        newContainer: Container
        lastContainerId: int = self.itemToMove.container_id
        oldContainer: Container = self._find_item_with_id(
            lastContainerId, self.containerSprites
        ) or self._find_item_with_id(lastContainerId, self.containerPlayerSprites)

        if chestContainersCollisions and not playerContainersCollisions:
            newContainer: Container = chestContainersCollisions[0]
        else:
            newContainer: Container = playerContainersCollisions[0]

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

    def cleanup(self):
        # Limpio todas las listas de sprites
        self.itemSprites.clear()
        self.containerSprites.clear()
        self.containerPlayerSprites.clear()
        self.itemTextSprites.clear()

        # Elimino la textura temporal (si querés)
        del self.backgroundImage

        # Anulá referencias fuertes si las tenés
        self.itemToMove = None
        self.playerInventory = None

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.ESCAPE:
            self.cleanup()
            self.window.show_view(self.previusScene)
