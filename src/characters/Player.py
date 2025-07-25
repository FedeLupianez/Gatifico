from typing import Dict, Literal
import arcade
from Constants import AssetsConstants, PlayerConfig
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
        self.actual_animation_path: str = TexturePaths["IDLE"]["FRONT"].replace(
            "{}",
            str(
                AssetsConstants.INITIAL_INDEX
            ),  # como es el sprite inicial lo intercambiamos por el indice inicial
        )
        self.sprite: arcade.Sprite = arcade.Sprite(
            self.actual_animation_path, scale=PlayerConfig.CHARACTER_SCALE
        )  # objeto sprite del personaje

        # Coordenadas de un cuadrado de 40x40 centrado en (0,0)
        hit_box = [
            (-10, -10),
            (10, -10),
            (10, 10),
            (-10, 10)
        ]
        hit_box = [(x * PlayerConfig.CHARACTER_SCALE, y * PlayerConfig.CHARACTER_SCALE) for x, y in hit_box]

        self.sprite._points = hit_box
        self.speed = PlayerConfig.PLAYER_SPEED
        self.actual_animation_frames: int = 4  # cantidad de frames de la animacion
        self.frames: list[arcade.Texture] = []  # lista de texturas
        self.texture_index = 0  # indice actual de la textura
        self.animation_timer: float = 0.0  # timer de la animacion
        self.sprite_cache: dict[
            str, arcade.Texture
        ] = {}  # Diccionario con las texturas cargadas para ahorrar llamdas a memoria
        # Diccionario para el inventario
        self.inventory: dict[str, int] = {}

    def genericStateHandler(self, event: int):
        """Función genérica para todos los estados del personaje, ya que casi todos hacen lo mismo"""
        # Cargo la configuración del estado actual
        config = ANIMATION_STATE_CONFIG[self.actual_state_id]
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
        if templatePath != self.actual_animation_path:
            self.actual_animation_path = templatePath
            self.actual_animation_frames = frames
            self.update_spritelist()
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
                    return self.actual_state_id

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
                return self.actual_state_id

    def setup(self):
        """Función para configurar la maquina de estados del personaje"""
        self.add_state(IDLE_FRONT, self.genericStateHandler)
        self.add_state(IDLE_BACK, self.genericStateHandler)
        self.add_state(IDLE_SIDE_LEFT, self.genericStateHandler)
        self.add_state(IDLE_SIDE_RIGHT, self.genericStateHandler)
        self.add_state(LEFT, self.genericStateHandler)
        self.add_state(RIGHT, self.genericStateHandler)
        self.add_state(DOWN, self.genericStateHandler)
        self.add_state(UP, self.genericStateHandler)
        self.update_spritelist()

    def update_position(self):
        """Actualiza la posición del personaje segun la velocidad actual"""
        self.sprite.center_x += self.sprite.change_x
        self.sprite.center_y += self.sprite.change_y

    def update_state(self, event: int):
        """Actualiza el estado actual del personaje"""
        self.process_state(event)  # Procesa el estado

    def update_spritelist(self):
        """
        Actualiza la lista de texturas segun el estado actual
        """

        self.last_animation_path = self.actual_animation_path
        self.frames.clear()
        for i in range(
            AssetsConstants.INITIAL_INDEX,
            self.actual_animation_frames + AssetsConstants.INITIAL_INDEX,
        ):
            route = self.actual_animation_path.replace("{}", str(i))
            texture = None
            # Si el path de la textura ya estaba cargada no hay que cargarla de nuevo
            if route in self.sprite_cache:
                # Dice que la texture a cargar es la que está en caché
                texture = self.sprite_cache[route]
            else:
                # Si no está en caché, la carga y la guarda en caché
                texture = arcade.load_texture(route)
                self.sprite_cache[route] = texture
            # Agrega la textura
            self.frames.append(texture)
        self.texture_index = 0

    def update_animation(self, deltaTime: float):
        """Función para actualizar la animación del personaje"""
        self.animation_timer += deltaTime
        if self.animation_timer > 0.1:
            self.animation_timer = 0
            self.texture_index = (self.texture_index + 1) % self.actual_animation_frames
            self.sprite.texture = self.frames[self.texture_index]

    def add_to_inventory(self, item: str, cant: int) -> None:
        if item not in self.inventory:
            self.inventory[item] = cant
        else:
            self.inventory[item] += cant

    def get_inventory(self):
        return self.inventory
