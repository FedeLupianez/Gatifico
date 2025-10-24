# Archivo para contener las constantes del juego
# usando el diseño singleton


class Game:
    # Tamaños de la pantalla :
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    SCREEN_CENTER_X = SCREEN_WIDTH / 2
    SCREEN_CENTER_Y = SCREEN_HEIGHT / 2

    FPS = 1 / 61

    FOREST_ZOOM_CAMERA = 4  # Zoom de la camara en el bosque
    CAMERA_LERP_FAST = 0.25
    CAMERA_LERP_SLOW = 0.06
    DEBUG_MODE = True


class PlayerConfig:
    # Valores del personaje principal :
    SCALE = 0.5
    SPEED = 0.5
    KNOCKBACK = 15
    HURT_COLDOWN = 0.2
    MAX_ITEMS_IN_INVENTORY = 5
    MAX_ITEMS_CANT = 64
    INVENTORY_POSITION = (523, 100)
    HITBOX_WIDTH = 27
    HITBOX_HEIGHT = 30
    SELF_ATTACK_COOLDOWN = 0.1


class SignalCodes:
    CHANGE_VIEW = 0
    CLOSE_WINDOW = 1
    PAUSE_GAME = 2
    SILENCE_BACKGROUND = 3
    RESUME_BACKGROUND = 4


class Assets:
    # Indice inicial de los sprites (comienzan por 1)
    INITIAL_INDEX = 1
    FONT = "born2bsporty-fs.regular.otf"
    FONT_NAME = "Born2bSporty FS"


class Filter:
    DARK = (0, 0, 0, 100)
