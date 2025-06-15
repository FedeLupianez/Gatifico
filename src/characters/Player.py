import arcade
from Constants import Game
from StateMachine import StateMachine


IdlePath = "src/assets/2D Pixel Dungeon Asset Pack/Character_animation/monsters_idle/skeleton2/v2/skeleton2_v2_{}.png"
MovementPath = "src/assets/Enemy_Animations_Set/enemies-vampire_movement.png"


class Player(StateMachine):
    def __init__(self):
        super().__init__()
        self.motions = [arcade.key.W, arcade.key.A, arcade.key.S, arcade.key.D]
        self.actualAnimationPath: str = IdlePath.replace("{}", "1")
        self.sprite = arcade.Sprite(self.actualAnimationPath)
        self.speed = Game.PLAYER_SPEED
        self.actualAnimationFrames: int = 0
        self.frames: list[arcade.Texture] = []
        self.textureIndex = 0
        self.animationTimer: float = 0.0

    def handleEvent(self, event: int):
        if event < 0:
            return "IDLE"

        match event:
            case arcade.key.W:
                return "UP"
            case arcade.key.A:
                return "LEFT"
            case arcade.key.S:
                return "DOWN"
            case arcade.key.D:
                return "RIGHT"
            case _:
                return self.actualState

    def IdleState(self, event):
        self.sprite.change_x = 0
        self.sprite.change_y = 0
        self.actualAnimationPath = IdlePath
        self.actualAnimationFrames = 4
        self.updateSpriteList()
        return self.handleEvent(event)

    def LeftState(self, event):
        self.sprite.change_x = -Game.PLAYER_SPEED
        self.sprite.change_y = 0
        self.actualAnimationPath = IdlePath
        self.actualAnimationFrames = 4
        self.updateSpriteList()
        return self.handleEvent(event)

    def RightState(self, event):
        self.sprite.change_x = Game.PLAYER_SPEED
        self.sprite.change_y = 0
        self.actualAnimationPath = IdlePath
        self.actualAnimationFrames = 4
        self.updateSpriteList()
        return self.handleEvent(event)

    def DownState(self, event):
        self.sprite.change_y = -Game.PLAYER_SPEED
        self.sprite.change_x = 0
        self.actualAnimationPath = IdlePath
        self.actualAnimationFrames = 4
        self.updateSpriteList()
        return self.handleEvent(event)

    def UpState(self, event):
        self.sprite.change_y = Game.PLAYER_SPEED
        self.sprite.change_x = 0
        self.actualAnimationPath = IdlePath
        self.updateSpriteList()
        return self.handleEvent(event)

    def setup(self):
        self.addState("IDLE", self.IdleState)
        self.addState("LEFT", self.LeftState)
        self.addState("RIGHT", self.RightState)
        self.addState("DOWN", self.DownState)
        self.addState("UP", self.UpState)

    def updatePosition(self):
        self.sprite.center_x += self.sprite.change_x
        self.sprite.center_y += self.sprite.change_y

    def updateState(self, event: int):
        self.processState(event)
        print("Estado actual : ", self.actualState)

    def updateSpriteList(self):
        for i in range(1, self.actualAnimationFrames + 1):
            route = self.actualAnimationPath.replace("{}", str(i))
            self.frames.append(arcade.load_texture(route))
        self.textureIndex = 1

    def updateFrame(self):
        self.sprite.texture = self.frames[self.textureIndex]

    def update_animation(self, deltaTime: float):
        if not self.frames:
            return
        self.animationTimer += deltaTime
        if self.animationTimer > 0.1:
            self.animationTimer = 0
            self.textureIndex = (self.textureIndex + 1) % len(self.frames)
            self.updateFrame()
