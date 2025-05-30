import arcade
import Constants.SignalCodes
import Constants.Game
import scenes.View


class Menu(scenes.View.View):
    def __init__(self, callback):
        try:
            backgroundUrl = "C:/Users/MAIN/Documents/diagramas_nico/Diagramas/salario_trabajador_diagrama.png"
            tileMapUrl = None
            super().__init__(backgroundUrl=backgroundUrl, tileMapUrl=tileMapUrl)
        except FileNotFoundError:
            print("error al inicial la view")
            pass

        self.window.set_mouse_visible(False)
        self.callback = callback

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

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.SPACE:
            print("Espacio detectado")
            self.callback(Constants.SignalCodes.CHANGE_VIEW, "SCHOOL")
