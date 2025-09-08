import arcade
from Constants import AssetsConstants, PlayerConfig
from StateMachine import StateMachine
from DataManager import loadData, texture_manager, game_data
from characters.Enemy import Enemy


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
    HITBOX_WIDTH = 27
    HITBOX_HEIGHT = 30

    def __init__(self):
        super().__init__(Player.IDLE_FRONT)
        self.motions = [arcade.key.W, arcade.key.A, arcade.key.S, arcade.key.D]
        # Todos los path tienen llaves {} donde iría el numero de sprite
        self.actual_animation_path: str = Player.ANIMATION_STATE_CONFIG["IDLE_FRONT"][
            "path"
        ].replace("{}", str(Player.INITIAL_INDEX))
        self.sprite: arcade.Sprite = arcade.Sprite(
            self.actual_animation_path, scale=Player.SCALE
        )  # objeto sprite del personaje

        self.speed = Player.SPEED
        self.actual_animation_frames: int = Player.ANIMATION_STATE_CONFIG[
            Player.IDLE_FRONT
        ]["frames"]  # cantidad de frames de la animacion
        self.actual_animation_speed: float = Player.ANIMATION_STATE_CONFIG[
            Player.IDLE_FRONT
        ]["animation_speed"]
        self.frames: list[arcade.Texture] = []  # lista de texturas actual
        # Acomodo la hitbox para que sea cuadrada
        self.sprite.hit_box._points = (
            (-self.HITBOX_WIDTH, -self.HITBOX_HEIGHT),
            (self.HITBOX_WIDTH, -self.HITBOX_HEIGHT),
            (self.HITBOX_WIDTH, self.HITBOX_HEIGHT),
            (-self.HITBOX_WIDTH, self.HITBOX_HEIGHT),
        )
        self.animations: dict[str, list[arcade.Texture]] = {
            Player.IDLE_SIDE_LEFT: [],
            Player.IDLE_SIDE_RIGHT: [],
            Player.IDLE_FRONT: [],
            Player.IDLE_BACK: [],
            Player.LEFT: [],
            Player.RIGHT: [],
            Player.UP: [],
            Player.DOWN: [],
        }

        # Cargo las texturas en el diccionario
        for state in self.animations:
            cant_frames = Player.ANIMATION_STATE_CONFIG[state]["frames"]
            for i in range(
                Player.INITIAL_INDEX,
                cant_frames + Player.INITIAL_INDEX,
            ):
                self.animations[state].append(
                    self._load_texture(Player.ANIMATION_STATE_CONFIG[state]["path"], i)
                )

        self.texture_index = 0  # indice actual de la textura
        self.animation_timer: float = 0.0  # timer de la animacion
        # Diccionario para el inventario
        self.inventory: dict[str, int] = {}
        self.max_inventory: int = 64
        self.coins: int = 0

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

        frames = config["frames"]
        self.actual_animation_speed = config.get("animation_speed", 0.1)

        template_path = Player.ANIMATION_STATE_CONFIG[self.actual_state_id]["path"]
        if template_path != self.actual_animation_path:
            self.actual_animation_path = template_path
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
                case arcade.key.W | arcade.key.UP:
                    return Player.IDLE_BACK
                case arcade.key.S | arcade.key.DOWN:
                    return Player.IDLE_FRONT
                case arcade.key.A | arcade.key.LEFT:
                    return Player.IDLE_SIDE_LEFT
                case arcade.key.D | arcade.key.RIGHT:
                    return Player.IDLE_SIDE_RIGHT
                case _:
                    return self.actual_state_id

        # Si es que presionó una tecla, se cambia al estado correspondiente
        match key:
            case arcade.key.W | arcade.key.UP:
                return Player.UP
            case arcade.key.A | arcade.key.LEFT:
                return Player.LEFT
            case arcade.key.S | arcade.key.DOWN:
                return Player.DOWN
            case arcade.key.D | arcade.key.RIGHT:
                return Player.RIGHT
            case _:
                # Si no es ninguna de las otras teclas retorna el estado actual
                return self.actual_state_id

    def setup(self, position: tuple[int, int] | None = None):
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
        self.sprite.center_x = (
            position[0] if position else antique_data["position"]["center_x"]
        )
        self.sprite.center_y = (
            position[1] if position else antique_data["position"]["center_y"]
        )
        self.inventory = antique_data["inventory"]
        self.update_spritelist()
        del antique_data

    def stop_state(self) -> None:
        states_keys = {
            Player.LEFT: arcade.key.A,
            Player.RIGHT: arcade.key.D,
            Player.DOWN: arcade.key.S,
            Player.UP: arcade.key.W,
        }
        new_key = states_keys.get(self.actual_state_id, None)
        if new_key:
            self.process_state(new_key)

    def update_position(self):
        """Actualiza la posición del personaje segun la velocidad actual"""
        self.sprite.center_x += self.sprite.change_x
        self.sprite.center_y += self.sprite.change_y

    def _load_texture(self, path: str, index: int):
        route = path.replace("{}", str(index))
        return texture_manager.load_or_get_texture(route)

    def update_spritelist(self):
        """
        Actualiza la lista de texturas segun el estado actual
        """
        self.frames = self.animations[self.actual_state_id]
        self.texture_index = 0

    def update_animation(self, deltaTime: float):
        """Función para actualizar la animación del personaje"""
        self.animation_timer += deltaTime
        if self.animation_timer > self.actual_animation_speed:
            self.animation_timer = 0
            new_index = (self.texture_index + 1) % self.actual_animation_frames
            new_texture = self.frames[new_index]
            if self.sprite.texture != new_texture:
                self.texture_index = new_index
                self.sprite.texture = new_texture

    def add_to_inventory(self, item: str, cant: int) -> None:
        if item not in self.inventory:
            self.inventory[item] = cant
        else:
            if self.inventory[item] >= self.max_inventory:
                return
            self.inventory[item] += cant

    def get_inventory(self):
        return self.inventory

    def get_items(self) -> list[tuple[str, int]]:
        return list(self.inventory.items())

    def pay(self, price: int):
        if (self.coins - price) < 0:
            raise ValueError("No hay suficiente dinero")
        self.coins -= price

    def attack(self, enemy: Enemy):
        print(f"atacando a {enemy}")
        enemy.hurt(damage=10)
