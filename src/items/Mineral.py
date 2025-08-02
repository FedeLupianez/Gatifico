import arcade
from StateMachine import StateMachine
from .utils import create_white_texture

BIG_SIZE = "big"
MID_SIZE = "mid"
SMALL_SIZE = "small"

BIG_STATE = "BIG"
MID_STATE = "MID"
SMALL_STATE = "SMALL"
KILL_STATE = "KILL"


class Mineral(arcade.Sprite):
    def __init__(
        self,
        mineral: str,
        size_type: str,
        center_x: float,
        center_y: float,
        mineral_attr: dict,
    ):
        self.attributes: dict = mineral_attr
        super().__init__(
            path_or_texture=self.attributes[mineral][size_type]["path"],
            center_x=center_x,
            center_y=center_y,
        )

        initial_state = ""
        if size_type.lower() == BIG_SIZE:
            initial_state = BIG_STATE
        elif size_type.lower() == MID_SIZE:
            initial_state = MID_STATE
        else:
            initial_state = SMALL_STATE
        self.state_machine = StateMachine(initial_state)

        self.mineral = mineral
        self.size_type = size_type

        self.touches = self.attributes[mineral][size_type]["touches"]
        self.actual_touches = 0

        self.should_removed: bool = False
        self.is_flashing: bool = False
        self.flash_timer: float = 0.0
        self.original_texture = self.texture

    def handle_state(self, key: int, actual_state: str, next_state: str) -> str:
        """
        Función genérica para todos los estados
        Args:
            key (int) -> es la tecla presionada
            actual_state (str) -> es el estado que va a tomar la función como actual
            next_state (str) -> es el estado que va a tomar la función como siguiente
        """
        self.size_type = actual_state.lower()
        data = self.attributes[self.mineral][self.size_type]
        new_texture_path = data["path"]
        self.update_sprite(new_texture_path)
        if key != arcade.key.E:
            return self.state_machine.actual_state_id
        self.start_flashing()
        self.actual_touches += 1
        if self.actual_touches >= self.touches:
            self.actual_touches = 0
            return next_state
        return actual_state

    def big_size_state(self, key: int):
        return self.handle_state(key=key, actual_state=BIG_STATE, next_state=MID_STATE)

    def mid_size_state(self, key: int):
        return self.handle_state(
            key=key, actual_state=MID_STATE, next_state=SMALL_STATE
        )

    def small_size_state(self, key: int):
        return self.handle_state(
            key=key, actual_state=SMALL_STATE, next_state=KILL_STATE
        )

    def kill_state(self, key: int):
        # Indico que este mineral debe de ser removido de la lista
        self.should_removed = True

    def setup(self):
        self.state_machine.add_state(id=BIG_STATE, state=self.big_size_state)
        self.state_machine.add_state(id=MID_STATE, state=self.mid_size_state)
        self.state_machine.add_state(id=SMALL_STATE, state=self.small_size_state)
        self.state_machine.add_state(id=KILL_STATE, state=self.kill_state)

    def update_state(self, key: int):
        self.state_machine.process_state(key)

    def update_sprite(self, newPath: str):
        if not self.is_flashing:
            self.texture = arcade.load_texture(newPath)

    def start_flashing(self):
        """
        Inicia el efecto de parpadeo
        """
        if self.is_flashing:
            return

        self.original_texture = self.texture
        white_texture = create_white_texture(str(self.original_texture._file_path))
        if white_texture:
            self.white_texture = white_texture
            self.is_flashing = True
            self.texture = self.white_texture
            self.flash_timer = 0.3

    def update_flash(self, delta_time) -> None:
        """
        Actualiza el efecto de parpadeo
        """
        if self.is_flashing:
            self.flash_timer -= delta_time
            if self.flash_timer <= 0:
                self.texture = self.original_texture
                self.is_flashing = False
                self.flash_timer = 0.0
