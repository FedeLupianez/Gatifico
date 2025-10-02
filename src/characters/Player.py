import arcade
from Constants import AssetsConstants, PlayerConfig
from StateMachine import StateMachine
from DataManager import loadData, texture_manager, game_data, get_path
from typing import Literal
from time import time
from random import randint


class Player(StateMachine, PlayerConfig):
    """Clase player, esta es un singleton, por lo que si se instancia mas de una vez devuelve la
    misma instancia"""

    # Defino los id de los estados para no repetir magic strings
    IDLE_SIDE_LEFT = "IDLE_SIDE_LEFT"
    IDLE_SIDE_RIGHT = "IDLE_SIDE_RIGHT"
    IDLE_FRONT = "IDLE_FRONT"
    IDLE_BACK = "IDLE_BACK"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    UP = "UP"
    DOWN = "DOWN"
    ANIMATIONS_CONFIG: dict = loadData("PlayerAnimationsConfig.json")
    INITIAL_INDEX = AssetsConstants.INITIAL_INDEX
    _instace = None
    _initialized = False

    # Config para que solo haya una instancia del jugador
    def __new__(cls) -> "Player":
        if not cls._instace:
            cls._instace = super().__new__(cls)
        return cls._instace

    def __init__(self):
        if self._initialized:
            return
        super().__init__(Player.IDLE_FRONT)
        self.motions = [arcade.key.W, arcade.key.A, arcade.key.S, arcade.key.D]
        # Todos los path tienen llaves {} donde iría el numero de sprite
        self.actual_animation_path: str = Player.ANIMATIONS_CONFIG["IDLE_FRONT"][
            "path"
        ].replace("{}", str(Player.INITIAL_INDEX))
        self.sprite: arcade.Sprite = arcade.Sprite(
            self.actual_animation_path, scale=self.SCALE
        )  # objeto sprite del personaje

        self.speed = self.SPEED
        self.knockback = 15
        self.actual_animation_frames: int = Player.ANIMATIONS_CONFIG[Player.IDLE_FRONT][
            "frames"
        ]  # cantidad de frames de la animacion
        self.actual_animation_speed: float = Player.ANIMATIONS_CONFIG[
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
            cant_frames = Player.ANIMATIONS_CONFIG[state]["frames"]
            for i in range(
                Player.INITIAL_INDEX,
                cant_frames + Player.INITIAL_INDEX,
            ):
                self.animations[state].append(
                    self._load_texture(Player.ANIMATIONS_CONFIG[state]["path"], i)
                )

        self.texture_index = 0  # indice actual de la textura
        self.animation_timer: float = 0.0  # timer de la animación
        # Diccionario para el inventario
        self.inventory: dict[str, int] = {}
        self.max_inventory: int = 64
        # Monedas del jugador
        self.coins: int = 100
        self.chunk_key: tuple[int, int] = (0, 0)

        self.healt = 100
        self.lifes = 5
        self.lifes_sprite_list = arcade.SpriteList()

        self.actual_floor: Literal["grass", "wood"] = "grass"
        self.step_sounds: dict[Literal["grass", "wood"], list[arcade.Sound]] = {
            "grass": [
                arcade.Sound(get_path("Step_grass_1.mp3")),
                arcade.Sound(get_path("Step_grass_2.mp3")),
            ],
            "wood": [
                arcade.Sound(get_path("Step_wood_1.mp3")),
                arcade.Sound(get_path("Step_wood_2.mp3")),
            ],
        }
        # Tiempo del ultimo sonido de paso, con este sabemos
        # si se terminó de reproducir el sonido anterior
        self.last_step_sound_time: float = 0.0
        self.step_coldown = 0.5  # Tiempo entre sonido y sonido
        self.setup()
        self._initialized = True

    def genericStateHandler(self, event: int):
        """Función genérica para todos los estados del personaje, ya que casi todos hacen lo mismo"""
        # Cargo la configuración del estado actual
        config = Player.ANIMATIONS_CONFIG[self.actual_state_id]
        # Hago los cambios que tengan que ver con el sprite
        self.sprite.change_x = config["speed_x"]
        self.sprite.change_y = config["speed_y"]

        if config["flip_x"]:
            self.sprite.scale_x = -abs(self.sprite.scale_x)
        else:
            self.sprite.scale_x = abs(self.sprite.scale_x)

        frames = config["frames"]
        self.actual_animation_speed = config.get("animation_speed", 0.1)

        template_path = Player.ANIMATIONS_CONFIG[self.actual_state_id]["path"]
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

    def setup(
        self,
        position: tuple[int, int] | None = None,
    ):
        """Función para configurar la maquina de estados del personaje"""
        self.add_state(Player.IDLE_FRONT, self.genericStateHandler)
        self.add_state(Player.IDLE_BACK, self.genericStateHandler)
        self.add_state(Player.IDLE_SIDE_LEFT, self.genericStateHandler)
        self.add_state(Player.IDLE_SIDE_RIGHT, self.genericStateHandler)
        self.add_state(Player.LEFT, self.genericStateHandler)
        self.add_state(Player.RIGHT, self.genericStateHandler)
        self.add_state(Player.DOWN, self.genericStateHandler)
        self.add_state(Player.UP, self.genericStateHandler)
        print(game_data)
        antique_data = game_data["player"]
        self.sprite.center_x = (
            position[0] if position else antique_data["position"]["center_x"]
        )
        self.sprite.center_y = (
            position[1] if position else antique_data["position"]["center_y"]
        )
        self.inventory = antique_data["inventory"]
        self.update_spritelist()
        texture = texture_manager.load_or_get_texture(get_path("full_heart.png"))
        self.lifes_sprite_list.clear()
        for i in range(self.lifes):
            temp = arcade.Sprite(texture, scale=3)
            temp.center_x = 40 + ((temp.width + 10) * i)
            self.lifes_sprite_list.append(temp)
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
            self.process_state(-new_key)

    def update_position(self):
        """Actualiza la posición del personaje según la velocidad actual"""
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

    def play_step_sound(self) -> None:
        if "IDLE" in self.actual_state_id:
            return
        current_time = time()
        if not (current_time - self.last_step_sound_time > self.step_coldown):
            return
        volume = 1 if self.actual_floor == "grass" else 0.2
        self.step_sounds[self.actual_floor][randint(0, 1)].play(
            volume=volume, speed=1.2
        )
        self.last_step_sound_time = current_time

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
                self.play_step_sound()

    def add_to_inventory(self, item: str, cant: int) -> None:
        if item not in self.inventory:
            self.inventory[item] = cant
        else:
            if self.inventory[item] >= self.max_inventory:
                return
            self.inventory[item] += cant

    def get_inventory(self) -> dict[str, int]:
        return self.inventory

    def get_items(self) -> list[tuple[str, int]]:
        return list(self.inventory.items())

    def remove_from_inventory(self, item: str, cant: int) -> bool:
        if item not in self.inventory:
            return False
        self.inventory[item] -= cant
        if self.inventory[item] <= 0:
            self.inventory.pop(item)
        return True

    def pay(self, price: int):
        if (self.coins - price) < 0:
            raise ValueError("No hay suficiente dinero")
        self.coins -= price

    def add_coins(self, coins: int) -> None:
        self.coins += coins

    def attack(self, enemy):
        enemy.hurt(damage=10, knockback=self.knockback)

    def change_hearts(self) -> None:
        # Remuevo los corazones sobrantes
        diff = len(self.lifes_sprite_list) - self.lifes
        # Si la parte decimal de la vida es impar significa que debe tener medio corazón
        is_half_heart = (self.healt / 10) % 2 != 0
        texture_name = "empty_heart.png" if not is_half_heart else "mid_heart.png"
        texture = texture_manager.load_or_get_texture(get_path(texture_name))
        self.lifes_sprite_list[-diff].texture = texture

    def hurt(self, damage: int):
        self.healt -= damage
        if self.healt <= 0:
            self.healt = 0
        self.lifes = self.healt // 20
        self.change_hearts()
        if self.lifes <= 0:
            return True
        return False

    def throw_item(self, item: str):
        self.inventory.pop(item)
