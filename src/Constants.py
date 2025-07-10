# Archivo para contener las constantes del juego
# usando el diseño singleton


class Game:
    # Tamaños de la pantalla :
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    FPS = 1 / 60

    # Personajes :
    CHARACTER_SCALE = 1

    # Valores del personaje principal :
    PLAYER_SPEED = 5
    PLAYER_WIDTH = 10
    PLAYER_HEIGHT = 10
    PLAYER_INVENTORY_POSITION = (550, 100)
    FOREST_ZOOM_CAMERA = 3.5


class SignalCodes:
    CHANGE_VIEW = 0
    CLOSE_WINDOW = 1


class AssetsConstants:
    # Indice inicial de los sprites (comienzan por 1)
    INITIAL_INDEX = 0
