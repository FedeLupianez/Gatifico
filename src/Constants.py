# Archivo para contener las constantes del juego
# usando el diseño singleton


from arcade import close_window


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


class SignalCodes:
    CHANGE_VIEW = 0
    CLOSE_WINDOW = 1


class SpriteNames:
    BACKGROUND = "Background"
    PLAYER = "Player"


class AssetsUrls:
    # Indice inicial de los sprites (comienzan por 1)
    INITIAL_INDEX = 0
    # Paths de los fondos
    MENU_BACKGROUND = "src/assets/2D Pixel Dungeon Asset Pack/interface/arrow_1.png"
    HOUSE_BACKGROUND = "src/assets/2D Pixel Dungeon Asset Pack/Dungeon_Tileset_at.png"
