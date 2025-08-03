# Archivo para contener las constantes del juego
# usando el diseño singleton


class Game:
    # Tamaños de la pantalla :
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    SCREEN_CENTER_X = SCREEN_WIDTH / 2
    SCREEN_CENTER_Y = SCREEN_HEIGHT / 2

    FPS = 1 / 60

    FOREST_ZOOM_CAMERA = 3.5  # Zoom de la camara en el bosque
    DEBUG_MODE = True


class PlayerConfig:
    # Valores del personaje principal :
    CHARACTER_SCALE = 0.5
    PLAYER_SPEED = 5
    PLAYER_INVENTORY_POSITION = (550, 100)


class SignalCodes:
    CHANGE_VIEW = 0
    CLOSE_WINDOW = 1


class AssetsConstants:
    # Indice inicial de los sprites (comienzan por 1)
    INITIAL_INDEX = 0


class Filter:
    DARK = (0, 0, 0, 100)
