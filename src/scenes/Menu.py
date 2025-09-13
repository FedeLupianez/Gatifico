import arcade
from Constants import Game, SignalCodes
import Constants
from scenes.View import View
import DataManager

Start_button_path: str = "src/resources/UI/PlayButton.png"
Exit_button_path: str = "src/resources/UI/ExitButton.png"


class Menu(View):
    def __init__(self, callback):
        background_url = "src/resources/UI/MenuBackground.jpg"
        super().__init__(background_url=background_url, tilemap_url=None)

        self.window.set_mouse_visible(True)
        self.sprite_list: arcade.SpriteList = arcade.SpriteList()
        self.start_button: arcade.Sprite = arcade.Sprite(Start_button_path, scale=2)
        self.start_button.center_x = Game.SCREEN_WIDTH // 2
        self.start_button.center_y = Game.SCREEN_HEIGHT // 2

        self.exit_button: arcade.Sprite = arcade.Sprite(Exit_button_path, scale=2)
        self.exit_button.center_x = Game.SCREEN_WIDTH // 2
        self.exit_button.center_y = (Game.SCREEN_HEIGHT // 2) - 100
        self.sprite_list.append(self.start_button)
        self.sprite_list.append(self.exit_button)

        self.title = arcade.Text(
            text="Gatifico",
            font_size=80,
            color=(0, 0, 0),
            x=Game.SCREEN_CENTER_X,
            y=Game.SCREEN_CENTER_Y + 150,
            anchor_x="center",
        )

        self.callback = callback
        self.camera.zoom = 1

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.scene.draw(pixelated=True)
        self.sprite_list.draw(pixelated=True)
        self.title.draw()

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        data_to_send = {
            arcade.key.SPACE: "TEST",
            arcade.key.M: "MIX_TABLE",
            arcade.key.C: ("CHEST", "chest_1", {"rubi": 4, "piedra": 2}),
            arcade.key.S: "SPLIT_TABLE",
            arcade.key.L: "LABORATORY",
            arcade.key.D: "SELL",
        }
        result = data_to_send.get(symbol, None)
        if result and Constants.Game.DEBUG_MODE:
            self.callback(SignalCodes.CHANGE_VIEW, result)

    def on_mouse_press(
        self, x: int, y: int, button: int, modifiers: int
    ) -> bool | None:
        if self.start_button.collides_with_point((x, y)):
            self.callback(
                SignalCodes.CHANGE_VIEW,
                DataManager.game_data["scene"],
                load_screen=True,
            )
            return

        if self.exit_button.collides_with_point((x, y)):
            self.callback(SignalCodes.CLOSE_WINDOW, "Close window")

    def clean_up(self):
        """Limpia todos los recursos"""
        self.sprite_list.clear()
        del self.sprite_list
        del self.start_button
        del self.exit_button
        del self.callback
