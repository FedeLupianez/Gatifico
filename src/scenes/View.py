import arcade
import constants


class View(arcade.View):
    Window = arcade.Window(
        constants.SCREEN_WIDTH,
        constants.SCREEN_HEIGHT,
        title="Prueba",
        update_rate=constants.FPS,
    )

    def __init__(self) -> None:
        super().__init__(window=self.Window)
        # Camara para dibujar los elementos
        self.camera_gui = arcade.Camera2D()

        self.scene = self.create_scene("test")

    def create_scene(self, map_url: str):
        print("scene created")
        pass
