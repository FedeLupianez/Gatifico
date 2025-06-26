import arcade
from scenes.View import View
import Constants
from characters.Player import Player
from typing import Callable


class Test(View):
    def __init__(self, callback: Callable, player: Player) -> None:
        backgroundUrl = None
        tileMapUrl = "src/assets/Maps/Tests.tmx"
        super().__init__(backgroundUrl=backgroundUrl, tileMapUrl=tileMapUrl)
        self.window.set_mouse_visible(False)
        self.callback = callback

        # Listas de Sprites
        self.playerSpritesList: arcade.SpriteList = arcade.SpriteList()
        self.backgroundSpriteList: arcade.SpriteList = arcade.SpriteList()

        self.player = player  # Defino el personaje
        self.player.sprite.center_x = Constants.Game.SCREEN_WIDTH // 2
        self.player.sprite.center_y = Constants.Game.SCREEN_HEIGHT // 2
        self.player.setup()
        # Camara para seguir al jugador :
        self.camera.zoom = 2.5

        # Capas de vista :
        self.floorLayer = self.scene["Piso"]
        self.wallsLayer = self.scene["Paredes"]
        self.backgroundObjects = self.scene["Objetos"]

        # Capas de colisiones :
        self.collisionSprites = self.loadObjectLayers("Colisiones", self.tileMap)
        self.interactSprites = self.loadObjectLayers("Interactuables", self.tileMap)

        self.playerSpritesList.append(self.player.sprite)
        self.keysPressed: set = set()

    def on_show_view(self) -> None:
        return super().on_show_view()

    def on_draw(self) -> bool | None:
        # Función que se llama cada vez que se dibuja la escena
        self.clear()  # limpia la pantalla
        self.camera.use()
        self.scene.draw(pixelated=True)  # dibuja la escena
        self.playerSpritesList.draw(pixelated=True)  # dibuja el personaje
        self.backgroundSpriteList.draw(pixelated=True)

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.SPACE:
            self.callback(Constants.SignalCodes.CHANGE_VIEW, "MENU")

        if symbol == arcade.key.E:
            interact_collisions = self.player.sprite.collides_with_list(
                self.interactSprites
            )
            if interact_collisions:
                print(interact_collisions[0].name)
                if interact_collisions[0].name.lower() == "door":
                    self.callback(Constants.SignalCodes.CHANGE_VIEW, "MENU")

        self.keysPressed.add(symbol)

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
        walls_collisions = self.player.sprite.collides_with_list(self.wallsLayer)

        if background_colisions or walls_collisions:
            self.player.sprite.center_x, self.player.sprite.center_y = lastPosition

        for key in self.keysPressed:
            self.player.updateState(key)
        self.camera.position = arcade.math.lerp_2d(
            self.camera.position, self.player.sprite.position, 0.50
        )
