# Archivo principal del juego, hay que tratar de que este archivo no contenga
# demasiadas líneas, lo ideal sería que se importen los componentes y los personajes acá
import arcade
from scenes.ViewManager import ViewManager
from characters.Player import Player
import os

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)  # Encuentra la ruta al archivo main.py
arcade.resources.add_resource_handle(
    "resources", os.path.join(BASE_DIR, "resources")
)  # Agrega la carpeta resources a los recursos de arcade


def main():
    player = Player()
    viewManager = ViewManager(player)
    arcade.run()


if __name__ == "__main__":
    main()
