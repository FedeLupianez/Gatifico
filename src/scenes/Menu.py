import arcade
from Constants import Game, SignalCodes
from scenes.View import View
import DataManager

StartButtonPath: str = ":resources:UI/PlayButton.png"
ExitButtonPath: str = ":resources:UI/ExitButton.png"


class Menu(View):
    def __init__(self, callback):
        backgroundUrl = ":resources:UI/MenuBackground.jpg"
        super().__init__(backgroundUrl=backgroundUrl, tileMapUrl=None)

        self.window.set_mouse_visible(True)
        self.spriteList: arcade.SpriteList = arcade.SpriteList()
        self.startButton: arcade.Sprite = arcade.Sprite(StartButtonPath, scale=2)
        self.startButton.center_x = Game.SCREEN_WIDTH // 2
        self.startButton.center_y = Game.SCREEN_HEIGHT // 2

        self.exitButton: arcade.Sprite = arcade.Sprite(ExitButtonPath, scale=2)
        self.exitButton.center_x = Game.SCREEN_WIDTH // 2
        self.exitButton.center_y = (Game.SCREEN_HEIGHT // 2) - 100
        self.spriteList.append(self.startButton)
        self.spriteList.append(self.exitButton)

        self.callback = callback
        self.camera.zoom = 1

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.scene.draw(pixelated=True)
        self.spriteList.draw(pixelated=True)

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        data_to_send = {
            arcade.key.SPACE: "TEST",
            arcade.key.M: "MIX_TABLE",
            arcade.key.C: ("CHEST", "chest_1", {"rubi": 4, "rock": 2}),
            arcade.key.S: "SPLIT_TABLE",
        }
        result = data_to_send.get(symbol, None)
        if result:
            self.callback(SignalCodes.CHANGE_VIEW, result)

    def on_mouse_press(
        self, x: int, y: int, button: int, modifiers: int
    ) -> bool | None:
        if self.startButton.collides_with_point((x, y)):
            print("Iniciando juego")
            self.callback(SignalCodes.CHANGE_VIEW, DataManager.gameData["scene"])
            return

        if self.exitButton.collides_with_point((x, y)):
            print("Saliendo ...")
            self.callback(SignalCodes.CLOSE_WINDOW, "Close window")

    def cleanUp(self):
        """Limpia todos los recursos"""
        self.spriteList.clear()
        del self.spriteList
        del self.startButton
        del self.exitButton
        del self.callback
