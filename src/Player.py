import arcade
import Constants.Game


class Player:
    def __init__(self, sprite_url: str) -> None:
        self.speed = Constants.Game.PLAYER_SPEED
        # Variable con la posicion del personaje
        self.position: arcade.Vec2 = arcade.Vec2(0, 0)

        # Sprite del personaje
        self.spriteName = "Player"
        self.sprite = arcade.Sprite(sprite_url, Constants.Game.CHARACTER_SCALE)

    def Actions(self) -> None:
        """Función para manejar los movimientos y acciones del personaje"""
        pass
