import arcade
from scenes.View import View
import Constants
from characters.Player import Player
from typing import Callable


class House(View):
    def __init__(self, callback: Callable) -> None:
        backgroundUrl = Constants.AssetsUrls.HOUSE_BACKGROUND
        tileMapUrl = None
        super().__init__(backgroundUrl=backgroundUrl, tileMapUrl=tileMapUrl)
        self.window.set_mouse_visible(False)
        self.callback = callback

        # Listas de Sprites
        self.playerSpritesList: arcade.SpriteList = arcade.SpriteList()
        self.backgroundSpriteList: arcade.SpriteList = arcade.SpriteList()

        self.player = Player()  # Defino el personaje
        self.player.sprite.center_x = Constants.Game.SCREEN_WIDTH // 2
        self.player.sprite.center_y = Constants.Game.SCREEN_HEIGHT // 2
        self.player.setup()

        self.obstacle: arcade.Sprite = arcade.Sprite(
            "src/assets/2D Pixel Dungeon Asset Pack/interface/square_left_4.png"
        )
        self.door: arcade.Sprite = arcade.Sprite(
            "src/assets/2D Pixel Dungeon Asset Pack/interface/square_left_4.png"
        )
        self.obstacle.center_x = 100
        self.obstacle.center_y = 100

        self.door.center_x = Constants.Game.SCREEN_WIDTH - 100
        self.door.center_y = Constants.Game.SCREEN_HEIGHT // 2
        self.playerSpritesList.append(self.player.sprite)
        self.backgroundSpriteList.append(self.obstacle)
        self.backgroundSpriteList.append(self.door)
        self.keysPressed: set = set()

    def on_show_view(self) -> None:
        return super().on_show_view()

    def on_draw(self) -> bool | None:
        # Función que se llama cada vez que se dibuja la escena
        self.clear()  # limpia la pantalla
        self.scene.draw()  # dibuja la escena
        text = arcade.Text(
            "Casa", Constants.Game.SCREEN_WIDTH / 2, Constants.Game.SCREEN_HEIGHT / 2
        )
        text.draw()
        self.playerSpritesList.draw(pixelated=True)  # dibuja el personaje
        self.backgroundSpriteList.draw(pixelated=True)

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.SPACE:
            self.callback(Constants.SignalCodes.CHANGE_VIEW, "MENU")
        self.keysPressed.add(symbol)

    def on_key_release(self, symbol: int, modifiers: int) -> bool | None:
        self.keysPressed.discard(symbol)

    def on_update(self, delta_time: float) -> bool | None:
        self.player.update_animation(delta_time)
        lastPosition = self.player.sprite.center_x, self.player.sprite.center_y
        self.player.updatePosition()

        for sprite in self.backgroundSpriteList:
            if sprite.collides_with_list(self.playerSpritesList):
                self.player.sprite.center_x, self.player.sprite.center_y = lastPosition
                if sprite == self.door:
                    self.callback(Constants.SignalCodes.CHANGE_VIEW, "MENU")

        if not (self.keysPressed):
            self.player.updateState(-1)
            return

        for key in self.keysPressed:
            self.player.updateState(key)
