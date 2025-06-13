from enum import Enum, auto
from characters.Base import Character, State
import arcade
from Constants import Game


class PlayerStates(Enum):
    IDLE = auto()
    X_MOVEMENT = auto()


IdlePath = "src/assets/2D Pixel Dungeon Asset Pack/Character_animation/monsters_idle/skeleton2/v2/skeleton2_v2_{}.png"
MovementPath = "src/assets/Enemy_Animations_Set/enemies-vampire_movement.png"


class Player(Character):
    def __init__(self):
        states = {
            PlayerStates.IDLE: State(IdlePath, 4, 5),
            PlayerStates.X_MOVEMENT: State(MovementPath, 8, 5),
        }
        super().__init__(
            validStates=PlayerStates,
            initialState=PlayerStates.IDLE,
            statesDict=states,
        )

        self.motions = [arcade.key.W, arcade.key.A, arcade.key.S, arcade.key.D]
        self.speed = Game.PLAYER_SPEED

    def movement(self, key: int):
        match key:
            case arcade.key.D:
                self.change_x = self.speed
            case arcade.key.A:
                self.change_x = -self.speed

            case arcade.key.W:
                self.change_y = self.speed
            case arcade.key.S:
                self.change_y = -self.speed

    def cancelMovement(self, key: int):
        if key in (arcade.key.W, arcade.key.S):
            self.change_y = 0
        if key in (arcade.key.A, arcade.key.D):
            self.change_x = 0

    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y
