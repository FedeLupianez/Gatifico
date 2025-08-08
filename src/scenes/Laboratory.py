
from typing import Callable
import arcade
from View import View
from characters.Player import Player

class Laboratory(View):
    def __init__(self, callback: Callable, player: Player):
        backgroundUrl = ":resources:Background/Texture/TX Plant.png"
        super().__init__(background_url=backgroundUrl, tilemap_url=None)
        self.player = player
        self.callback = callback
        self.keys_pressed: set = set()
        self.window.set_mouse_visible(False)

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        pass

    def on_draw(self) -> None:
        pass

    def on_update(self, delta_time: float):
        pass




