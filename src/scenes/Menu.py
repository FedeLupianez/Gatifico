import arcade
from Constants import Game, SignalCodes
import Constants
from scenes.View import View
from DataManager import get_path

Start_button_path: str = get_path("PlayButton.png")
Exit_button_path: str = get_path("ExitButton.png")
Keys_button_path: str = get_path("Keys_button.png")


class Menu(View):
    def __init__(self, callback):
        background_url = get_path("MenuBackground.png")
        super().__init__(background_url=background_url, tilemap_url=None)

        self.window.set_mouse_visible(True)
        self.start_button: arcade.Sprite = arcade.Sprite(Start_button_path, scale=2)
        self.start_button.center_x = Game.SCREEN_CENTER_X
        self.start_button.center_y = Game.SCREEN_CENTER_Y + 100

        self.exit_button: arcade.Sprite = arcade.Sprite(Exit_button_path, scale=2)
        self.exit_button.center_x = Game.SCREEN_WIDTH // 2
        self.exit_button.center_y = self.start_button.center_y - 100

        self.keys_button: arcade.Sprite = arcade.Sprite(Keys_button_path, scale=2)
        self.keys_button.center_x = Game.SCREEN_WIDTH // 2
        self.keys_button.center_y = self.exit_button.center_y - 100

        self.ui_sprites.append(self.keys_button)
        self.ui_sprites.append(self.start_button)
        self.ui_sprites.append(self.exit_button)
        title = arcade.Sprite(get_path("title.png"), scale=12)
        title.center_x = self.window.center_x
        title.center_y = self.window.center_y + 240
        self.ui_sprites.append(title)

        self.callback = callback
        self.camera.zoom = 1

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.scene.draw()
        self.ui_sprites.draw(pixelated=True)

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        data_to_send = {
            arcade.key.SPACE: "TEST",
            arcade.key.F: "FOREST",
            arcade.key.L: "LABORATORY",
            arcade.key.T: "KEYS",
        }
        result = data_to_send.get(symbol, None)
        if result and Constants.Game.DEBUG_MODE:
            self.callback(SignalCodes.CHANGE_VIEW, result)

    def on_mouse_press(
        self, x: int, y: int, button: int, modifiers: int
    ) -> bool | None:
        if self.start_button.collides_with_point((x, y)):
            from DataManager import game_data

            self.callback(
                SignalCodes.CHANGE_VIEW,
                game_data["scene"],
                load_screen=True,
            )
            return

        if self.exit_button.collides_with_point((x, y)):
            self.callback(SignalCodes.CLOSE_WINDOW, "Close window")
            return

        if self.keys_button.collides_with_point((x, y)):
            self.callback(SignalCodes.CHANGE_VIEW, "KEYS")
            return

    def clean_up(self):
        """Limpia todos los recursos"""
        self.ui_sprites.clear()
        del self.start_button
        del self.exit_button
        del self.callback
