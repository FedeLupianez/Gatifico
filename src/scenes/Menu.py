import arcade
import Constants
import scenes.View
from characters.Player import Player

class Menu(scenes.View.View):
    def __init__(self, callback):
        backgroundUrl = Constants.AssetsUrls.MENU_BACKGROUND
        tileMapUrl = None
        super().__init__(backgroundUrl=backgroundUrl, tileMapUrl=tileMapUrl)

        self.window.set_mouse_visible(False)
        self.callback = callback
        self.player = Player()

    def on_show_view(self) -> None:
        return super().on_show_view()

    def on_draw(self):
        self.clear()
        self.scene.draw()
        text = arcade.Text(
            "A coloquio",
            Constants.Game.SCREEN_WIDTH / 2,
            Constants.Game.SCREEN_HEIGHT / 2,
        )
        text.draw()
        self.player.draw()

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.SPACE:
            print("Espacio detectado")
            self.callback(Constants.SignalCodes.CHANGE_VIEW, "SCHOOL")

    def on_update(self):
        self.player.update_animation()
