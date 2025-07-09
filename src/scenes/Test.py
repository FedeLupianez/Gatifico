import arcade
from typing import Tuple
from scenes.View import View
import Constants
from characters.Player import Player
from typing import Callable
from items.Mineral import Mineral
import DataManager
from items.Item import Item
from .utils import add_containers_to_list

MineralsResources = DataManager.loadData("Minerals.json")


def is_near_to_sprite(
    sprite1: arcade.Sprite, sprite2: arcade.Sprite, tolerance: float = 16.0
) -> bool:
    return arcade.get_distance_between_sprites(sprite1, sprite2) <= tolerance


class Test(View):
    def __init__(self, callback: Callable, player: Player) -> None:
        backgroundUrl = None
        tileMapUrl = ":resources:Maps/Tests.tmx"
        super().__init__(backgroundUrl=backgroundUrl, tileMapUrl=tileMapUrl)

        self.callback = callback

        self.player = player  # Defino el personaje
        self.guiCamera = arcade.Camera2D()

        self.setupSpriteLists()
        self.setupSceneLayers()
        self.setupPlayer()
        self.updateItemSprites()
        self.updateItemTexts()

        self.keysPressed: set = set()

    def setupSpriteLists(self):
        # Listas de Sprites
        self.playerSpritesList: arcade.SpriteList = arcade.SpriteList()
        self.backgroundSpriteList: arcade.SpriteList = arcade.SpriteList()
        self.inventorySpriteList: arcade.SpriteList = arcade.SpriteList()
        self.itemsInventory: arcade.SpriteList = arcade.SpriteList()
        self.inventoryTexts: arcade.SpriteList = arcade.SpriteList()

        # Agrego los contenedores a la lista del inventario
        CONTAINER_SIZE = 50
        ITEMS_INIT = (500, 100)
        positions = [(ITEMS_INIT[0] + 60 * i, ITEMS_INIT[1]) for i in range(5)]
        add_containers_to_list(
            positions, self.inventorySpriteList, containerSize=CONTAINER_SIZE
        )

    def setupPlayer(self) -> None:
        self.player.sprite.center_x = Constants.Game.SCREEN_WIDTH // 2
        self.player.sprite.center_y = Constants.Game.SCREEN_HEIGHT // 2
        self.player.setup()
        self.playerSpritesList.append(self.player.sprite)
        # Camara para seguir al jugador :
        self.camera.zoom = 2.5

    def setupSceneLayers(self) -> None:
        assert self.tileMap is not None
        # Capas de vista :
        self.floor = self.scene["Piso"]
        self.walls = self.scene["Paredes"]
        self.backgroundObjects = self.scene["Objetos"]
        # Capas de colisiones :
        self.collisionSprites = self.loadObjectLayers("Colisiones", self.tileMap)
        self.interactSprites = self.loadObjectLayers("Interactuables", self.tileMap)
        self.mineralsLayer = self.loadMineralLayer()

    def loadMineralLayer(self) -> arcade.SpriteList:
        tempLayer = self.tileMap.object_lists["Minerales"]
        tempList = arcade.SpriteList()

        for obj in tempLayer:
            assert obj.name is not None
            assert obj.properties is not None
            shape: Tuple[
                Tuple[float, float],
                Tuple[float, float],
                Tuple[float, float],
                Tuple[float, float],
            ] = obj.shape

            topLeft, topRight, bottomRight, bottomLeft = shape
            width: float = topRight[0] - topLeft[0]
            height: float = topLeft[1] - bottomLeft[1]
            center_x: float = topLeft[0] + (width) / 2
            center_y: float = bottomLeft[1] + (height) / 2
            size = str(obj.properties.get("size"))

            newObj = Mineral(
                obj.name,
                size,
                center_x=center_x,
                center_y=center_y,
                mineralAttributes=MineralsResources,
            )
            tempList.append(newObj)
        return tempList

    def on_show_view(self) -> None:
        return super().on_show_view()

    def on_draw(self) -> bool | None:
        # Función que se llama cada vez que se dibuja la escena
        self.clear()  # limpia la pantalla
        self.camera.use()
        self.scene.draw(pixelated=True)  # dibuja la escena
        self.playerSpritesList.draw(pixelated=True)  # dibuja el personaje
        self.backgroundSpriteList.draw(pixelated=True)
        self.mineralsLayer.draw(pixelated=True)

        self.guiCamera.use()
        self.inventorySpriteList.draw(pixelated=True)
        self.inventoryTexts.draw(pixelated=True)

    def updateItemSprites(self):
        self.itemsInventory.clear()
        for index, (item, quantity) in enumerate(self.player.inventory.items()):
            container = self.inventorySpriteList[index]
            newItem: Item = Item(name=item, quantity=quantity, scale=2)
            newItem.id = index
            newItem.change_container(container.id)
            newItem.change_position(container.center_x, container.center_y)
            self.inventorySpriteList.append(newItem)

    def updateItemTexts(self):
        self.inventoryTexts.clear()
        for index, (item, quantity) in enumerate(self.player.inventory.items()):
            container = self.inventorySpriteList[index]
            newText = arcade.create_text_sprite(
                text=f"{item} x {quantity}", font_size=9
            )
            newText.center_x = container.center_x
            newText.center_y = container.center_y - (container.height / 2)
            self.inventoryTexts.append(newText)

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.SPACE:
            self.callback(Constants.SignalCodes.CHANGE_VIEW, "MENU")
            return

        if symbol == arcade.key.E:
            if self.handleInteractions():
                return

        self.keysPressed.add(symbol)

    def handleInteractions(self):
        for interactObject in self.interactSprites:
            if is_near_to_sprite(self.player.sprite, interactObject, tolerance=40):
                print(interactObject.name)
                if interactObject.name.lower() == "door":
                    self.callback(Constants.SignalCodes.CHANGE_VIEW, "MENU")
                    return True

        for mineral in self.mineralsLayer:
            if is_near_to_sprite(self.player.sprite, mineral, tolerance=35):
                mineral.setup()
                mineral.stateMachine.processState(arcade.key.E)
                self.player.addToInventory(mineral.mineral, 1)
                self.updateItemSprites()
                self.updateItemTexts()

                if mineral.should_removed:
                    mineral.remove_from_sprite_lists()
                return True
        return False

    def on_key_release(self, symbol: int, modifiers: int) -> bool | None:
        self.keysPressed.discard(symbol)
        self.player.updateState(-symbol)

    def on_update(self, delta_time: float) -> bool | None:
        self.player.update_animation(delta_time)
        lastPosition = self.player.sprite.center_x, self.player.sprite.center_y
        self.player.updatePosition()

        # Colisiones físicas solo con capas físicas reales
        collisions = arcade.check_for_collision_with_lists(
            self.player.sprite,
            [
                self.collisionSprites,
                self.walls,
            ],
        )

        # Chequeo manual de colisión "física" con interactuables (sin bloquear interacción)
        for obj in self.interactSprites:
            if arcade.check_for_collision(self.player.sprite, obj):
                collisions.append(obj)
        for mineral in self.mineralsLayer:
            if arcade.check_for_collision(self.player.sprite, mineral):
                collisions.append(mineral)

        if collisions:
            self.player.sprite.center_x, self.player.sprite.center_y = lastPosition

        for key in self.keysPressed:
            self.player.updateState(key)

        self.camera.position = arcade.math.lerp_2d(
            self.camera.position, self.player.sprite.position, 0.50
        )
