import arcade
import Constants
from characters.Player import Player
from .View import View

from items.Container import Container
from items.Item import Item
from .utils import add_containers_to_list

from DataManager import testChests

CONTAINER_SIZE = 50
ITEMS_INIT = (550, 300)


class Chest(View):
    def __init__(
        self, chestId: str, player: Player, previusScene, backgroundImage
    ) -> None:
        backgroundUrl = ":resources:Background/Texture/TX Plant.png"
        super().__init__(backgroundUrl=backgroundUrl, tileMapUrl=None)
        self.backgroundImage = backgroundImage
        self.backgroundImage
        self.window.set_mouse_visible(True)
        self.itemSprites: arcade.SpriteList = arcade.SpriteList()
        self.containerSprites = arcade.SpriteList()
        self.containerPlayerSprites = arcade.SpriteList()
        self.itemTextSprites: list[arcade.Text] = []
        self.nextItemId: int = 0
        self.actualChest: str = chestId
        self.player = player
        self.is_mouse_active = False
        self.itemToMove: Item | None = None
        self.previusScene = previusScene

        self.playerContainerIndex = 0
        self._setup()

    def _setup_containers(self) -> None:
        positions_1 = [(ITEMS_INIT[0] + 60 * i, ITEMS_INIT[1]) for i in range(4)]
        positions_2 = [(ITEMS_INIT[0] + 60 * i, ITEMS_INIT[1] + 60) for i in range(4)]
        playerInitPosition = Constants.Game.PLAYER_INVENTORY_POSITION
        playerItems = [
            (playerInitPosition[0] + 60 * i, playerInitPosition[1]) for i in range(5)
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

    def _find_item_with_containerId(
        self, container_id: int, sprite_index: int = 0
    ) -> Item | None:
        if sprite_index == len(self.itemSprites):
            return None
        sprite: Item = self.itemSprites[sprite_index]
        if sprite.container_id == container_id:
            return sprite
        return self._find_item_with_containerId(container_id, sprite_index + 1)

    def _update_texts_position(self) -> None:
        for item in self.itemSprites:
            actualText: arcade.Text | None = self._find_item_with_id(
                item.id, self.itemTextSprites
            )
            if not (actualText):
                continue
            actualText.x = item.center_x
            actualText.y = item.center_y - ((item.height / 2) + 24)

    def _create_item_text(self, item: Item) -> arcade.Text:
        content = f"{item.name} x {item.quantity}"
        textSprite = arcade.Text(
            text=content,
            font_size=9,
            x=item.center_x,
            y=item.center_y - ((item.height / 2) + 24),
            anchor_x="center",
            anchor_y="baseline",
        )
        textSprite.id = item.id
        return textSprite

    def _generate_item_sprites(self):
        for index, (item, quantity) in enumerate(testChests[self.actualChest].items()):
            container: Container = self.containerSprites[index]
            newItem = Item(name=item, quantity=quantity, scale=2)
            newItem.id = self.nextItemId
            self.nextItemId += 1
            newItem.change_container(container.id)
            newItem.change_position(container.center_x, container.center_y)
            container.item_placed = True
            self.itemTextSprites.append(self._create_item_text(newItem))
            self.itemSprites.append(newItem)

        for index, (item, quantity) in enumerate(self.player.getInventory().items()):
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
            if textSprite.text != f"{item.name} x {item.quantity}":
                textSprite.text = f"{item.name} x {item.quantity}"
            textSprite.anchor_x = "center"
            textSprite.anchor_y = "baseline"
        self._update_texts_position()

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

    def on_update(self, delta_time: float) -> bool | None:
        self._sync_item_text()
        self._update_texts_position()

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
                pixelated=True,
            )
        self.containerSprites.draw(pixelated=True)
        self.containerPlayerSprites.draw(pixelated=True)
        self.itemSprites.draw(pixelated=True)
        for text in self.itemTextSprites:
            text.draw()

    def on_show_view(self) -> None:
        pass

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
                text: arcade.Text = self._find_item_with_id(
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

    def updateInventories(self):
        # Acá voy a actualizar los inventarios tanto del cofre como del personaje
        # Esta parte es del cofre
        newchestInventory = {}
        for container in self.containerSprites:
            item: Item | None = self._find_item_with_containerId(container.id)
            if item:
                newchestInventory[item.name] = item.quantity

        testChests[self.actualChest] = newchestInventory
        # Ahora voy a actualizar el inventario del jugador
        newPlayerInventory = {}
        for container in self.containerPlayerSprites:
            item: Item | None = self._find_item_with_containerId(container.id)
            if item:
                newPlayerInventory[item.name] = item.quantity
        self.player.inventory = newPlayerInventory

    def cleanup(self):
        # Limpio todas las listas de sprites
        self.itemSprites = arcade.SpriteList()
        self.containerSprites = arcade.SpriteList()
        self.containerPlayerSprites = arcade.SpriteList()
        self.itemTextSprites = []
        # Elimino la textura del fondo
        del self.backgroundImage
        # Elimno las referencias directas
        self.itemToMove = None
        self.playerInventory = None
        self.window.set_mouse_visible(False)

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.ESCAPE:
            self.updateInventories()
            self.cleanup()
            self.window.show_view(self.previusScene)
