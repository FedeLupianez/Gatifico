from typing import Callable
from DataManager import get_path
from scenes.View import View
import arcade
from Constants import SignalCodes


class Keys(View):
    def __init__(self, callback: Callable) -> None:
        super().__init__(background_url=get_path("keys.png"), tilemap_url=None)
        self.callback = callback
        self.window.set_mouse_visible(True)
        self.button_exit = arcade.Sprite(get_path("exit_symbol.png"), scale=4)
        self.button_exit.center_x = 50
        self.button_exit.center_y = self.window.height - 50
        self.ui_sprites.append(self.button_exit)

    def on_draw(self) -> bool | None:
        self.scene.draw(pixelated=True)
        self.ui_sprites.draw(pixelated=True)

    def on_mouse_press(
        self, x: int, y: int, button: int, modifiers: int
    ) -> bool | None:
        if self.button_exit.collides_with_point((x, y)):
            self.callback(SignalCodes.CHANGE_VIEW, "MENU")

    def clean_up(self) -> None:
        del self.button_exit
        del self.callback
