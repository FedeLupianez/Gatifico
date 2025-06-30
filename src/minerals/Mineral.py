import arcade
from StateMachine import StateMachine

BIG_SIZE = "big"
MID_SIZE = "mid"
SMALL_SIZE = "small"

mineralAttributes: dict[str, dict] = {
    "rock": {
        SMALL_SIZE: {"path": ":resources:Minerals/Rock/Rock_Small.png", "touches": 1},
        MID_SIZE: {"path": ":resources:Minerals/Rock/Rock_Mid.png", "touches": 2},
        BIG_SIZE: {"path": ":resources:Minerals/Rock/Rock_Big.png", "touches": 3},
    }
}

BIG_STATE = "BIG"
MID_STATE = "MID"
SMALL_STATE = "SMALL"
KILL_STATE = "KILL"


class Mineral(arcade.Sprite):
    def __init__(self, mineral: str, size_type: str, center_x: float, center_y: float):
        super().__init__(
            path_or_texture=mineralAttributes[mineral][size_type]["path"],
            center_x=center_x,
            center_y=center_y,
        )

        initialState = ""
        if size_type.lower() == BIG_SIZE:
            initialState = BIG_STATE
        elif size_type.lower() == MID_SIZE:
            initialState = MID_STATE
        else:
            initialState = SMALL_STATE
        self.stateMachine = StateMachine(initialState)

        self.mineral = mineral
        self.size_type = size_type

        self.touches = mineralAttributes[mineral][size_type]["touches"]
        self.actualTouches = 0

        self.should_removed: bool = False

    def bigSizeState(self, key: int):
        self.size_type = BIG_SIZE
        data = mineralAttributes[self.mineral][BIG_SIZE]
        newTexturePath = data["path"]
        self.updateSprite(newTexturePath)
        if key != arcade.key.E:
            return self.stateMachine.actualStateId

        self.actualTouches += 1
        print(self.actualTouches, self.touches)
        if self.actualTouches >= self.touches:
            self.actualTouches = 0
            return MID_STATE
        return BIG_STATE

    def midSizeState(self, key: int):
        self.size_type = MID_SIZE
        data = mineralAttributes[self.mineral][MID_SIZE]
        newTexturePath = data["path"]
        self.touches = data["touches"]
        self.updateSprite(newTexturePath)

        if key != arcade.key.E:
            return self.stateMachine.actualStateId
        self.actualTouches += 1

        print(self.actualTouches, self.touches)
        if self.actualTouches >= self.touches:
            self.actualTouches = 0
            return SMALL_STATE
        return MID_STATE

    def smallSizeState(self, key: int):
        self.size_type = SMALL_SIZE
        data = mineralAttributes[self.mineral][SMALL_SIZE]
        newTexturePath = data["path"]
        self.touches = data["touches"]
        self.updateSprite(newTexturePath)

        if key != arcade.key.E:
            return self.stateMachine.actualStateId
        self.actualTouches += 1

        if self.actualTouches >= self.touches:
            self.actualTouches = 0
            return KILL_STATE
        return SMALL_STATE

    def killState(self, key: int):
        self.should_removed = True

    def setup(self):
        self.stateMachine.addState(BIG_STATE, self.bigSizeState)
        self.stateMachine.addState(MID_STATE, self.midSizeState)
        self.stateMachine.addState(SMALL_STATE, self.smallSizeState)
        self.stateMachine.addState(KILL_STATE, self.killState)

    def updateState(self, key: int):
        self.stateMachine.processState(key)

    def updateSprite(self, newPath: str):
        self.texture = arcade.load_texture(newPath)
