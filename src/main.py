# Archivo principal del juego, hay que tratar de que este archivo no contenga
# demasiadas líneas, lo ideal sería que se importen los componentes y los personajes acá
import arcade
from scenes.ViewManager import ViewManager
from characters.Player import Player

def main():
    player = Player()
    viewManager = ViewManager(player=player)
    arcade.run()


if __name__ == "__main__":
    main()
