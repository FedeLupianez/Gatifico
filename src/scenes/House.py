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
        self.playerList: arcade.SpriteList = (
            arcade.SpriteList()
        )  # Lista de sprites del jugador
        self.player = Player()  # Defino el personaje
        self.player.sprite.center_x = Constants.Game.SCREEN_WIDTH // 2
        self.player.sprite.center_y = Constants.Game.SCREEN_HEIGHT // 2
        self.player.setup()
        self.playerList.append(self.player.sprite)
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
        self.playerList.draw(pixelated=True)  # dibuja el personaje

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.SPACE:
            self.callback(Constants.SignalCodes.CHANGE_VIEW, "MENU")
        self.keysPressed.add(symbol)

    def on_key_release(self, symbol: int, modifiers: int) -> bool | None:
        self.keysPressed.discard(symbol)

    def on_update(self, delta_time: float) -> bool | None:
        self.player.update_animation(delta_time)
        self.player.updatePosition()
        if arcade.key.W in self.keysPressed:
            self.player.updateState(arcade.key.W)
        elif arcade.key.A in self.keysPressed:
            self.player.updateState(arcade.key.A)
        elif arcade.key.S in self.keysPressed:
            self.player.updateState(arcade.key.S)
        elif arcade.key.D in self.keysPressed:
            self.player.updateState(arcade.key.D)
        else:
            self.player.updateState(-1)
