import arcade
from StateMachine import StateMachine
from DataManager import texture_manager
from typing import Dict, Any
from DataManager import loadData


class Mineral(arcade.Sprite):
    BIG_SIZE = "big"
    MID_SIZE = "mid"
    SMALL_SIZE = "small"

    BIG_STATE = "BIG"
    MID_STATE = "MID"
    SMALL_STATE = "SMALL"
    KILL_STATE = "KILL"
    __slots__ = [
        "mineral",
        "size_type",
        "touches",
        "actual_touches",
        "is_flashing",
        "flash_timer",
        "original_texture",
        "white_texture",
        "should_removed",
        "state_machine",
    ]

    _resources: Dict[str, Any] = loadData("Minerals.json")

    def __init__(
        self,
        mineral: str,
        size_type: str,
        center_x: float,
        center_y: float,
    ):
        super().__init__(
            path_or_texture=Mineral._resources[mineral][size_type]["path"],
            center_x=center_x,
            center_y=center_y,
        )
        self.chunk_key: tuple[int, int] = (-1, -1)

        initial_state = ""
        if size_type.lower() == Mineral.BIG_SIZE:
            initial_state = Mineral.BIG_STATE
        elif size_type.lower() == Mineral.MID_SIZE:
            initial_state = Mineral.MID_STATE
        else:
            initial_state = Mineral.SMALL_STATE
        self.state_machine = StateMachine(initial_state)

        self.mineral = mineral
        self.size_type = size_type

        self.touches = Mineral._resources[mineral][size_type]["touches"]
        self.actual_touches = 0

        self.should_removed: bool = False
        self.original_texture = self.texture
        hitbox_half_x = self.width / 2
        hitbox_half_y = self.height / 2
        self.hit_box._points = (
            (-hitbox_half_x, -hitbox_half_y),
            (hitbox_half_x, -hitbox_half_y),
            (hitbox_half_x, hitbox_half_y),
            (-hitbox_half_x, hitbox_half_y),
        )

    def handle_state(self, key: int, actual_state: str, next_state: str) -> str:
        """
        Función genérica para todos los estados
        Args:
            key (int) -> es la tecla presionada
            actual_state (str) -> es el estado que va a tomar la función como actual
            next_state (str) -> es el estado que va a tomar la función como siguiente
        """
        self.size_type = actual_state.lower()
        data = Mineral._resources[self.mineral][self.size_type]
        new_texture_path = data["path"]
        self.update_sprite(new_texture_path)
        if key != arcade.key.E:
            return self.state_machine.actual_state_id
        self.actual_touches += 1
        if self.actual_touches >= self.touches:
            self.actual_touches = 0
            return next_state
        return actual_state

    def big_size_state(self, key: int):
        return self.handle_state(
            key=key, actual_state=Mineral.BIG_STATE, next_state=Mineral.MID_STATE
        )

    def mid_size_state(self, key: int):
        return self.handle_state(
            key=key, actual_state=Mineral.MID_STATE, next_state=Mineral.SMALL_STATE
        )

    def small_size_state(self, key: int):
        return self.handle_state(
            key=key, actual_state=Mineral.SMALL_STATE, next_state=Mineral.KILL_STATE
        )

    def kill_state(self, key: int):
        # Indico que este mineral debe de ser removido de la lista
        self.should_removed = True

    def setup(self):
        self.state_machine.add_state(id=Mineral.BIG_STATE, state=self.big_size_state)
        self.state_machine.add_state(id=Mineral.MID_STATE, state=self.mid_size_state)
        self.state_machine.add_state(
            id=Mineral.SMALL_STATE, state=self.small_size_state
        )
        self.state_machine.add_state(id=Mineral.KILL_STATE, state=self.kill_state)

    def update_state(self, key: int):
        self.state_machine.process_state(key)

    def update_sprite(self, newPath: str):
        self.texture = texture_manager.load_or_get_texture(newPath)
