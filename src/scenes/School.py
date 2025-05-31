import arcade
import scenes.View as ViewScene
import Constants


class School(ViewScene.View):
    def __init__(self, callback) -> None:
        backgroundUrl = "C:/Users/MAIN/Pictures/FotosViejas/f14548008.jpg"
        tileMapUrl = None
        super().__init__(backgroundUrl=backgroundUrl, tileMapUrl=tileMapUrl)
        self.window.set_mouse_visible(False)
        self.callback = callback

    def on_show_view(self) -> None:
        return super().on_show_view()

    def on_draw(self) -> bool | None:
        self.clear()
        self.scene.draw()
        text = arcade.Text(
            "Escuela", Constants.Game.SCREEN_WIDTH / 2, Constants.Game.SCREEN_HEIGHT / 2
        )
        text.draw()

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.SPACE:
            print("Cambio de escena")
            self.callback(Constants.SignalCodes.CHANGE_VIEW, "MENU")
