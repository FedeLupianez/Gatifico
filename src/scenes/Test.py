import arcade
from typing import Optional, Dict, Any

from scenes.View import View
import Constants
from characters.Player import Player
from typing import Callable
from items.Mineral import Mineral
import DataManager
from items.Item import Item
from Types import PlayerData
from .utils import add_containers_to_list
from .Chest import Chest

import random

_minerals_cache: Optional[Dict[str, Any]] = None


def get_minerals_resources() -> Dict[str, Any]:
    """Hago un Lazy loading de los recursos de los minerales con caché"""
    global _minerals_cache
    if _minerals_cache is None:
        _minerals_cache = DataManager.loadData("Minerals.json")
    return _minerals_cache


def is_near_to_sprite(
    sprite1: arcade.Sprite, sprite2: arcade.Sprite, tolerance: float = 16.0
) -> bool:
    dx = sprite1.center_x - sprite2.center_x
    dy = sprite1.center_y - sprite2.center_y
    return (dx * dx + dy * dy) <= (tolerance * tolerance)


class Test(View):
    def __init__(self, callback: Callable, player: Player) -> None:
        backgroundUrl = None
        tileMapUrl = ":resources:Maps/Tests.tmx"
        super().__init__(backgroundUrl=backgroundUrl, tileMapUrl=tileMapUrl)
        self.window.set_mouse_visible(False)

        self.callback = callback

        self.player = player  # Defino el personaje
        self.player.inventory = DataManager.gameData["player"]["inventory"]
        self.guiCamera = arcade.Camera2D()

        self.keysPressed: set = set()
        # Flag para actualizaciones selectivas del inventario
        self.inventoryDirty = True
        # Hash para detectar cambios en el inventario
        self.lastInventoryHash = None
        self._setup_scene()

    def _setup_scene(self) -> None:
        """Configuración principal"""
        self.setupSpriteLists()
        self.setupSceneLayers()
        self.setupPlayer()
        self.updateInventorySprites()
        self.updateInventoryTexts()

    def setupSpriteLists(self):
        # Listas de Sprites
        self.playerSpritesList: arcade.SpriteList = arcade.SpriteList()
        self.backgroundSpriteList: arcade.SpriteList = arcade.SpriteList()
        self.inventorySpriteList: arcade.SpriteList = arcade.SpriteList()
        self.itemsInventory: arcade.SpriteList = arcade.SpriteList()
        self.inventoryTexts: list[arcade.Text] = []
        self.setupInventoryContainers()

    def setupInventoryContainers(self) -> None:
        """Agrego los contenedores a la lista del inventario"""
        CONTAINER_SIZE = 50
        ITEMS_INIT = Constants.Game.PLAYER_INVENTORY_POSITION
        positions = [(ITEMS_INIT[0] + 60 * i, ITEMS_INIT[1]) for i in range(5)]
        add_containers_to_list(
            positions, self.inventorySpriteList, containerSize=CONTAINER_SIZE
        )

    def setupPlayer(self) -> None:
        self.player.sprite.center_x = DataManager.gameData["player"]["position"][
            "center_x"
        ]
        self.player.sprite.center_y = DataManager.gameData["player"]["position"][
            "center_y"
        ]
        self.player.setup()
        self.playerSpritesList.append(self.player.sprite)
        # Camara para seguir al jugador :
        self.camera.zoom = Constants.Game.FOREST_ZOOM_CAMERA
        self.camera.position = self.player.sprite.position

    def setupSceneLayers(self) -> None:
        if not self.tileMap:
            raise ValueError("TileMap no puede set None")

        # Capas de vista :
        self.floor = self.scene["Piso"]
        self.walls = self.scene["Paredes"]
        self.backgroundObjects = self.scene["Objetos"]
        # Capas de colisiones :
        self.collisionSprites = self.loadObjectLayers("Colisiones", self.tileMap)
        self.interactSprites = self.loadObjectLayers("Interactuables", self.tileMap)
        self.mineralsLayer = self.loadMineralLayer()
        # Variable para precomputar las listas de colisiones
        self._collisionList = [self.collisionSprites, self.walls]

    def loadMineralLayer(self) -> arcade.SpriteList:
        if "Minerales" not in self.tileMap.object_lists:
            return arcade.SpriteList()

        tempLayer = self.tileMap.object_lists["Minerales"]
        tempList = arcade.SpriteList()
        mineralsResources = get_minerals_resources()

        for obj in tempLayer:
            if not obj.name or not obj.properties:
                continue
            try:
                mineral = self.createMineralFromObject(obj, mineralsResources)
                tempList.append(mineral)
            except ValueError as e:
                print(e)
        tempList.extend(self.loadRandomMinerals(mineralsResources))
        return tempList

    def createMineralFromObject(self, obj: Any, mineralResources: Dict) -> Mineral:
        """Función para crear un minerl a partir de un objeto de Tilemap"""
        shape = obj.shape
        if len(shape) != 4:
            raise ValueError(f"Forma del objeto {obj.name} invalida")

        topLeft, topRight, _, bottomLeft = shape[:4]
        width: float = topRight[0] - topLeft[0]
        height: float = topLeft[1] - bottomLeft[1]
        center_x: float = topLeft[0] + (width) / 2
        center_y: float = bottomLeft[1] + (height) / 2
        size = str(obj.properties.get("size", "mid"))

        return Mineral(
            obj.name,
            size,
            center_x=center_x,
            center_y=center_y,
            mineralAttributes=get_minerals_resources(),
        )

    def loadRandomMinerals(self, mineralsResources: Dict) -> arcade.SpriteList:
        tempList = arcade.SpriteList()
        names = list(list(mineralsResources.keys()))
        sizes = ["big", "mid", "small"]
        # Pongo un límite en los intentos de crear
        # el mineral para evitar loops infinitos
        maxCollisionAttempts = 10
        collisionAttempts = 0

        # en este loop creo 10 minerales con atributos random
        for _ in range(10):
            mineral = Mineral(
                random.choice(names),
                random.choice(sizes),
                center_x=random.randint(0, Constants.Game.SCREEN_WIDTH),
                center_y=random.randint(0, Constants.Game.SCREEN_HEIGHT),
                mineralAttributes=mineralsResources,
            )

            while collisionAttempts < maxCollisionAttempts:
                collisions = mineral.collides_with_list(self.collisionSprites)
                if not collisions:
                    break
                mineral.center_x = random.randint(50, Constants.Game.SCREEN_WIDTH - 50)
                mineral.center_y = random.randint(50, Constants.Game.SCREEN_HEIGHT - 50)
                collisionAttempts += 1
            if collisionAttempts < 10:
                tempList.append(mineral)
        return tempList

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
        self.itemsInventory.draw(pixelated=True)
        for text in self.inventoryTexts:
            text.draw()

    def updateInventoryDisplay(self) -> None:
        """Esta función se asegura de actualizar el inventario solo cuando hay cambios en este"""
        currentInventoryHash = hash(tuple(sorted(self.player.inventory.items())))

        # Si los hashes son iguales no actualiza la vista
        if self.lastInventoryHash == currentInventoryHash:
            return
        self.lastInventoryHash = currentInventoryHash
        self.updateInventorySprites()
        self.updateInventoryTexts()

    def updateInventorySprites(self):
        self.itemsInventory.clear()
        for index, (item, quantity) in enumerate(self.player.inventory.items()):
            container = self.inventorySpriteList[index]
            newItem: Item = Item(name=item, quantity=quantity, scale=2)
            newItem.id = index
            newItem.change_container(container.id)
            newItem.change_position(container.center_x, container.center_y)
            self.itemsInventory.append(newItem)

    def updateInventoryTexts(self):
        self.inventoryTexts.clear()
        for index, (item, quantity) in enumerate(self.player.inventory.items()):
            container = self.inventorySpriteList[index]
            newText = arcade.Text(
                text=f"{item} x {quantity}",
                font_size=9,
                x=container.center_x,
                y=container.center_y - (container.height / 2 + 15),
                anchor_x="center",
                anchor_y="baseline",
            )
            self.inventoryTexts.append(newText)

    def openChest(self, chestId: str) -> None:
        # Borro la lista de keys activas para que no se siga moviendo al volver a la escena
        self.keysPressed.clear()
        self.player.updateState(-arcade.key.W)
        # Limpio la pantalla y dibujo solo el mundo para que no aparezcan los textos
        self.clear()
        self.camera.use()
        self.scene.draw(pixelated=True)
        self.playerSpritesList.draw(pixelated=True)
        self.backgroundSpriteList.draw(pixelated=True)

        screenshot = arcade.get_image()
        background_texture = arcade.texture.Texture.create_empty(
            "chest_bg", size=(screenshot.width, screenshot.height)
        )
        background_texture.image = screenshot
        newChestScene = Chest(
            chestId=chestId,
            player=self.player,
            previusScene=self,
            backgroundImage=background_texture,
        )
        self.window.show_view(newChestScene)

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.SPACE:
            playerData: PlayerData = {
                "Position": {
                    "center_x": self.player.sprite.center_x,
                    "center_y": self.player.sprite.center_y,
                },
                "Inventory": self.player.inventory,
            }
            DataManager.storeGameData(playerData, "TEST")
            self.callback(Constants.SignalCodes.CHANGE_VIEW, "MENU")
            return True

        if symbol == arcade.key.E:
            return self.handleInteractions()

        self.keysPressed.add(symbol)
        return None

    def handleInteractions(self):
        for interactObject in self.interactSprites:
            if is_near_to_sprite(self.player.sprite, interactObject, tolerance=40):
                return self.processObjectInteraction(interactObject)

        for mineral in self.mineralsLayer:
            if is_near_to_sprite(self.player.sprite, mineral, tolerance=35):
                return self.processMineralInteraction(mineral)

        for mineral in self.mineralsLayer:
            if is_near_to_sprite(self.player.sprite, mineral, tolerance=35):
                mineral.setup()
                mineral.stateMachine.processState(arcade.key.E)
                self.player.addToInventory(mineral.mineral, 1)
                self.updateInventorySprites()
                self.updateInventoryTexts()

                if mineral.should_removed:
                    mineral.remove_from_sprite_lists()
                return True
        return False

    def processObjectInteraction(self, interactObject: arcade.Sprite) -> bool:
        """Procesa la interaccion con un objeto"""
        object_name = interactObject.name.lower()
        if object_name == "door":
            # Cambio de escena y guardo los datos actuales
            playerData: PlayerData = {
                "Position": {
                    "center_x": self.player.sprite.center_x,
                    "center_y": self.player.sprite.center_y,
                },
                "Inventory": self.player.inventory,
            }
            DataManager.storeGameData(playerData, "TEST")
            self.callback(Constants.SignalCodes.CHANGE_VIEW, "MENU")
            return True
        if "chest" in object_name:
            self.openChest(chestId=object_name)
            return True
        return False

    def processMineralInteraction(self, mineral: Mineral) -> bool:
        mineral.setup()
        mineral.stateMachine.processState(arcade.key.E)
        self.player.addToInventory(mineral.mineral, 1)

        # Cambio el valor del hash del inventario para que se actualice
        self.lastInventoryHash = None

        if mineral.should_removed:
            mineral.remove_from_sprite_lists()
        return True

    def on_key_release(self, symbol: int, modifiers: int) -> bool | None:
        self.keysPressed.discard(symbol)
        self.player.updateState(-symbol)

    def on_update(self, delta_time: float) -> bool | None:
        self.player.update_animation(delta_time)
        lastPosition = self.player.sprite.center_x, self.player.sprite.center_y
        self.player.updatePosition()
        self.updateInventoryDisplay()

        # Detección de colisiones
        if self.checkCollisions():
            self.player.sprite.center_x, self.player.sprite.center_y = lastPosition

        for key in self.keysPressed:
            self.player.updateState(key)

        self.camera.position = arcade.math.lerp_2d(
            self.camera.position, self.player.sprite.position, 0.50
        )

    def checkCollisions(self) -> bool:
        """Función para detectar si hay colisiones"""
        physicalCollisions = arcade.check_for_collision_with_lists(
            self.player.sprite, self._collisionList
        )
        if physicalCollisions:
            return True
        # Colisiones con cosas interactuables
        for spriteList in [self.interactSprites, self.mineralsLayer]:
            for sprite in spriteList:
                if arcade.check_for_collision(self.player.sprite, sprite):
                    # No bloquea el movimiento, pero si registra la colisión
                    return True

        return False

    def cleanUp(self) -> None:
        del self.player
        del self.camera
        del self.interactSprites
        del self.mineralsLayer
        del self._collisionList
        del self.floor
        del self.walls
        del self.backgroundObjects
        del self.collisionSprites
        del self.lastInventoryHash
        del self.keysPressed
        del self.inventoryDirty

        del self.playerSpritesList
        del self.backgroundSpriteList
        del self.inventorySpriteList
        del self.itemsInventory
        del self.inventoryTexts
