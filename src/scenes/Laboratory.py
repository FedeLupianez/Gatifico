from typing import Callable
import arcade
from View import View
from characters.Player import Player
from src import Constants


class Laboratory(View):
    def __init__(self, callback: Callable, player: Player):
        backgroundUrl = ":resources:Background/Texture/TX Plant.png"
        super().__init__(background_url=backgroundUrl, tilemap_url=None)
        self.player = player
        self.player_sprites = arcade.SpriteList()
        self.callback = callback
        self.keys_pressed: set = set()
        self.window.set_mouse_visible(False)
        self.camera.zoom = Constants.Game.FOREST_ZOOM_CAMERA
        self.camera.position = self.player.sprite.position

        # Inicializacion de funciones
        self.setup_player()

    def setup_player(self):
        self.player.setup()
        self.player_sprites.append(self.player.sprite)

    def setup_layers(self):
        if not self.tilemap:
            raise ValueError("TileMap no cargado")
        self.background_layer = self.scene["Fondo"]
        self.collisions_layer = self.scene["Colisiones"]

    def check_collision(self):
        return arcade.check_for_collision_with_list(
            self.player.sprite, self.collisions_layer
        )

    def change_to_menu(self):
        self.callback(Constants.SignalCodes.CHANGE_VIEW, "TEST")

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        match symbol:
            case arcade.key.E:
                # return self.handleInteractions()
                return False
            case arcade.key.ESCAPE:
                self.callback(Constants.SignalCodes.PAUSE_GAME, self.change_to_menu)
                return True

        self.keys_pressed.add(symbol)
        return None

    def on_draw(self) -> None:
        self.clear()
        self.camera.use()
        self.scene.draw(pixelated=True)  # Dibuja la escena con el fondo y los objetos
        self.player_sprites.draw(pixelated=True)  # Dibuja el personaje

    def on_update(self, delta_time: float):
        self.player.update_animation(delta_time)
        for key in self.keys_pressed:
            # Actualica el estado del personaje según la tecla
            self.player.update_state(key)
        self.player.update_position()

        player = self.player.sprite
        last_position = player.center_x, player.center_y
        player_moved = (player.center_x != last_position[0]) or (
            player.center_y != last_position[1]
        )
        if player_moved:
            if self.check_collision():
                self.player.sprite.center_x, self.player.sprite.center_y = last_position

        cam_lerp = 0.25 if (player_moved) else 0.06
        self.camera.position = arcade.math.lerp_2d(
            self.camera.position, self.player.sprite.position, cam_lerp
        )
