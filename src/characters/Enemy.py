from typing import Literal
import arcade
from characters.Player import Player


class Enemy(arcade.SpriteSolidColor):
    def __init__(self, center_x: float, center_y: float) -> None:
        super().__init__(
            color=arcade.color.GREEN,
            width=25,
            height=25,
            center_x=center_x,
            center_y=center_y,
        )
        self.speed = 0.8
        self.health = 100
        self.damage = 10
        self.is_hurt = False
        self.hit_time = 1  # tiempo en segundos que dura la animación de daño
        self.actual_state: Literal["IDLE", "ATTACK", "RUN"] = "IDLE"
        self.distance_to_player: float = 0
        self.persecute_radius = 140

        self.attack_radius = 35
        self.attack_coldown = 0.8
        self.attack_time = self.attack_coldown

        # Referencia al player
        self.player = Player()

    def process_state(self, player_position: tuple[float, float]) -> None:
        self.distance_to_player = (
            (player_position[0] - self.center_x) ** 2
            + (player_position[1] - self.center_y) ** 2
        ) ** 0.5

        if self.distance_to_player > self.persecute_radius:
            self.actual_state = "IDLE"
        elif self.distance_to_player < self.attack_radius:
            self.actual_state = "ATTACK"
        else:
            self.actual_state = "RUN"

    def update(self, delta_time: float, player_position: tuple[float, float]):
        self.process_state(player_position)
        if self.is_hurt:
            self.hit_time -= delta_time
            if self.hit_time <= 0:
                self.is_hurt = False
                self.hit_time = 5

        if self.actual_state == "ATTACK":
            self.attack_time -= delta_time
            if self.attack_time <= 0:
                self.attack()
                self.attack_time = self.attack_coldown

        if self.actual_state == "RUN":
            diff_x = player_position[0] - self.center_x
            diff_y = player_position[1] - self.center_y
            self.center_x += (diff_x / self.distance_to_player) * self.speed
            self.center_y += (diff_y / self.distance_to_player) * self.speed

        self.color = arcade.color.RED if self.is_hurt else arcade.color.GREEN

    def hurt(self, damage: int):
        self.is_hurt = True
        self.health -= damage

    def attack(self) -> None:
        self.player.hurt(self.damage)
