# Archivo principal del juego, hay que tratar de que este archivo no contenga
# demasiadas líneas, lo ideal sería que se importen los componentes y los personajes acá
import arcade
from scenes.ViewManager import ViewManager


def main():
    viewManager = ViewManager()
    arcade.run()


if __name__ == "__main__":
    main()
