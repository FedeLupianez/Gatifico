from typing import Callable, Literal
import arcade
from characters.Player import Player
from utils import random_item


class Enemy(arcade.SpriteSolidColor):
    def __init__(
        self,
        center_x: float,
        center_y: float,
        callback_update_chunk: Callable,
        callback_drop_item: Callable,
    ) -> None:
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
        self.actual_state: Literal["IDLE", "ATTACK", "RUN", "STUNED"] = "IDLE"
        self.distance_to_player: float = 0
        self.persecute_radius = 140

        self.attack_radius = 35
        self.attack_coldown = 0.8
        self.attack_time = self.attack_coldown

        # Referencia al player
        self.player = Player()
        # Esta función se va a ejecutar cuando el enemy se quede quieto para actualizar su chunk_key
        self.update_chunk = callback_update_chunk
        self.drop_item = callback_drop_item
        self.chunk_key: tuple[int, int] = (0, 0)

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
            self.color = arcade.color.RED
            if self.hit_time <= 0:
                self.is_hurt = False
                self.hit_time = 5
                self.color = arcade.color.GREEN

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
        self.update_chunk(self)

    def hurt(self, damage: int, knockback: int = 0):
        self.is_hurt = True
        self.health -= damage
        if self.health <= 0:
            self.update_chunk(self, kill=True)
            self.remove_from_sprite_lists()
            self.drop_item(random_item(center_x=self.center_x, center_y=self.center_y))
            return
        # Enviar para atrás si tiene knockback
        if not knockback > 0:
            return
        diff_x: int = int(self.player.sprite.center_x - self.center_x)
        diff_y: int = int(self.player.sprite.center_y - self.center_y)
        knockback *= 5
        result_x: int = 0
        result_y: int = 0
        if not (
            self.player.sprite.center_x >= self.left
            and self.player.sprite.center_x <= self.right
        ):
            result_x = (knockback) if diff_x < 0 else -(knockback)

        if not (
            self.player.sprite.center_y >= self.bottom
            and self.player.sprite.center_y <= self.top
        ):
            result_y = (knockback) if diff_y < 0 else -(knockback)
        self.center_x += result_x
        self.center_y += result_y

    def attack(self) -> None:
        self.player.hurt(self.damage)
