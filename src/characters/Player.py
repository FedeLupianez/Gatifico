import arcade
from Constants import Game, AssetsUrls
import Constants
from StateMachine import StateMachine


IdleFrontPath = "src/assets/Player/Idle/Front/Front_Idle_{}.png"
IdleBackPath = "src/assets/Player/Idle/Back/Back_Idle_{}.png"
IdleSidePath = "src/assets/Player/Idle/Side/Side_Idle_{}.png"

RunFrontPath = "src/assets/Player/Run/Front/Front_Run_{}.png"
RunBackPath = "src/assets/Player/Run/Back/Back_Run_{}.png"
RunSidePath = "src/assets/Player/Run/Side/Side_Run_{}.png"


# Defino los id de los estados para no repetir magic strings
IDLE_SIDE = "IDLE_SIDE"
IDLE_FRONT = "IDLE_FRONT"
IDLE_BACK = "IDLE_BACk"
LEFT = "LEFT"
RIGHT = "RIGHT"
UP = "UP"
DOWN = "DOWN"


class Player(StateMachine):
    def __init__(self):
        super().__init__(IDLE_FRONT)
        self.motions = [arcade.key.W, arcade.key.A, arcade.key.S, arcade.key.D]
        # Todos los path tienen llaves {} donde iría el numero de sprite
        self.actualAnimationPath: str = IdleFrontPath.replace(
            "{}",
            str(
                AssetsUrls.INITIAL_INDEX
            ),  # como es el sprite inicial lo intercambiamos por el indice inicial
        )
        self.sprite: arcade.Sprite = arcade.Sprite(
            self.actualAnimationPath
        )  # objeto sprite del personaje
        self.speed = Game.PLAYER_SPEED
        self.actualAnimationFrames: int = 0  # cantidad de frames de la animacion
        self.frames: list[arcade.Texture] = []  # lista de texturas
        self.textureIndex = 0  # indice actual de la textura
        self.animationTimer: float = 0.0  # timer de la animacion
        self.sprite.scale = Constants.Game.CHARACTER_SCALE
        self.spriteCache: dict[
            str, arcade.Texture
        ] = {}  # Diccionario con las texturas cargadas para ahorrar llamdas a memoria

    def handleMovementEvent(self, key: int):
        """Función que se llama siempre que se toca una tecla de movimiento
        Args :
            key (int) : Tecla presionada
        """
        # Si la key es negativa significa que se soltó una tecla,
        # por lo que regresa al estado IDLE
        if key < 0:
            return IDLE_FRONT
        # Si es que presionó una tecla, se cambia al estado correspondiente
        match key:
            case arcade.key.W:
                return UP
            case arcade.key.A:
                return LEFT
            case arcade.key.S:
                return DOWN
            case arcade.key.D:
                return RIGHT
            case _:
                # Si no es ninguna de las otras teclas retorna el estado actual
                return self.actualStateId

    # Definición de los estados como funciones
    def IdleFront(self, event):
        self.sprite.change_x = 0
        self.sprite.change_y = 0
        self.actualAnimationPath = IdleFrontPath
        self.actualAnimationFrames = 1
        return self.handleMovementEvent(event)

    def IdleBack(self, event):
        self.sprite.change_x = 0
        self.sprite.change_y = 0
        self.actualAnimationPath = IdleBackPath
        self.actualAnimationFrames = 1
        return self.handleMovementEvent(event)

    def IdleSide(self, event):
        self.sprite.change_x = 0
        self.sprite.change_y = 0
        self.actualAnimationPath = IdleSidePath
        self.actualAnimationFrames = 1
        return self.handleMovementEvent(event)

    def LeftState(self, event):
        self.sprite.change_x = -Game.PLAYER_SPEED
        self.sprite.change_y = 0
        self.actualAnimationPath = RunSidePath
        self.actualAnimationFrames = 1
        self.sprite.scale_x = -abs(self.sprite.scale_x)
        return self.handleMovementEvent(event)

    def RightState(self, event):
        self.sprite.change_x = Game.PLAYER_SPEED
        self.sprite.change_y = 0
        self.actualAnimationPath = RunSidePath
        self.actualAnimationFrames = 1
        self.sprite.scale_x = abs(self.sprite.scale_x)
        return self.handleMovementEvent(event)

    def DownState(self, event):
        self.sprite.change_y = -Game.PLAYER_SPEED
        self.sprite.change_x = 0
        self.actualAnimationPath = RunFrontPath
        self.actualAnimationFrames = 1
        return self.handleMovementEvent(event)

    def UpState(self, event):
        self.sprite.change_y = Game.PLAYER_SPEED
        self.sprite.change_x = 0
        self.actualAnimationPath = RunBackPath
        return self.handleMovementEvent(event)

    def setup(self):
        """Función para configurar la maquina de estados del personaje"""
        self.addState(IDLE_FRONT, self.IdleFront)
        self.addState(IDLE_BACK, self.IdleBack)
        self.addState(IDLE_SIDE, self.IdleSide)
        self.addState(LEFT, self.LeftState)
        self.addState(RIGHT, self.RightState)
        self.addState(DOWN, self.DownState)
        self.addState(UP, self.UpState)

    def updatePosition(self):
        """Actualiza la posición del personaje segun la velocidad actual"""
        self.sprite.center_x += self.sprite.change_x
        self.sprite.center_y += self.sprite.change_y

    def updateState(self, event: int):
        """Actualiza el estado actual del personaje"""
        tempState = self.actualStateId
        self.processState(event)  # Procesa el estado
        if self.actualStateId != tempState:
            self.updateSpriteList()

    def updateSpriteList(self):
        """
        Actualiza la lista de texturas segun el estado actual
        """
        print("cargando nuevas texturas ...\n")
        self.frames.clear()
        for i in range(
            AssetsUrls.INITIAL_INDEX,
            self.actualAnimationFrames + AssetsUrls.INITIAL_INDEX,
        ):
            route = self.actualAnimationPath.replace("{}", str(i))
            # Si el path de la textura ya estaba cargada no hay que cargarla de nuevo
            if route in self.spriteCache.keys():
                # Agrega la textura de la cache a la lista de frames
                self.frames.append(self.spriteCache[route])
                continue
            # Si no está en la cache, la carga y la guarda en ella
            self.spriteCache[route] = arcade.load_texture(route)
        self.textureIndex = 0

    def updateFrame(self):
        self.sprite.texture = self.frames[self.textureIndex]

    def update_animation(self, deltaTime: float):
        """Función para actualizar la animación del personaje"""
        if not self.frames:
            return
        self.animationTimer += deltaTime
        if self.animationTimer > 0.1:
            self.animationTimer = 0
            self.textureIndex = (self.textureIndex + 1) % self.actualAnimationFrames
            self.updateFrame()
