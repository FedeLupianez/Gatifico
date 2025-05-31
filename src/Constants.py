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
    PLAYER_SPEED = 10


class SignalCodes:
    CHANGE_VIEW = 0


class SpriteNames:
    BACKGROUND = "Background"
    PLAYER = "Player"
