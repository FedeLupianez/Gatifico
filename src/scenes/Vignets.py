from typing import Callable
import arcade
import Constants
from scenes.View import View
from DataManager import get_path, texture_manager
from Constants import SignalCodes


class Vignets(View):
    def __init__(self, callback: Callable, **kwargs) -> None:
        super().__init__(None, None)
        self.callback = callback
        self.window.set_mouse_visible(False)
        self.image_idx = 0
        self.images: list[arcade.Texture] = []
        for i in range(15):
            path = get_path(f"figure_{i + 1}.png")
            texture = texture_manager.load_or_get_texture(path)
            self.images.append(texture)

        self.rect = arcade.rect.Rect(
            left=0,
            right=self.window.width,
            top=0,
            bottom=self.window.height,
            width=self.window.width,
            height=self.window.height,
            x=Constants.Game.SCREEN_CENTER_X,
            y=Constants.Game.SCREEN_CENTER_Y,
        )
        self.actual_vignet = self.images[self.image_idx]

    def on_draw(self) -> None:
        arcade.draw_texture_rect(self.actual_vignet, self.rect)

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.SPACE:
            self.image_idx += 1
            if self.image_idx >= len(self.images):
                self.callback(SignalCodes.CHANGE_VIEW, "MENU")
                return
            self.actual_vignet = self.images[self.image_idx]

    def clean_up(self) -> None:
        del self.actual_vignet
        del self.rect
        del self.callback
        del self.image_idx
        del self.images
