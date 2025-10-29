import arcade
from Managers.ViewManager import ViewManager
from characters.Player import Player
import Constants
import DataManager
from pyglet.image import load as load_image


class Main(arcade.Window):
    def __init__(self) -> None:
        # Cargas el icono
        icon = load_image(DataManager.get_path("icon.png"))
        icon = icon.get_image_data()
        #
        super().__init__(
            Constants.Game.SCREEN_WIDTH,
            Constants.Game.SCREEN_HEIGHT,
            title="Gatifico",
            update_rate=Constants.Game.FPS,
            draw_rate=Constants.Game.FPS,
            center_window=True,
            resizable=False,
        )
        self.set_icon(icon)
        arcade.load_font(DataManager.get_path(Constants.Assets.FONT))
        # Manejador de las escenas
        self.ViewManager = ViewManager(self)
        self.player = Player()
        self.player.setup_antique_data()

    def on_close(self):
        if self.ViewManager.current_scene_id != "MENU":
            DataManager.store_actual_data(
                self.player, actualScene=self.ViewManager.current_scene_id
            )
        self.close()


if __name__ == "__main__":
    window = Main()
    arcade.run()
