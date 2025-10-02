from typing import Callable, Literal
import arcade
import math
import random
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
        self.hit_time = 1  # tiempo en segundos que dura la animación de daño
        self.actual_state: Literal["IDLE", "ATTACK", "RUN", "HURT"] = "IDLE"
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

        if self.actual_state == "HURT" and self.hit_time >= 0:
            return
        if self.distance_to_player > self.persecute_radius:
            self.actual_state = "IDLE"
        elif self.distance_to_player < self.attack_radius:
            self.actual_state = "ATTACK"
        else:
            self.actual_state = "RUN"

    def update(self, delta_time: float, player_position: tuple[float, float]):
        if self.actual_state == "HURT":
            self.hit_time -= delta_time
            self.color = arcade.color.RED

            # Aplicar fricción para detener el knockback gradualmente
            self.change_x *= 0.5
            self.change_y *= 0.5

            # Si la velocidad es muy baja, detenerla por completo
            if abs(self.change_x) < 0.1 and abs(self.change_y) < 0.1:
                self.change_x = 0
                self.change_y = 0

            if self.hit_time <= 0:
                self.hit_time = 1
                self.color = arcade.color.GREEN
                self.change_y = 0
                self.change_x = 0
                self.actual_state = "IDLE"

        elif self.actual_state == "ATTACK":
            self.attack_time -= delta_time
            if self.attack_time <= 0:
                self.attack()
                self.attack_time = self.attack_coldown
            self.change_x = 0
            self.change_y = 0

        elif self.actual_state == "RUN":
            diff_x = player_position[0] - self.center_x
            diff_y = player_position[1] - self.center_y
            if self.distance_to_player > 0:
                self.change_x = (diff_x / self.distance_to_player) * self.speed
                self.change_y = (diff_y / self.distance_to_player) * self.speed
            else:
                self.change_x = 0
                self.change_y = 0

        elif self.actual_state == "IDLE":
            self.change_x = 0
            self.change_y = 0

        self.center_x += self.change_x
        self.center_y += self.change_y
        self.update_chunk(self)
        self.process_state(player_position)

    def hurt(self, damage: int, knockback: int = 0):
        self.actual_state = "HURT"
        self.health -= damage
        if self.health <= 0:
            self.update_chunk(self, kill=True)
            self.remove_from_sprite_lists()
            self.drop_item(random_item(center_x=self.center_x, center_y=self.center_y))
            return
        # Enviar para atrás si tiene knockback
        if knockback > 0:
            knockback_speed = knockback * 2.5

            # Vector desde el jugador al enemigo
            dx = self.center_x - self.player.sprite.center_x
            dy = self.center_y - self.player.sprite.center_y
            dist = math.sqrt(dx**2 + dy**2)

            if dist > 0:
                # Aplicar velocidad de knockback
                self.change_x = (dx / dist) * knockback_speed
                self.change_y = (dy / dist) * knockback_speed
            else:
                # Si el jugador está justo encima, knockback en dirección aleatoria
                angle = random.uniform(0, 2 * math.pi)
                self.change_x = math.cos(angle) * knockback_speed
                self.change_y = math.sin(angle) * knockback_speed

    def attack(self) -> None:
        self.player.hurt(self.damage)

