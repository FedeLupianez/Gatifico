# Archivo principal del juego, hay que tratar de que este archivo no contenga
# demasiadas líneas, lo ideal sería que se importen los componentes y los personajes acá
import arcade
from scenes.ViewManager import ViewManager
from characters.Player import Player
import os
import Constants

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)  # Encuentra la ruta al archivo main.py
arcade.resources.add_resource_handle(
    "resources", os.path.join(BASE_DIR, "resources")
)  # Agrega la carpeta resources a los recursos de arcade


class Main(arcade.Window):
    def __init__(self) -> None:
        super().__init__(
            Constants.Game.SCREEN_WIDTH,
            Constants.Game.SCREEN_HEIGHT,
            title="Gatifico",
            update_rate=Constants.Game.FPS,
            draw_rate=Constants.Game.FPS,
        )
        self.player = Player()
        self.ViewManager = ViewManager(self.player, self)


if __name__ == "__main__":
    window = Main()
    arcade.run()
