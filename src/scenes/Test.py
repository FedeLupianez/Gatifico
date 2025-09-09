import arcade
from typing import Dict, Any, Callable

from characters.Enemy import Enemy
from scenes.View import View, Object
import Constants
from characters.Player import Player
from items.Mineral import Mineral
import DataManager
from items.Item import Item
from .utils import add_containers_to_list
from .Chest import Chest
from dataclasses import dataclass, field
from time import time

import random
from functools import lru_cache


@dataclass
class Chunk:
    sprites: Dict[str, list] = field(
        default_factory=lambda: {
            "mineral": [],
            "interact": [],
            "floor": [],
            "trees": [],
            "copes": [],
            "objects": [],
        }
    )
    is_loaded: bool = False
    last_accessed: float = field(default_factory=time)


class Chunk_Manager:
    def __init__(self, chunk_size_x: int, chunk_size_y: int) -> None:
        self.chunk_size_x = chunk_size_x
        self.chunk_size_y = chunk_size_y
        self.chunks: Dict[tuple[int, int], Chunk] = {}
        self.max_loaded_chunks = 15

    @lru_cache(maxsize=100)
    def get_chunk_key(self, x: float, y: float) -> tuple[int, int]:
        return (int(x // self.chunk_size_x), int(y // self.chunk_size_y))

    def get_chunk(self, key: tuple[int, int]) -> Chunk:
        if key not in self.chunks:
            self.chunks[key] = Chunk()
        chunk = self.chunks[key]
        chunk.last_accessed = time()
        return chunk

    def get_nearby_chunks(self, center_key: tuple[int, int]):
        col, row = center_key
        return [
            (col + dx, row + dy)
            for dx in range(-1, 2)
            for dy in range(-1, 2)
            if (col + dx, row + dy) in self.chunks
        ]


class Test(View):
    def __init__(self, callback: Callable, player: Player) -> None:
        tileMapUrl = ":resources:Maps/Tests.tmx"
        super().__init__(background_url=None, tilemap_url=tileMapUrl)
        self.window.set_mouse_visible(False)
        self.chunk_manager = Chunk_Manager(
            int(self.camera.viewport.width // 7), int(self.camera.viewport.height // 7)
        )

        self.callback = callback

        self.player = player  # Defino el personaje
        self.enemies: list[Enemy] = [Enemy(500, 500)]

        self.keys_pressed: set = set()
        # Flag para actualizaciones selectivas del inventario
        self.inventory_dirty = True
        # Hash para detectar cambios en el inventario
        self.last_inventory_hash = None

        self.areas: dict[tuple, dict[str, list]] = {}
        self._actual_area: dict[str, arcade.SpriteList] = {
            "collisions": arcade.SpriteList(use_spatial_hash=True, lazy=True),
            "interact": arcade.SpriteList(use_spatial_hash=True, lazy=True),
            "mineral": arcade.SpriteList(use_spatial_hash=True, lazy=True),
            "floor": arcade.SpriteList(use_spatial_hash=True, lazy=True),
            "trees": arcade.SpriteList(use_spatial_hash=True, lazy=True),
            "copes": arcade.SpriteList(use_spatial_hash=True, lazy=True),
            "objects": arcade.SpriteList(use_spatial_hash=True, lazy=True),
        }
        self.last_area_key = None
        self._cached_keys = []
        self._view_hitboxes: bool = False
        self._setup_scene()

    def _setup_scene(self) -> None:
        """Configuración principal"""
        self.setup_spritelists()
        self.setup_scene_layer()
        self.setup_player()
        self.update_inventory_sprites()
        self.update_inventory_texts()
        self.assign_tilemap_chunks()
        self.update_actual_chunk()

    def setup_spritelists(self):
        # Listas de Sprites
        self.characters_sprites: arcade.SpriteList = arcade.SpriteList()
        self.inventory_sprites: arcade.SpriteList = arcade.SpriteList()
        self.items_inventory: arcade.SpriteList = arcade.SpriteList()
        self.inventory_texts: list[arcade.Text] = []
        self.setup_inventory_containers()

    def setup_inventory_containers(self) -> None:
        """Agrego los contenedores a la lista del inventario"""
        CONTAINER_SIZE = 35
        ITEMS_INIT = Constants.PlayerConfig.PLAYER_INVENTORY_POSITION
        positions = [(ITEMS_INIT[0] + 50 * i, ITEMS_INIT[1]) for i in range(4)]
        add_containers_to_list(
            positions, self.inventory_sprites, container_size=CONTAINER_SIZE
        )
        inventory_sprite = arcade.Sprite(":resources:UI/inventory_tools.png", scale=3)
        inventory_sprite.center_x = ITEMS_INIT[0] + 75
        inventory_sprite.center_y = ITEMS_INIT[1]
        self.inventory_sprites.append(inventory_sprite)

    def setup_player(self) -> None:
        player_data = DataManager.game_data["player"]
        self.player.inventory = player_data["inventory"]
        self.player.setup((900, 600))
        self.characters_sprites.append(self.player.sprite)
        self.characters_sprites.append(self.enemies[0])
        # Camara para seguir al jugador :
        self.camera.zoom = Constants.Game.FOREST_ZOOM_CAMERA
        self.camera.position = self.player.sprite.position
        del player_data

    def setup_scene_layer(self) -> None:
        if not self.tilemap:
            raise ValueError("TileMap no puede set None")

        # Capas de vista :
        self.floor = self.scene["Floor"]
        self.walls = self.scene["Paredes"]
        self.background_objects = self.scene["Objects"]
        # Capas de colisiones :
        self.collision_objects = self.load_object_layers("Colisiones", self.tilemap)
        self.interact_objects = self.load_object_layers("Interactuables", self.tilemap)
        self.batch_assign_sprites(self.interact_objects, "interact")
        self.load_mineral_layer()
        # Variable para precomputar las listas de colisiones
        self._collision_list = arcade.SpriteList()

    def assign_sprite_chunk(self, sprite: arcade.Sprite, sprite_type: str):
        chunk_key = self.chunk_manager.get_chunk_key(sprite.center_x, sprite.center_y)
        if hasattr(sprite, "chunk_key"):
            sprite.chunk_key = chunk_key
        chunk = self.chunk_manager.get_chunk(chunk_key)
        if sprite_type in chunk.sprites:
            chunk.sprites[sprite_type].append(sprite)

    def batch_assign_sprites(self, sprite_list: arcade.SpriteList, sprite_type: str):
        for sprite in sprite_list:
            self.assign_sprite_chunk(sprite, sprite_type)

    def assign_tilemap_chunks(self) -> None:
        for layer, sprite_list in self.tilemap.sprite_lists.items():
            if layer.capitalize() in ["Paredes", "Colisiones", "Interactuables"]:
                continue

            layer_key = layer.lower()
            for sprite in sprite_list:
                key = self.chunk_manager.get_chunk_key(sprite.center_x, sprite.center_y)

                chunk = self.chunk_manager.get_chunk(key)
                if layer_key in chunk.sprites:
                    chunk.sprites[layer_key].append(sprite)

    def load_mineral_layer(self) -> None:
        if "Minerales" not in self.tilemap.object_lists:
            return

        temp_layer = self.tilemap.object_lists["Minerales"]

        minerals_to_create = []
        for obj in temp_layer:
            if obj.name and obj.properties:
                try:
                    mineral = self.create_mineral_from_object(obj)
                    mineral.chunk_key = self.chunk_manager.get_chunk_key(
                        mineral.center_x, mineral.center_y
                    )
                    minerals_to_create.append(mineral)
                except ValueError as e:
                    print(e)
        for mineral in minerals_to_create:
            self.assign_sprite_chunk(mineral, "mineral")
        self.load_random_minerals()

    def create_mineral_from_object(self, obj: Any) -> Mineral:
        """Función para crear un minerl a partir de un objeto de Tilemap"""
        shape = obj.shape
        top_left, top_right, *_, bottom_left = shape[:4]
        center_x: float = (top_left[0] + top_right[0]) * 0.5
        center_y: float = (top_left[1] + bottom_left[1]) * 0.5
        size = str(obj.properties.get("size", "mid"))

        return Mineral(
            mineral=obj.name,
            size_type=size,
            center_x=center_x,
            center_y=center_y,
        )

    def load_random_minerals(self) -> None:
        names = list(list(Mineral._resources.keys()))
        sizes = ["big", "mid", "small"]
        # Pongo un límite en los intentos de crear
        # el mineral para evitar loops infinitos
        max_collision_attemps = 10
        mineral_count = random.randint(1, 15)
        random_data = [
            {
                "name": random.choice(names),
                "size": random.choice(sizes),
                "x": random.randint(50, Constants.Game.SCREEN_WIDTH - 50),
                "y": random.randint(50, Constants.Game.SCREEN_HEIGHT - 50),
            }
            for _ in range(mineral_count)
        ]

        # en este loop creo 10 minerales con atributos random
        for i in range(mineral_count):
            data = random_data[i]
            collision_attemps = 0
            mineral = Mineral(
                mineral=data["name"],
                size_type=data["size"],
                center_x=data["x"],
                center_y=data["y"],
            )

            while collision_attemps < max_collision_attemps:
                collisions = mineral.collides_with_list(self.collision_objects)
                if not collisions:
                    self.assign_sprite_chunk(mineral, "mineral")
                    break
                else:
                    mineral.center_x = random.randint(
                        0, Constants.Game.SCREEN_WIDTH - 50
                    )
                    mineral.center_y = random.randint(
                        50, Constants.Game.SCREEN_HEIGHT - 50
                    )
                    collision_attemps += 1

    def world_draw(self):
        self.camera.use()

        if self._actual_area["floor"]:
            self._actual_area["floor"].draw(pixelated=True)
        self.walls.draw(pixelated=True)

        if self._actual_area["trees"]:
            self._actual_area["trees"].draw(pixelated=True)

        self.characters_sprites.draw(pixelated=True)  # dibuja el personaje

        if self._actual_area["copes"]:
            self._actual_area["copes"].draw(pixelated=True)

        if self._actual_area["objects"]:
            self._actual_area["objects"].draw(pixelated=True)

        if self._actual_area["mineral"]:
            self._actual_area["mineral"].draw(pixelated=True)

        if self._view_hitboxes:
            self.draw_hit_boxes()

    def draw_hit_boxes(self):
        self._actual_area["interact"].draw_hit_boxes(
            color=arcade.color.BLUE, line_thickness=2
        )
        self._actual_area["mineral"].draw_hit_boxes(
            color=arcade.color.GREEN, line_thickness=2
        )
        self.player.sprite.draw_hit_box(color=arcade.color.RED, line_thickness=2)

    def gui_draw(self):
        if not self.inventory_dirty:
            return
        self.gui_camera.use()
        self.inventory_sprites.draw(pixelated=True)
        self.items_inventory.draw(pixelated=True)
        for text in self.inventory_texts:
            text.draw()

    def on_draw(self) -> bool | None:
        # Función que se llama cada vez que se dibuja la escena
        self.clear()  # limpia la pantalla
        self.world_draw()
        self.gui_draw()

    def update_inventory(self):
        self.update_inventory_sprites()
        self.update_inventory_texts()
        self.inventory_dirty = True

    def update_inventory_display(self) -> None:
        """Esta función se asegura de actualizar el inventario solo cuando hay cambios en este"""
        current_hash = hash(tuple(sorted(self.player.inventory.items())))

        # Si los hashes son iguales no actualiza la vista
        if self.last_inventory_hash == current_hash:
            return
        self.last_inventory_hash = current_hash
        self.update_inventory()

    def update_inventory_sprites(self):
        self.items_inventory.clear()
        for index, (item, quantity) in enumerate(self.player.inventory.items()):
            container = self.inventory_sprites[index]
            new_item: Item = Item(name=item, quantity=quantity, scale=2)
            new_item.id = index
            new_item.change_container(container.id)
            new_item.change_position(container.center_x, container.center_y)
            self.items_inventory.append(new_item)

    def update_inventory_texts(self):
        self.inventory_texts.clear()
        for index, (item, quantity) in enumerate(self.player.inventory.items()):
            container = self.inventory_sprites[index]
            new_text = arcade.Text(
                text=f"{item} x {quantity}",
                font_size=9,
                x=container.center_x,
                y=container.center_y - (container.height * 0.5 + 10),
                anchor_x="center",
                anchor_y="baseline",
            )
            self.inventory_texts.append(new_text)

    def update_actual_chunk(self):
        active_chunk_lists = {
            "mineral": arcade.SpriteList(),
            "interact": arcade.SpriteList(),
            "floor": arcade.SpriteList(),
            "trees": arcade.SpriteList(),
            "copes": arcade.SpriteList(),
            "objects": arcade.SpriteList(),
        }
        player_key = self.chunk_manager.get_chunk_key(
            self.player.sprite.center_x, self.player.sprite.center_y
        )
        nearby_chunks = self.chunk_manager.get_nearby_chunks(center_key=player_key)
        self._collision_list.clear()
        self._collision_list.extend(self.walls)
        for key in nearby_chunks:
            chunk = self.chunk_manager.get_chunk(key)
            for list_name, sprite_list in active_chunk_lists.items():
                sprites = chunk.sprites.get(list_name, [])
                sprite_list.extend(sprites)
                if list_name in ["floor", "copes"]:
                    continue
                self._collision_list.extend(sprites)
        self._actual_area = active_chunk_lists

    def change_to_menu(self) -> None:
        DataManager.store_actual_data(self.player, "TEST")
        self.callback(Constants.SignalCodes.CHANGE_VIEW, "MENU")

    def open_chest(self, chest_id: str) -> None:
        new_scene = Chest(
            chest_id=chest_id,
            player=self.player,
            previusScene=self,
        )
        self.window.show_view(new_scene)

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        match symbol:
            case arcade.key.SPACE:
                if Constants.Game.DEBUG_MODE:
                    self.callback(Constants.SignalCodes.CHANGE_VIEW, "MENU")
                    return True
            case arcade.key.E:
                return self.handleInteractions()

            case arcade.key.ESCAPE:
                DataManager.store_actual_data(self.player, "TEST")
                self.keys_pressed.clear()
                self.player.stop_state()
                self.callback(Constants.SignalCodes.PAUSE_GAME, "Pause Game")
                return True

            case arcade.key.M:
                if Constants.Game.DEBUG_MODE:
                    self.callback(Constants.SignalCodes.CHANGE_VIEW, "MIX_TABLE")
                    return True
            case arcade.key.H:
                if Constants.Game.DEBUG_MODE:
                    self._view_hitboxes = not self._view_hitboxes
                    return True
            case arcade.key.T:
                arcade.print_timings()
            case arcade.key.Z:
                if Constants.Game.DEBUG_MODE:
                    self.camera.zoom = (
                        Constants.Game.FOREST_ZOOM_CAMERA
                        if (self.camera.zoom == 1)
                        else 1
                    )
            case arcade.key.F:
                self.player.attack(self.enemies[0])

        self.keys_pressed.add(symbol)
        return None

    def handleInteractions(self):
        closest_obj = arcade.get_closest_sprite(
            self.player.sprite, self._actual_area["interact"]
        )
        if closest_obj and closest_obj[1] <= 50:
            return self.process_object_interaction(closest_obj[0])

        closest_obj = arcade.get_closest_sprite(
            self.player.sprite, self._actual_area["mineral"]
        )
        if closest_obj and closest_obj[1] <= 50:
            return self.process_mineral_interaction(closest_obj[0])
        del closest_obj

        return False

    def process_object_interaction(self, interact_obj: Object) -> bool:
        """Procesa la interaccion con un objeto"""
        object_name = interact_obj.name.lower()
        self.keys_pressed.clear()
        self.player.stop_state()
        if "chest" in object_name:
            self.open_chest(chest_id=object_name)
            return True

        match object_name:
            case "door":
                # Cambio de escena y guardo los datos actuales
                DataManager.store_actual_data(self.player, "TEST")
                self.callback(Constants.SignalCodes.CHANGE_VIEW, "LABORATORY")
                return True
            case "comerce":
                # Cambiar a la escena de compra
                return True
        return False

    def process_mineral_interaction(self, mineral: Mineral) -> bool:
        if len(self.player.inventory) >= 4:
            return True
        mineral.setup()
        mineral.state_machine.process_state(arcade.key.E)
        self.player.add_to_inventory(mineral.mineral, 1)

        # Cambio el valor del hash del inventario para que se actualice
        self.last_inventory_hash = None

        if mineral.should_removed:
            mineral.remove_from_sprite_lists()
            self.chunk_manager.chunks[mineral.chunk_key].sprites["mineral"].remove(
                mineral
            )
        return True

    def on_key_release(self, symbol: int, modifiers: int) -> bool | None:
        self.keys_pressed.discard(symbol)
        self.player.process_state(-symbol)

    def on_update(self, delta_time: float) -> bool | None:
        self.player.update_animation(delta_time)
        player = self.player.sprite
        lastPosition = (player.center_x, player.center_y)

        if self.keys_pressed:
            for key in self.keys_pressed:
                self.player.process_state(key)

        self.player.update_position()
        for enemy in self.enemies:
            enemy.update(delta_time, player.position)

        player_moved = (
            abs(player.center_x - lastPosition[0]) > 0
            or abs(player.center_y - lastPosition[1]) > 0
        )
        if player_moved or self.camera.position != self.player.sprite.position:
            cam_lerp = 0.25 if (player_moved) else 0.06
            self.camera.position = arcade.math.lerp_2d(
                self.camera.position, self.player.sprite.position, cam_lerp
            )

        self.update_inventory_display()

        if player_moved:
            self.update_actual_chunk()
            # Detección de colisiones
            if self.player_collides():
                self.player.sprite.center_x, self.player.sprite.center_y = lastPosition

    def player_collides(self) -> bool:
        """Función para detectar si hay colisiones"""
        if not self._collision_list:
            return False

        return (
            len(
                arcade.check_for_collision_with_list(
                    self.player.sprite, self._collision_list
                )
            )
            > 0
        )

    def clean_up(self) -> None:
        for area_list in self._actual_area.values():
            area_list.clear()

        self.chunk_manager.get_chunk_key.cache_clear()
        del self.chunk_manager
        del self.player
        del self.camera
        del self.interact_objects
        del self._collision_list
        del self.floor
        del self.walls
        del self.background_objects
        del self.collision_objects
        del self.last_inventory_hash
        del self.keys_pressed
        del self.inventory_dirty

        del self.characters_sprites
        del self.inventory_sprites
        del self.items_inventory
        del self.inventory_texts

        self._actual_area.clear()

    def get_screenshot(self):
        self.clear()
        self.world_draw()
        return arcade.get_image()
