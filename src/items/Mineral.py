import arcade
from StateMachine import StateMachine

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

    def big_size_state(self, key: int):
        self.size_type = BIG_SIZE
        data = self.attributes[self.mineral][BIG_SIZE]
        new_texture_path = data["path"]
        self.update_sprite(new_texture_path)
        if key != arcade.key.E:
            return self.state_machine.actual_state_id

        self.actual_touches += 1
        if self.actual_touches >= self.touches:
            self.actual_touches = 0
            return MID_STATE
        return BIG_STATE

    def mid_size_state(self, key: int):
        self.size_type = MID_SIZE
        data = self.attributes[self.mineral][MID_SIZE]
        new_texture_path = data["path"]
        self.touches = data["touches"]
        self.update_sprite(new_texture_path)

        if key != arcade.key.E:
            return self.state_machine.actual_state_id
        self.actual_touches += 1

        if self.actual_touches >= self.touches:
            self.actual_touches = 0
            return SMALL_STATE
        return MID_STATE

    def small_size_state(self, key: int):
        self.size_type = SMALL_SIZE
        data = self.attributes[self.mineral][SMALL_SIZE]
        new_texture_path = data["path"]
        self.touches = data["touches"]
        self.update_sprite(new_texture_path)

        if key != arcade.key.E:
            return self.state_machine.actual_state_id
        self.actual_touches += 1

        if self.actual_touches >= self.touches:
            self.actual_touches = 0
            return KILL_STATE
        return SMALL_STATE

    def kill_state(self, key: int):
        self.should_removed = True

    def setup(self):
        self.state_machine.add_state(BIG_STATE, self.big_size_state)
        self.state_machine.add_state(MID_STATE, self.mid_size_state)
        self.state_machine.add_state(SMALL_STATE, self.small_size_state)
        self.state_machine.add_state(KILL_STATE, self.kill_state)

    def update_state(self, key: int):
        self.state_machine.process_state(key)

    def update_sprite(self, newPath: str):
        self.texture = arcade.load_texture(newPath)
