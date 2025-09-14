# Archivo para contener las constantes del juego
# usando el diseño singleton


class Game:
    # Tamaños de la pantalla :
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    SCREEN_CENTER_X = SCREEN_WIDTH / 2
    SCREEN_CENTER_Y = SCREEN_HEIGHT / 2

    FPS = 1 / 60

    FOREST_ZOOM_CAMERA = 4  # Zoom de la camara en el bosque
    DEBUG_MODE = True


class PlayerConfig:
    # Valores del personaje principal :
    SCALE = 0.5
    SPEED = 0.5
    INVENTORY_POSITION = (550, 100)
    HITBOX_WIDTH = 27
    HITBOX_HEIGHT = 30


class SignalCodes:
    CHANGE_VIEW = 0
    CLOSE_WINDOW = 1
    PAUSE_GAME = 2


class AssetsConstants:
    # Indice inicial de los sprites (comienzan por 1)
    INITIAL_INDEX = 1


class Filter:
    DARK = (0, 0, 0, 100)
