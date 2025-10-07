from typing import Callable
import arcade
from characters.Player import Player
from utils import random_item
from StateMachine import StateMachine
from DataManager import get_path, texture_manager
from random import uniform


class Enemy(arcade.Sprite):
    WALK = "WALK"
    IDLE = "IDLE"
    ATTACK = "ATTACK"
    HURT = "HURT"
    _sprites: dict[str, list[arcade.Texture]] = {WALK: []}

    def __init__(
        self,
        center_x: float,
        center_y: float,
        callback_update_chunk: Callable,
        callback_drop_item: Callable,
    ) -> None:
        # Si el dict de clase no está cargado lo cargo
        if not self._sprites[self.WALK]:
            for i in range(3):
                texture = self._load_texture("sprite_secuaz_{}.png", i + 1)
                self._sprites[self.WALK].append(texture)
        self.custom_scale = uniform(0.7, 1.2)
        super().__init__(center_x=center_x, center_y=center_y, scale=self.custom_scale)
        self.texture = self._sprites[self.WALK][0]
        self.speed = 0.8
        self.health = 100
        self.damage = 10
        self.hurt_time = 1  # tiempo en segundos que dura la animación de daño

        self.animation_cooldown = 0.3
        self.animation_timer = 0
        self.frame_index = 0

        self.distance_to_player: float = 0
        self.persecute_radius = 140

        self.attack_radius = 35
        self.attack_coldown = 1.3
        self.attack_time = self.attack_coldown

        # Referencia al player
        self.player = Player()
        # Esta función se va a ejecutar cuando el enemy se quede quieto para actualizar su chunk_key
        self.update_chunk = callback_update_chunk
        self.drop_item = callback_drop_item
        self.chunk_key: tuple[int, int] = (0, 0)

        self.state_machine = StateMachine(self.IDLE)
        self.state_machine.add_state(self.IDLE, self.idle_state)
        self.state_machine.add_state(self.ATTACK, self.attack_state)
        self.state_machine.add_state(self.WALK, self.walk_state)
        self.state_machine.add_state(self.HURT, self.hurt_state)

    def _load_texture(self, path: str, index: int):
        route = path.replace("{}", str(index))
        return texture_manager.load_or_get_texture(get_path(route))

    def get_new_state(self) -> str:
        if self.distance_to_player > self.persecute_radius:
            return self.IDLE
        elif self.distance_to_player < self.attack_radius:
            return self.ATTACK
        else:
            return self.WALK

    def idle_state(self, event):
        if event == 0:  # on enter
            self.change_x = 0
            self.change_y = 0
            return
        self.texture = self._sprites[self.WALK][0]
        return self.get_new_state()

    def walk_state(self, event):
        if event == 0:  # on enter
            return
        *_, player_position = event
        diff_x = player_position[0] - self.center_x
        diff_y = player_position[1] - self.center_y
        self.scale_x = -self.custom_scale if diff_x > 0 else self.custom_scale

        if self.distance_to_player > 0:
            self.change_x = (diff_x / self.distance_to_player) * self.speed
            self.change_y = (diff_y / self.distance_to_player) * self.speed
        else:
            self.change_x = 0
            self.change_y = 0

        return self.get_new_state()

    def attack_state(self, event):
        if event == 0:  # on enter
            self.change_x = 0
            self.change_y = 0
            return
        delta_time, *_ = event
        self.attack_time -= delta_time
        if self.attack_time <= 0:
            self.attack()
            self.attack_time = self.attack_coldown
        return self.get_new_state()

    def hurt_state(self, event):
        if event == 0:  # on enter
            self.color = arcade.color.RED
            self.hurt_time = 1
            return
        self.texture = self._sprites[self.WALK][0]
        delta_time, *_ = event
        self.hurt_time -= delta_time

        self.change_x *= 0.5
        self.change_y *= 0.5

        # Si la velocidad e s muy baja lo dejo de mover
        if abs(self.change_x) < 0.1 and abs(self.change_y) < 0.1:
            self.change_x = 0
            self.change_y = 0

        # Si ya pasó el tiemp de hit lo vuelvo al estado IDLE
        if self.hurt_time <= 0:
            # Volver al color normal de la texture
            self.color = arcade.color.WHITE
            self.change_y = 0
            self.change_x = 0
            return self.IDLE

        return self.HURT

    def update(
        self,
        delta_time: float,
        player_position: tuple[float, float],
        objects_collisions: arcade.SpriteList,
    ):
        self.distance_to_player = (
            (player_position[0] - self.center_x) ** 2
            + (player_position[1] - self.center_y) ** 2
        ) ** 0.5

        self.state_machine.process_state((delta_time, player_position))

        self.update_position(objects=objects_collisions)
        self.update_chunk(self)
        self.update_animation(delta_time)

    def update_position(self, objects: arcade.SpriteList) -> None:
        last_position = self.position
        self.center_x += self.change_x
        self.center_y += self.change_y
        if self.collides_with_list(objects):
            self.position = last_position

    def update_animation(self, delta_time: float) -> None:
        if self.state_machine.actual_state_id in [self.HURT, self.IDLE]:
            return
        self.animation_timer += delta_time
        if self.animation_timer > self.animation_cooldown:
            self.animation_timer = 0
            new_index = (self.frame_index + 1) % len(self._sprites[self.WALK])
            new_texture = self._sprites[self.WALK][new_index]
            if self.texture != new_texture:
                self.frame_index = new_index
                self.texture = new_texture

    def hurt(self, damage: int, knockback: int = 0):
        self.health -= damage
        if self.health <= 0:
            self.update_chunk(self, kill=True)
            self.remove_from_sprite_lists()
            self.drop_item(random_item(center_x=self.center_x, center_y=self.center_y, quantity=1))
            return

        self.state_machine.set_state(self.HURT)
        if knockback < 0:
            return
            # Enviar para atrás si tiene knockback
        knockback_speed = knockback * 2.5

        dx = self.center_x - self.player.sprite.center_x
        dy = self.center_y - self.player.sprite.center_y
        dist = (dx**2 + dy**2) ** (1 / 2)

        if dist > 0:
            # Aplicar velocidad de knockback
            self.change_x = (dx / dist) * knockback_speed
            self.change_y = (dy / dist) * knockback_speed

    def attack(self) -> None:
        self.player.hurt(self.damage, enemy=self, knockback=10)
