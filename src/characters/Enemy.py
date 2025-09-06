import arcade


class Enemy(arcade.SpriteSolidColor):
    def __init__(self, center_x: float, center_y: float) -> None:
        super().__init__(
            color=arcade.color.GREEN,
            width=50,
            height=50,
            center_x=center_x,
            center_y=center_y,
        )
        self.is_hurt: bool = False
        self.hit_time = 1  # tiempo en segundos que dura la animación de daño

    def update(self, delta_time: float):
        if not self.is_hurt:
            self.color = arcade.color.GREEN
            return

        self.color = arcade.color.RED
        self.hit_time -= delta_time
        if self.hit_time <= 0:
            self.is_hurt = False
            self.hit_time = 5

    def hurt(self):
        self.is_hurt = True
