import arcade
import Constants
from scenes.View import View
from characters.Player import Player


class Menu(View):
    def __init__(self, callback):
        backgroundUrl = Constants.AssetsUrls.MENU_BACKGROUND
        tileMapUrl = None
        super().__init__(backgroundUrl=backgroundUrl, tileMapUrl=tileMapUrl)

        self.window.set_mouse_visible(False)
        self.callback = callback
        self.playerList = arcade.SpriteList()
        self.player = Player()
        self.player.sprite.center_x = Constants.Game.SCREEN_WIDTH // 2
        self.player.sprite.center_y = Constants.Game.SCREEN_HEIGHT // 2
        self.player.setup()
        self.playerList.append(self.player.sprite)

    def on_show_view(self) -> None:
        return super().on_show_view()

    def on_draw(self):
        self.clear()
        self.scene.draw()
        text = arcade.Text(
            "Menu",
            Constants.Game.SCREEN_WIDTH / 2,
            Constants.Game.SCREEN_HEIGHT / 2,
        )
        text.draw()
        self.playerList.draw(pixelated=True)

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.SPACE:
            self.callback(Constants.SignalCodes.CHANGE_VIEW, "HOUSE")

    def on_update(self, delta_time: float) -> bool | None:
        self.player.update_animation(delta_time)
