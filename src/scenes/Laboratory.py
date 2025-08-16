from typing import Callable
import arcade
from scenes.View import View
from characters.Player import Player
import Constants
from scenes.Chest import Chest


class Laboratory(View):
    def __init__(self, callback: Callable, player: Player):
        backgroundUrl = None
        tileMapUrl = ":resources:Maps/Laboratory.tmx"
        super().__init__(background_url=backgroundUrl, tilemap_url=tileMapUrl)
        self.player = player
        self.player_sprites = arcade.SpriteList()
        self.callback = callback
        self.keys_pressed: list[int] = []
        self.window.set_mouse_visible(False)
        self.camera.zoom = Constants.Game.FOREST_ZOOM_CAMERA
        self.camera.position = self.player.sprite.position

        # constantes para precalcular las operacions para actualizar la camara
        self._screen_width = self.camera.viewport_width
        self._screen_height = self.camera.viewport_height
        self._half_w = (self._screen_width / self.camera.zoom) / 2
        self._half_h = (self._screen_height / self.camera.zoom) / 2

        self._map_width = self.tilemap.width * self.tilemap.tile_width
        self._map_height = self.tilemap.height * self.tilemap.tile_height

        # Inicializacion de funciones
        self.setup_player()
        self.setup_layers()

    def setup_player(self):
        self.player.setup()
        self.player_sprites.append(self.player.sprite)

    def setup_layers(self):
        if not self.tilemap:
            raise ValueError("TileMap no cargado")
        self.background_layer = self.scene["Fondo"]
        self.collisions_layer = self.scene["Colisiones"]
        self.collisions_layer.enable_spatial_hashing()
        self.interact_layer = self.load_object_layers("Interactuables", self.tilemap)
        self.interact_layer.enable_spatial_hashing()
        # Meto las listas de colisiones en otra lista para precomputar antes del
        # check de colisiones
        self.collisions_list = [self.collisions_layer, self.interact_layer]

    def check_collision(self) -> bool:
        player = self.player.sprite
        if arcade.check_for_collision_with_lists(player, self.collisions_list):
            return True
        return False

    def change_to_menu(self):
        self.callback(Constants.SignalCodes.CHANGE_VIEW, "TEST")

    def open_chest(self, chest_id: str):
        new_scene = Chest(
            chestId=chest_id,
            player=self.player,
            previusScene=self,
            background_image=self.get_screenshot(),
        )
        self.window.show_view(new_scene)

    def process_object_interaction(self, obj: arcade.Sprite) -> bool:
        obj_name: str = obj.name.lower()
        if obj_name == "door":
            self.callback(Constants.SignalCodes.PAUSE_GAME)
            return True
        if "chest" in obj_name:
            self.open_chest(chest_id=obj_name)
            return True

        return False

    def handle_interactions(self):
        closest_obj = arcade.get_closest_sprite(self.player.sprite, self.interact_layer)
        if closest_obj and closest_obj[1] <= 50:
            return self.process_object_interaction(closest_obj[0])

        del closest_obj

        return False

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        match symbol:
            case arcade.key.E:
                self.handle_interactions()
            case arcade.key.ESCAPE:
                self.callback(Constants.SignalCodes.PAUSE_GAME, self.change_to_menu)
                return True

        self.keys_pressed.append(symbol)
        return None

    def on_key_release(self, symbol: int, modifiers: int) -> bool | None:
        if symbol in self.keys_pressed:
            self.keys_pressed.remove(symbol)
        self.player.process_state(-symbol)

    def on_draw(self) -> None:
        self.clear()
        self.camera.use()
        self.scene.draw(pixelated=True)  # Dibuja la escena con el fondo y los objetos
        self.player_sprites.draw(pixelated=True)  # Dibuja el personaje

    def on_update(self, delta_time: float):
        self.player.update_animation(delta_time)
        player = self.player.sprite
        last_position = player.center_x, player.center_y

        if self.keys_pressed:
            self.player.process_state(self.keys_pressed[-1])
        self.player.update_position()

        player_moved = (player.center_x != last_position[0]) or (
            player.center_y != last_position[1]
        )
        if player_moved:
            if self.check_collision():
                self.player.sprite.center_x, self.player.sprite.center_y = last_position
        self.update_camera(player_moved)

    def update_camera(self, player_moved: bool) -> None:
        cam_lerp = 0.25 if (player_moved) else 0.06

        target_x = self.player.sprite.center_x
        target_y = self.player.sprite.center_y

        target_x = max(self._half_w, min(target_x, self._map_width - self._half_w))
        target_y = max(self._half_h, min(target_y, self._map_height - self._half_h))

        self.camera.position = arcade.math.lerp_2d(
            self.camera.position, (target_x, target_y), cam_lerp
        )
