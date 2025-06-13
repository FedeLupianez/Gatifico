from enum import Enum, auto
from characters.Base import Character, State
import Constants

class PlayerStates(Enum):
    IDLE = auto()
    X_MOVEMENT = auto()

IdlePath = "src/assets/Enemy_Animations_Set/enemies-vampire_idle.png"
MovementPath = "src/assets/Enemy_Animations_Set/enemies-vampire_movement.png"


class Player(Character):
    def __init__(self):
        textures = {
            PlayerStates.IDLE: State(IdlePath, 6),
            PlayerStates.X_MOVEMENT: State(MovementPath, 8),
        }
        super().__init__(validStates=PlayerStates, textureDict=textures)