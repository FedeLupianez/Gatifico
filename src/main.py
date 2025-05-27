# Archivo principal del juego, hay que tratar de que este archivo no contenga
# demasiadas líneas, lo ideal sería que se importen los componentes y los personajes acá
import arcade
import constants

from scenes.View import View

main_view = View()

if __name__ == "__main__":
    arcade.run(main_view)
