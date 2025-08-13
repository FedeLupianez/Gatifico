from typing import Dict, Literal
import arcade
from Constants import AssetsConstants, PlayerConfig
from StateMachine import StateMachine
from DataManager import loadData, texture_manager, game_data


actionKeys = Literal["IDLE", "RUN", "WALK"]
directionKeys = Literal["FRONT", "SIDE", "BACK"]
TexturePaths: Dict[actionKeys, Dict[directionKeys, str]] = loadData("PlayerPaths.json")


class Player(StateMachine):
    # Defino los id de los estados para no repetir magic strings
    IDLE_SIDE_LEFT = "IDLE_SIDE_LEFT"
    IDLE_SIDE_RIGHT = "IDLE_SIDE_RIGHT"
    IDLE_FRONT = "IDLE_FRONT"
    IDLE_BACK = "IDLE_BACK"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    UP = "UP"
    DOWN = "DOWN"
    ANIMATION_STATE_CONFIG: dict = loadData("PlayerAnimationsConfig.json")
    INITIAL_INDEX = AssetsConstants.INITIAL_INDEX
    SCALE = PlayerConfig.CHARACTER_SCALE
    SPEED = PlayerConfig.PLAYER_SPEED

    def __init__(self):
        super().__init__(Player.IDLE_FRONT)
        self.motions = [arcade.key.W, arcade.key.A, arcade.key.S, arcade.key.D]
        # Todos los path tienen llaves {} donde iría el numero de sprite
        self.actual_animation_path: str = TexturePaths["IDLE"]["FRONT"].replace(
            "{}",
            str(
                Player.INITIAL_INDEX
            ),  # como es el sprite inicial lo intercambiamos por el indice inicial
        )
        self.sprite: arcade.Sprite = arcade.Sprite(
            self.actual_animation_path, scale=Player.SCALE
        )  # objeto sprite del personaje

        self.speed = Player.SPEED
        self.actual_animation_frames: int = 4  # cantidad de frames de la animacion
        self.frames: list[arcade.Texture] = []  # lista de texturas
        self.texture_index = 0  # indice actual de la textura
        self.animation_timer: float = 0.0  # timer de la animacion
        self.actual_animation_speed: float = 0.1
        # Diccionario para el inventario
        self.inventory: dict[str, int] = {}
        self.animation_cache: dict[str, list[arcade.Texture]] = {}

    def genericStateHandler(self, event: int):
        """Función genérica para todos los estados del personaje, ya que casi todos hacen lo mismo"""
        # Cargo la configuración del estado actual
        config = Player.ANIMATION_STATE_CONFIG[self.actual_state_id]
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
        self.actual_animation_speed = config.get("animation_speed", 0.1)

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
                    return Player.IDLE_BACK
                case arcade.key.S:
                    return Player.IDLE_FRONT
                case arcade.key.A:
                    return Player.IDLE_SIDE_LEFT
                case arcade.key.D:
                    return Player.IDLE_SIDE_RIGHT
                case _:
                    return self.actual_state_id

        # Si es que presionó una tecla, se cambia al estado correspondiente
        match key:
            case arcade.key.W:
                return Player.UP
            case arcade.key.A:
                return Player.LEFT
            case arcade.key.S:
                return Player.DOWN
            case arcade.key.D:
                return Player.RIGHT
            case _:
                # Si no es ninguna de las otras teclas retorna el estado actual
                return self.actual_state_id

    def setup(self):
        """Función para configurar la maquina de estados del personaje"""
        self.add_state(Player.IDLE_FRONT, self.genericStateHandler)
        self.add_state(Player.IDLE_BACK, self.genericStateHandler)
        self.add_state(Player.IDLE_SIDE_LEFT, self.genericStateHandler)
        self.add_state(Player.IDLE_SIDE_RIGHT, self.genericStateHandler)
        self.add_state(Player.LEFT, self.genericStateHandler)
        self.add_state(Player.RIGHT, self.genericStateHandler)
        self.add_state(Player.DOWN, self.genericStateHandler)
        self.add_state(Player.UP, self.genericStateHandler)
        antique_data = game_data["player"]
        self.sprite.center_x = antique_data["position"]["center_x"]
        self.sprite.center_y = antique_data["position"]["center_y"]
        self.inventory = antique_data["inventory"]
        self.update_spritelist()
        del antique_data

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
        if self.actual_animation_path in self.animation_cache:
            self.frames = self.animation_cache[self.actual_animation_path]
            self.texture_index = 0
            return
        self.frames.clear()

        def load_texture(path: str, index: int):
            route = path.replace("{}", str(index))
            return texture_manager.load_or_get_texture(route)

        load_textures = (
            load_texture(self.actual_animation_path, i)
            for i in range(
                Player.INITIAL_INDEX,
                self.actual_animation_frames + Player.INITIAL_INDEX,
            )
        )
        self.frames = list(load_textures)
        self.texture_index = 0

    def update_animation(self, deltaTime: float):
        """Función para actualizar la animación del personaje"""
        self.animation_timer += deltaTime
        if self.animation_timer > self.actual_animation_speed:
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
