import arcade
from Constants import Game, SignalCodes
from scenes.View import View

StartButtonPath: str = ":resources:UI/StartButton.png"
ExitButtonPath: str = ":resources:UI/ExitButton.png"


class Menu(View):
    def __init__(self, callback):
        backgroundUrl = ":resources:Background/Texture/TX Plant.png"
        super().__init__(backgroundUrl=backgroundUrl, tileMapUrl=None)

        self.window.set_mouse_visible(True)
        self.spriteList = arcade.SpriteList()
        self.startButton = arcade.Sprite(StartButtonPath, scale=5)
        self.startButton.center_x = Game.SCREEN_WIDTH // 2
        self.startButton.center_y = Game.SCREEN_HEIGHT // 2

        self.exitButton = arcade.Sprite(ExitButtonPath, scale=5)
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
        if symbol == arcade.key.SPACE:
            self.callback(SignalCodes.CHANGE_VIEW, "TEST")

    def on_mouse_press(
        self, x: int, y: int, button: int, modifiers: int
    ) -> bool | None:
        if self.startButton.collides_with_point((x, y)):
            print("Iniciando juego")
            self.callback(SignalCodes.CHANGE_VIEW, "TEST")
            return

        if self.exitButton.collides_with_point((x, y)):
            print("Saliendo ...")
            self.callback(SignalCodes.CLOSE_WINDOW, "Close window")
