import arcade
from Constants import Game, AssetsUrls
import Constants
from StateMachine import StateMachine

# Paths a las texturas del personaje segun su estado
IdleFrontPath = ":resources:Player/Idle/Front/Front_Idle_{}.png"
IdleBackPath = ":resources:Player/Idle/Back/Back_Idle_{}.png"
IdleSidePath = ":resources:Player/Idle/Side/Side_Idle_{}.png"

RunFrontPath = ":resources:Player/Run/Front/Front_Run_{}.png"
RunBackPath = ":resources:Player/Run/Back/Back_Run_{}.png"
RunSidePath = ":resources:Player/Run/Side/Side_Run_{}.png"

WalkFrontPath = ":resources:Player/Walk/Front/Front_Walk_{}.png"
WalkBackPath = ":resources:Player/Walk/Back/Back_Walk_{}.png"
WalkSidePath = ":resources:Player/Walk/Side/Side_Walk_{}.png"

# Defino los id de los estados para no repetir magic strings
IDLE_SIDE_LEFT = "IDLE_SIDE_LEFT"
IDLE_SIDE_RIGHT = "IDLE_SIDE_RIGHT"
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
        self.actualAnimationFrames: int = 5  # cantidad de frames de la animacion
        self.frames: list[arcade.Texture] = []  # lista de texturas
        self.textureIndex = 0  # indice actual de la textura
        self.animationTimer: float = 0.0  # timer de la animacion
        self.sprite.scale = Constants.Game.CHARACTER_SCALE
        self.spriteCache: dict[
            str, arcade.Texture
        ] = {}  # Diccionario con las texturas cargadas para ahorrar llamdas a memoria
        # Diccionario para el inventario
        self.inventory: dict[str, int] = {}

    def handleMovementEvent(self, key: int):
        """Función que se llama siempre que se toca una tecla de movimiento
        Args :
            key (int) : Tecla presionada
        """
        # Si la tecla es negativa significa que se soltó una tecla
        if key < 0:
            match abs(key):
                case arcade.key.W:
                    return IDLE_BACK
                case arcade.key.S:
                    return IDLE_FRONT
                case arcade.key.A:
                    return IDLE_SIDE_LEFT
                case arcade.key.D:
                    return IDLE_SIDE_RIGHT
                case _:
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
        self.actualAnimationFrames = 5
        return self.handleMovementEvent(event)

    def IdleBack(self, event):
        self.sprite.change_x = 0
        self.sprite.change_y = 0
        self.actualAnimationPath = IdleBackPath
        self.actualAnimationFrames = 5
        return self.handleMovementEvent(event)

    def IdleSideLeft(self, event):
        self.sprite.change_x = 0
        self.sprite.change_y = 0
        self.actualAnimationPath = IdleSidePath
        self.actualAnimationFrames = 5
        self.sprite.scale_x = -abs(self.sprite.scale_x)
        return self.handleMovementEvent(event)

    def IdleSideRight(self, event):
        self.sprite.change_x = 0
        self.sprite.change_y = 0
        self.actualAnimationPath = IdleSidePath
        self.actualAnimationFrames = 5
        return self.handleMovementEvent(event)

    def LeftState(self, event):
        self.sprite.change_x = -Game.PLAYER_SPEED
        self.sprite.change_y = 0
        self.actualAnimationPath = RunSidePath
        self.actualAnimationFrames = 6
        self.sprite.scale_x = -abs(self.sprite.scale_x)
        return self.handleMovementEvent(event)

    def RightState(self, event):
        self.sprite.change_x = Game.PLAYER_SPEED
        self.sprite.change_y = 0
        self.actualAnimationPath = RunSidePath
        self.actualAnimationFrames = 6
        self.sprite.scale_x = abs(self.sprite.scale_x)
        return self.handleMovementEvent(event)

    def DownState(self, event):
        self.sprite.change_y = -Game.PLAYER_SPEED
        self.sprite.change_x = 0
        self.actualAnimationPath = RunFrontPath
        self.actualAnimationFrames = 6
        return self.handleMovementEvent(event)

    def UpState(self, event):
        self.sprite.change_y = Game.PLAYER_SPEED
        self.sprite.change_x = 0
        self.actualAnimationFrames = 6
        self.actualAnimationPath = RunBackPath
        return self.handleMovementEvent(event)

    def setup(self):
        """Función para configurar la maquina de estados del personaje"""
        self.addState(IDLE_FRONT, self.IdleFront)
        self.addState(IDLE_BACK, self.IdleBack)
        self.addState(IDLE_SIDE_LEFT, self.IdleSideLeft)
        self.addState(IDLE_SIDE_RIGHT, self.IdleSideRight)
        self.addState(LEFT, self.LeftState)
        self.addState(RIGHT, self.RightState)
        self.addState(DOWN, self.DownState)
        self.addState(UP, self.UpState)
        self.updateSpriteList()

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

        self.lastAnimationPath = self.actualAnimationPath
        print("cargando nuevas texturas ...\n")
        self.frames.clear()
        for i in range(
            AssetsUrls.INITIAL_INDEX,
            self.actualAnimationFrames + AssetsUrls.INITIAL_INDEX,
        ):
            route = self.actualAnimationPath.replace("{}", str(i))
            texture = None
            # Si el path de la textura ya estaba cargada no hay que cargarla de nuevo
            if route in self.spriteCache:
                # Dice que la texture a cargar es la que está en caché
                texture = self.spriteCache[route]
            else:
                # Si no está en caché, la carga y la guarda en caché
                texture = arcade.load_texture(route)
                self.spriteCache[route] = texture
            # Agrega la textura
            self.frames.append(texture)
        self.textureIndex = 0
        print("texturas cargadas !")

    def update_animation(self, deltaTime: float):
        """Función para actualizar la animación del personaje"""
        if not self.frames:
            return
        self.animationTimer += deltaTime
        if self.animationTimer > 0.1:
            self.animationTimer = 0
            self.textureIndex = (self.textureIndex + 1) % self.actualAnimationFrames
            self.sprite.texture = self.frames[self.textureIndex]

    def addToInventory(self, item: str, cant: int) -> None:
        if item not in self.inventory:
            self.inventory[item] = cant
        else:
            self.inventory[item] += cant
        print(self.inventory)
