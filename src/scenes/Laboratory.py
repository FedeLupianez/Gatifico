from typing import Callable
import arcade
from items.Container import Container
from items.Item import Item
from scenes.View import View
from characters.Player import Player
import Constants
from scenes.Chest import Chest
from scenes.MixTable import MixTable
from scenes.SplitTable import SplitTable
from .utils import add_containers_to_list


class Laboratory(View):
    def __init__(self, callback: Callable, player: Player):
        tileMapUrl = ":resources:Maps/laboratorio/Laboratory.tmx"
        super().__init__(background_url=None, tilemap_url=tileMapUrl)
        self.player = player
        self.callback = callback
        self.keys_pressed: set[int] = set()
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
        self.last_inventory_hash = 0

        # Inicializacion de funciones
        self.setup_spritelists()
        self.setup_player()
        self.setup_layers()
        self.setup_inventory_containers()
        self.update_inventory_items(self.player.get_items())
        self.update_inventory_texts(self.player.get_items())

    def setup_spritelists(self):
        self.player_sprites = arcade.SpriteList()
        self.inventory_containers = arcade.SpriteList()
        self.inventory_items = arcade.SpriteList()
        self.inventory_texts: list[arcade.Text] = []

    def setup_player(self):
        self.player.setup()
        self.player.sprite.center_x = 321
        self.player.sprite.center_y = 60
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

    def setup_inventory_containers(self) -> None:
        """Agrego los contenedores a la lista del inventario"""
        CONTAINER_SIZE = 35
        ITEMS_INIT = Constants.PlayerConfig.PLAYER_INVENTORY_POSITION
        positions = [(ITEMS_INIT[0] + 50 * i, ITEMS_INIT[1]) for i in range(4)]
        add_containers_to_list(
            positions, self.inventory_containers, container_size=CONTAINER_SIZE
        )
        inventory_sprite = arcade.Sprite(":resources:UI/inventory_tools.png", scale=3)
        inventory_sprite.center_x = ITEMS_INIT[0] + 75
        inventory_sprite.center_y = ITEMS_INIT[1]
        self.inventory_containers.append(inventory_sprite)

    def update_inventory_items(self, player_items: list) -> None:
        self.inventory_items.clear()
        for index, (item, quantity) in enumerate(player_items):
            container: Container = self.inventory_containers[index]
            new_item = Item(name=item, quantity=quantity, scale=2)
            new_item.id = index
            new_item.change_container(container.id)
            new_item.change_position(container.center_x, container.center_y)
            self.inventory_items.append(new_item)

    def update_inventory_texts(self, player_items: list) -> None:
        self.inventory_texts.clear()
        for index, (item, quantity) in enumerate(player_items):
            container: Container = self.inventory_containers[index]
            new_text = arcade.Text(
                text=f"{item} x {quantity}",
                font_size=9,
                x=container.center_x,
                y=container.center_y - (container.height / 2 + 10),
                anchor_x="center",
                anchor_y="baseline",
            )
            self.inventory_texts.append(new_text)

    def update_inventory_view(self) -> None:
        current_hash = hash(tuple(sorted(self.player.inventory.items())))
        if self.last_inventory_hash == current_hash:
            player_items = self.player.get_items()
            self.update_inventory_items(player_items)
            self.update_inventory_texts(player_items)
        self.last_inventory_hash = current_hash

    def check_collision(self) -> bool:
        player = self.player.sprite
        if arcade.check_for_collision_with_lists(player, self.collisions_list):
            return True
        return False

    def open_chest(self, chest_id: str):
        new_scene = Chest(
            chestId=chest_id,
            player=self.player,
            previusScene=self,
        )
        self.window.show_view(new_scene)

    def open_table(self, table_id: str):
        new_scene: View | None = None
        if table_id == "split_table":
            new_scene = SplitTable(background_scene=self, player=self.player)
        elif table_id == "mix_table":
            new_scene = MixTable(background_scene=self, player=self.player)
        if new_scene:
            self.window.show_view(new_scene)

    def process_object_interaction(self, obj: arcade.Sprite) -> bool:
        obj_name: str = obj.name.lower()
        self.keys_pressed.clear()
        self.player.stop_state()
        if obj_name == "door":
            self.callback(Constants.SignalCodes.PAUSE_GAME)
            return True
        if "chest" in obj_name:
            self.open_chest(chest_id=obj_name)
            return True
        if "table" in obj_name:
            self.open_table(table_id=obj_name)
            return True

        return False

    def handle_interactions(self):
        closest_obj = arcade.get_closest_sprite(self.player.sprite, self.interact_layer)
        if closest_obj and closest_obj[1] <= 50:
            return self.process_object_interaction(closest_obj[0])

        del closest_obj

        return False

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.E:
            self.handle_interactions()

        if symbol == arcade.key.ESCAPE:
            # Si el jugador actualmente se está moviendo lo paro
            if self.keys_pressed:
                self.keys_pressed.clear()
                self.player.process_state(-next(iter(self.keys_pressed)))
            self.callback(Constants.SignalCodes.PAUSE_GAME)
            return True

        self.keys_pressed.add(symbol)
        self.update_inventory_view()
        return None

    def on_key_release(self, symbol: int, modifiers: int) -> bool | None:
        if symbol in self.keys_pressed:
            self.keys_pressed.discard(symbol)
        self.player.process_state(-symbol)

    def world_draw(self):
        self.camera.use()
        self.scene.draw(pixelated=True)  # Dibuja la escena con el fondo y los objetos
        self.player_sprites.draw(pixelated=True)  # Dibuja el personaje

    def gui_draw(self):
        self.gui_camera.use()
        self.inventory_containers.draw(pixelated=True)
        self.inventory_items.draw(pixelated=True)
        for text in self.inventory_texts:
            text.draw()

    def on_draw(self) -> None:
        self.clear()
        self.world_draw()
        self.gui_draw()

    def on_update(self, delta_time: float):
        self.player.update_animation(delta_time)
        player = self.player.sprite
        last_position = player.center_x, player.center_y

        for key in self.keys_pressed:
            self.player.process_state(key)
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

        # Le pongo el limite del mundo a la cámara
        target_x = max(self._half_w, min(target_x, self._map_width - self._half_w))
        target_y = max(self._half_h, min(target_y, self._map_height - self._half_h))

        self.camera.position = arcade.math.lerp_2d(
            self.camera.position, (target_x, target_y), cam_lerp
        )

    def clean_up(self) -> None:
        del self.player
        del self.camera
        del self.gui_camera
        del self.last_inventory_hash
        del self.keys_pressed
        del self.inventory_items
        del self.inventory_containers
        del self.inventory_texts
        del self.background_layer
        del self.collisions_layer
        del self.interact_layer
        del self.collisions_list

    def get_screenshot(self):
        self.clear()
        self.world_draw()
        return arcade.get_image()
