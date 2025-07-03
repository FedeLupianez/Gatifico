from typing import Dict, Literal
import arcade
from Constants import Game, AssetsConstants
import Constants
from StateMachine import StateMachine
import DataManager

# Defino los id de los estados para no repetir magic strings
IDLE_SIDE_LEFT = "IDLE_SIDE_LEFT"
IDLE_SIDE_RIGHT = "IDLE_SIDE_RIGHT"
IDLE_FRONT = "IDLE_FRONT"
IDLE_BACK = "IDLE_BACK"
LEFT = "LEFT"
RIGHT = "RIGHT"
UP = "UP"
DOWN = "DOWN"


actionKeys = Literal["IDLE", "RUN", "WALK"]
directionKeys = Literal["FRONT", "SIDE", "BACK"]
TexturePaths: Dict[actionKeys, Dict[directionKeys, str]] = DataManager.loadData(
    "PlayerPaths.json"
)

ANIMATION_STATE_CONFIG: dict = DataManager.loadData("PlayerAnimationsConfig.json")


class Player(StateMachine):
    def __init__(self):
        super().__init__(IDLE_FRONT)
        self.motions = [arcade.key.W, arcade.key.A, arcade.key.S, arcade.key.D]
        # Todos los path tienen llaves {} donde iría el numero de sprite
        self.actualAnimationPath: str = TexturePaths["IDLE"]["FRONT"].replace(
            "{}",
            str(
                AssetsConstants.INITIAL_INDEX
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

    def genericStateHandler(self, event: int):
        """Función genérica para todos los estados del personaje, ya que casi todos hacen lo mismo"""
        # Cargo la configuración del estado actual
        config = ANIMATION_STATE_CONFIG[self.actualStateId]
        # Hago los cambios que tengan que ver con el sprite
        self.sprite.change_x = config["speed_x"]
        self.sprite.change_y = config["speed_y"]

        if config["flip_x"]:
            self.sprite.scale_x = -abs(self.sprite.scale_x)
        else:
            self.sprite.scale_x = abs(self.sprite.scale_x)

        action = config["action"]
        direction = config["direction"]
        frames = config["frames"]

        templatePath = TexturePaths[action][direction]
        if templatePath != self.actualAnimationPath:
            self.actualAnimationPath = templatePath
            self.actualAnimationFrames = frames
            self.updateSpriteList()
        newState = self.handleMovementEvent(event)
        return newState

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
                    return self.actualStateId

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

    def setup(self):
        """Función para configurar la maquina de estados del personaje"""
        self.addState(IDLE_FRONT, self.genericStateHandler)
        self.addState(IDLE_BACK, self.genericStateHandler)
        self.addState(IDLE_SIDE_LEFT, self.genericStateHandler)
        self.addState(IDLE_SIDE_RIGHT, self.genericStateHandler)
        self.addState(LEFT, self.genericStateHandler)
        self.addState(RIGHT, self.genericStateHandler)
        self.addState(DOWN, self.genericStateHandler)
        self.addState(UP, self.genericStateHandler)
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
        self.frames.clear()
        for i in range(
            AssetsConstants.INITIAL_INDEX,
            self.actualAnimationFrames + AssetsConstants.INITIAL_INDEX,
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

    def getInventory(self):
        return self.inventory
