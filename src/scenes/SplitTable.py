from typing import Callable
import arcade
from scenes.View import View
import DataManager
from Constants import SignalCodes
from characters.Player import Player


class SplitView(View):
    def __init__(
        self,
        callback: Callable[[int, str], None],
        player: Player,
        backgroundUrl: str | None,
        tileMapUrl: str | None,
    ) -> None:
        backgroundUrl = ":resources:Background/Texture/TX Plant.png"
        super().__init__(backgroundUrl, tileMapUrl)
        self.window.set_mouse_visible(True)

        self.callback = callback
        self.player = player
        self.items: dict = player.getInventory() or {"rubi": 4, "rock": 3, "water": 5}

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.SPACE:
            self.callback(SignalCodes.CHANGE_VIEW, "MENU")
