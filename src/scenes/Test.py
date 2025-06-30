import arcade
from typing import Tuple
from scenes.View import View
import Constants
from characters.Player import Player
from typing import Callable
from minerals.Mineral import Mineral
from DataManager import dataManager

MineralsResources = dataManager.loadData("Minerals.json")


class Test(View):
    def __init__(self, callback: Callable, player: Player) -> None:
        backgroundUrl = None
        tileMapUrl = ":resources:Maps/Tests.tmx"
        super().__init__(backgroundUrl=backgroundUrl, tileMapUrl=tileMapUrl)
        self.window.set_mouse_visible(False)
        self.callback = callback

        self.player = player  # Defino el personaje

        self.setupSpriteLists()
        self.setupSceneLayers()
        self.setupPlayer()

        self.keysPressed: set = set()

    def setupSpriteLists(self):
        # Listas de Sprites
        self.playerSpritesList: arcade.SpriteList = arcade.SpriteList()
        self.backgroundSpriteList: arcade.SpriteList = arcade.SpriteList()

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

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.SPACE:
            self.callback(Constants.SignalCodes.CHANGE_VIEW, "MENU")
            return

        if symbol == arcade.key.E:
            if self.handleInteractions():
                return

        self.keysPressed.add(symbol)

    def handleInteractions(self):
        if interact_collisions := self.player.sprite.collides_with_list(
            self.interactSprites
        ):
            obj = interact_collisions[0]
            if obj.name.lower() == "door":
                self.callback(Constants.SignalCodes.CHANGE_VIEW, "MENU")
                return True

        if mineralCollisions := self.player.sprite.collides_with_list(
            self.mineralsLayer
        ):
            mineral = mineralCollisions[0]
            mineral.setup()
            mineral.stateMachine.processState(arcade.key.E)
            self.player.addToInventory(mineral.mineral, 1)

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

        background_colisions = self.player.sprite.collides_with_list(
            self.backgroundObjects
        )
        walls_collisions = self.player.sprite.collides_with_list(self.walls)

        if background_colisions or walls_collisions:
            self.player.sprite.center_x, self.player.sprite.center_y = lastPosition

        for key in self.keysPressed:
            self.player.updateState(key)

        self.camera.position = arcade.math.lerp_2d(
            self.camera.position, self.player.sprite.position, 0.50
        )
