import arcade
from Constants import Game, AssetsUrls
from StateMachine import StateMachine


IdlePath = "src/assets/2D Pixel Dungeon Asset Pack/Character_animation/monsters_idle/skeleton2/v2/skeleton2_v2_{}.png"
MovementPath = "src/assets/Enemy_Animations_Set/enemies-vampire_movement.png"

# Defino los id de los estados para no repetir magic strings
IDLE = "IDLE"
LEFT = "LEFT"
RIGHT = "RIGHT"
UP = "UP"
DOWN = "DOWN"


class Player(StateMachine):
    def __init__(self):
        super().__init__()
        self.motions = [arcade.key.W, arcade.key.A, arcade.key.S, arcade.key.D]
        # Todos los path tienen llaves {} donde iría el numero de sprite
        self.actualAnimationPath: str = IdlePath.replace(
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
        self.sprite.scale = 5
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
            return IDLE
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
    def IdleState(self, event):
        self.sprite.change_x = 0
        self.sprite.change_y = 0
        self.actualAnimationPath = IdlePath
        self.actualAnimationFrames = 4
        return self.handleMovementEvent(event)

    def LeftState(self, event):
        self.sprite.change_x = -Game.PLAYER_SPEED
        self.sprite.change_y = 0
        self.actualAnimationPath = IdlePath
        self.actualAnimationFrames = 4
        self.sprite.scale_x = -abs(self.sprite.scale_x)
        return self.handleMovementEvent(event)

    def RightState(self, event):
        self.sprite.change_x = Game.PLAYER_SPEED
        self.sprite.change_y = 0
        self.actualAnimationPath = IdlePath
        self.actualAnimationFrames = 4
        self.sprite.scale_x = abs(self.sprite.scale_x)
        return self.handleMovementEvent(event)

    def DownState(self, event):
        self.sprite.change_y = -Game.PLAYER_SPEED
        self.sprite.change_x = 0
        self.actualAnimationPath = IdlePath
        self.actualAnimationFrames = 4
        return self.handleMovementEvent(event)

    def UpState(self, event):
        self.sprite.change_y = Game.PLAYER_SPEED
        self.sprite.change_x = 0
        self.actualAnimationPath = IdlePath
        return self.handleMovementEvent(event)

    def setup(self):
        """Función para configurar la maquina de estados del personaje"""
        self.addState(IDLE, self.IdleState)
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
        if not self.frames:
            return
        self.animationTimer += deltaTime
        if self.animationTimer > 0.1:
            self.animationTimer = 0
            self.textureIndex = (self.textureIndex + 1) % self.actualAnimationFrames
            self.updateFrame()
