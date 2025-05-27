import arcade
import constants


class Player:
    def __init__(self, sprite_url: str) -> None:
        self.speed = constants.PLAYER_SPEED
        # Sprite del personaje
        self.sprite = arcade.Sprite(sprite_url, constants.CHARACTER_SCALE)

    def Actions(self) -> None:
        """Función para manejar los movimientos y acciones del personaje"""
        pass
