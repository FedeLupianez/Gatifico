import arcade
from typing import Any, Callable
from random import randint, choice

from characters.Enemy import Enemy
from scenes.View import View, Object
import Constants
from characters.Player import Player
from items.Mineral import Mineral
import DataManager as Dm
from items.Item import Item
from .utils import add_containers_to_list
from .Chest import Chest
from Managers.ChunkManager import Chunk_Manager


class Forest(View):
    def __init__(self, callback: Callable) -> None:
        tileMapUrl = Dm.get_path("Mapa.tmx")
        super().__init__(background_url=None, tilemap_url=tileMapUrl)
        self.window.set_mouse_visible(True)

        # Constantes de clase
        self.player = Player()
        self.callback = callback  # Callback al ViewManager

        # Le pongo el zoom a la cámara
        self.camera.zoom = Constants.Game.FOREST_ZOOM_CAMERA
        self.camera.position = self.player.sprite.position
        self._half_w = (self.camera.viewport.width / self.camera.zoom) * 0.5
        self._half_h = (self.camera.viewport.height / self.camera.zoom) * 0.5
        self.is_first_load: bool = True

        self.chunk_manager = Chunk_Manager(
            int(self.camera.viewport.width // 7), int(self.camera.viewport.height // 6)
        )
        # constantes para precalcular el tamaño del mapa
        self._map_width = self.tilemap.width * self.tilemap.tile_width
        self._map_height = self.tilemap.height * self.tilemap.tile_height
        self._dimensions_diff = (
            (self._map_width - self._half_w),
            (self._map_height - self._half_h),
        )

        self.keys_pressed: set = set()
        # Flag para actualizaciones selectivas del inventario
        self.inventory_dirty = True
        # Hash para detectar cambios en el inventario
        self.last_inventory_hash = None
        self._view_hitboxes: bool = False  # Flag para mostrar las hitboxes

        self.areas: dict[tuple, dict[str, list]] = {}
        self._actual_area: dict[str, arcade.SpriteList] = {
            "collisions": arcade.SpriteList(use_spatial_hash=True, lazy=True),
            "interact": arcade.SpriteList(use_spatial_hash=True, lazy=True),
            "mineral": arcade.SpriteList(use_spatial_hash=True, lazy=True),
            "floor": arcade.SpriteList(use_spatial_hash=True, lazy=True),
            "sky": arcade.SpriteList(use_spatial_hash=True, lazy=True),
            "objects": arcade.SpriteList(use_spatial_hash=True, lazy=True),
            "items": arcade.SpriteList(use_spatial_hash=True),
            "enemy": arcade.SpriteList(use_spatial_hash=True),
        }
        # Variable para precomputar las listas de colisiones
        self._collision_list = arcade.SpriteList(use_spatial_hash=True, lazy=True)
        self.update_actual_chunk()
        self._setup_scene()

    def _setup_scene(self) -> None:
        """Configuración principal"""
        self.setup_spritelists()
        self.setup_scene_layer()
        self.setup_player()
        self.setup_enemies()
        # Hago que la vida siempre esté en el top de la ventana
        for i in range(len(self.player.lifes_sprite_list)):
            self.player.lifes_sprite_list[i].center_y = self.window.height - 44
        self.update_inventory_sprites()
        self.update_inventory_texts()
        # El chunk_manager carga todo el mundo
        self.chunk_manager.load_world(self.tilemap)
        self.update_actual_chunk()
        self.update_sizes(
            int(self.camera.viewport.width), int(self.camera.viewport.height)
        )

    def setup_spritelists(self):
        # Listas de Sprites
        self.characters_sprites: arcade.SpriteList = arcade.SpriteList()
        self.inventory_sprites: arcade.SpriteList = arcade.SpriteList()
        self.items_inventory: arcade.SpriteList = arcade.SpriteList()
        self.inventory_texts: list[arcade.Text] = []
        self.setup_inventory_containers()
        if Constants.Game.DEBUG_MODE:
            self.fps_text = arcade.Text("0", 10, 10, arcade.color.WHITE, 12)

    def setup_enemies(self) -> None:
        for _ in range(5):
            enemy = Enemy(
                randint(0, int(self._map_width)),
                randint(0, int(self._map_height)),
                self.chunk_manager.update_enemy_key,
                self.chunk_manager.drop_item,
            )
            while enemy.collides_with_list(self._collision_list):
                enemy.center_x = randint(0, int(self._map_width))
                enemy.center_y = randint(0, int(self._map_height))

            self.chunk_manager.assign_sprite_chunk(enemy, "enemy")

    def setup_inventory_containers(self) -> None:
        """Agrego los contenedores a la lista del inventario"""
        CONTAINER_SIZE = 35
        DISTANCE_BETWEEN_CONTAINERS = 57.5
        ITEMS_INIT = Constants.PlayerConfig.INVENTORY_POSITION
        positions = [
            (int(ITEMS_INIT[0] + (DISTANCE_BETWEEN_CONTAINERS * i)), ITEMS_INIT[1] + 5)
            for i in range(Constants.PlayerConfig.MAX_ITEMS_IN_INVENTORY)
        ]
        add_containers_to_list(
            positions, self.inventory_sprites, container_size=CONTAINER_SIZE
        )
        inventory_sprite = arcade.Sprite(Dm.get_path("inventory_tools.png"), scale=3)
        inventory_sprite.scale_y = 3.2
        inventory_sprite.center_x = self.window.width * 0.5
        inventory_sprite.center_y = ITEMS_INIT[1]
        self.inventory_sprites.append(inventory_sprite)

    def setup_player(self) -> None:
        # Cargo el inventario anterior del jugador, si no tiene le pongo uno vacío
        player_data = Dm.game_data["player"]
        self.player.inventory = player_data.get("inventory", {})
        self.player.setup(position=(1000, 500))  # Setup del personaje
        # Le asigno la chunk_key al jugador
        self.player.chunk_key = self.chunk_manager.get_chunk_key(
            self.player.sprite.center_x, self.player.sprite.center_y
        )
        self.player.actual_floor = "grass"
        self.characters_sprites.append(self.player.sprite)
        del player_data

    def setup_scene_layer(self) -> None:
        if not self.tilemap:
            raise ValueError("TileMap no puede set None")

        # Capas de vista :
        # self.walls = self.scene["Paredes"]
        # Capas de colisiones :
        self.collision_objects = self.scene["Objects"]
        # self.interact_objects = self.load_object_layers("Interactuables", self.tilemap)
        # self.chunk_manager.batch_assign_sprites(self.interact_objects, "interact")
        self.load_antique_minerals()
        # Variable para precomputar las listas de colisiones
        self._collision_list = arcade.SpriteList(use_spatial_hash=True, lazy=True)
        for object in self.collision_objects:
            self._collision_list.append(object)

    def load_antique_minerals(self) -> None:
        minerals_to_create = []
        lines = Dm.read_file("minerals_in_map.txt")
        for line in lines:
            name, size, x, y, touches = line.split(",")
            mineral = Mineral(
                mineral=name, size_type=size, center_x=float(x), center_y=float(y)
            )
            mineral.touches = int(touches)
            minerals_to_create.append(mineral)

        if len(minerals_to_create) < 5:
            new_minerals = self.load_random_minerals()
            minerals_to_create.extend(new_minerals)

        for mineral in minerals_to_create:
            self.chunk_manager.assign_sprite_chunk(mineral, "mineral")

    def save_minerals(self) -> None:
        # Recorro todos los chunks
        result_file: str = ""
        counter = 0
        for chunk in self.chunk_manager.chunks.values():
            for mineral in chunk.sprites["mineral"]:
                counter += 1
                result_file += f"{mineral.mineral},{mineral.size_type},{mineral.center_x},{mineral.center_y:},{mineral.touches}\n"
        print(f"Guardando {counter} minerales")
        Dm.write_file("minerals_in_map.txt", result_file, "w")

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

    def load_random_minerals(self) -> list[Mineral]:
        names = list(list(Mineral._resources.keys()))
        sizes = ["big", "mid", "small"]
        max_collision_attemps = 10
        mineral_count = randint(1, 15)
        random_data = [
            {
                "name": choice(names),
                "size": choice(sizes),
                "x": randint(50, Constants.Game.SCREEN_WIDTH - 50),
                "y": randint(50, Constants.Game.SCREEN_HEIGHT - 50),
            }
            for _ in range(mineral_count)
        ]

        created_minerals = []
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
                collisions = mineral.collides_with_list(self._collision_list)
                if not collisions:
                    created_minerals.append(mineral)
                    break
                else:
                    mineral.center_x = randint(0, Constants.Game.SCREEN_WIDTH - 50)
                    mineral.center_y = randint(50, Constants.Game.SCREEN_HEIGHT - 50)
                    collision_attemps += 1
        print("Minerales creados aleatoriamente : ", len(created_minerals))
        return created_minerals

    def world_draw(self):
        draw_order = [
            "floor",
            "items",
            "objects",
            "mineral",
            "characters",
            "sky",
        ]
        self.camera.use()
        for layer in draw_order:
            if layer in self._actual_area:
                self._actual_area[layer].draw(pixelated=True)
            elif layer == "characters":
                self.characters_sprites.draw(pixelated=True)
                self._actual_area["enemy"].draw(pixelated=True)
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
        self._actual_area["interact"].draw_hit_boxes(
            color=arcade.color.AFRICAN_VIOLET, line_thickness=2
        )
        self._actual_area["objects"].draw_hit_boxes(
            color=arcade.color.ANTIQUE_BRONZE, line_thickness=2
        )

    def gui_draw(self):
        if not self.inventory_dirty:
            return
        self.gui_camera.use()
        self.fps_text.draw()
        self.inventory_sprites.draw(pixelated=True)
        self.items_inventory.draw(pixelated=True)
        self.ui_sprites.draw(pixelated=True)
        for text in self.inventory_texts:
            text.draw()
        self.player.lifes_sprite_list.draw(pixelated=True)

    # Funciones de actualización

    def update_inventory(self):
        """Esta función se asegura de actualizar el inventario solo cuando hay cambios en este"""
        current_hash = hash(tuple(sorted(self.player.inventory.items())))

        # Si los hashes son iguales no actualiza la vista
        if self.last_inventory_hash == current_hash:
            return
        self.last_inventory_hash = current_hash
        self.update_inventory_sprites()
        self.update_inventory_texts()
        self.inventory_dirty = True

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
        for index, item in enumerate(self.items_inventory):
            container = self.inventory_sprites[index]
            new_text = arcade.Text(
                text=str(item.quantity),
                font_size=9,
                x=container.center_x,
                y=container.center_y - (container.height * 0.5 + 10),
                anchor_x="center",
                anchor_y="baseline",
                color=arcade.color.BLACK,
            )
            self.inventory_texts.append(new_text)

    def update_actual_chunk(self):
        active_chunk_lists = {
            "mineral": arcade.SpriteList(use_spatial_hash=True),
            "interact": arcade.SpriteList(use_spatial_hash=True),
            "floor": arcade.SpriteList(use_spatial_hash=True),
            "sky": arcade.SpriteList(use_spatial_hash=True),
            "objects": arcade.SpriteList(use_spatial_hash=True),
            "items": arcade.SpriteList(use_spatial_hash=True),
            "enemy": arcade.SpriteList(use_spatial_hash=True),
        }
        nearby_chunks = self.chunk_manager.get_nearby_chunks(
            center_key=self.player.chunk_key
        )
        self._collision_list.clear()
        for key in nearby_chunks:
            chunk = self.chunk_manager.get_chunk(key)
            for list_name, sprite_list in active_chunk_lists.items():
                sprites = chunk.sprites.get(list_name, [])
                sprite_list.extend(sprites)
                if list_name.lower() in ["floor", "sky"]:
                    continue
                self._collision_list.extend(sprites)
        self._actual_area = active_chunk_lists

    def update_camera(self, player_moved: bool) -> None:
        cam_lerp = (
            Constants.Game.CAMERA_LERP_FAST
            if (player_moved)
            else Constants.Game.CAMERA_LERP_SLOW
        )

        target_x = self.player.sprite.center_x
        target_y = self.player.sprite.center_y

        # Le pongo el limite del mundo a la cámara
        target_x = max(self._half_w, min(target_x, self._dimensions_diff[0]))
        target_y = max(self._half_h, min(target_y, self._dimensions_diff[1]))

        self.camera.position = arcade.math.lerp_2d(
            self.camera.position, (target_x, target_y), cam_lerp
        )

    # Funciones de cambio de escena

    def change_to_menu(self) -> None:
        Dm.store_actual_data(self.player, "TEST")
        self.callback(Constants.SignalCodes.CHANGE_VIEW, "MENU")

    def open_chest(self, chest_id: str) -> None:
        new_scene = Chest(
            chest_id=chest_id,
            previusScene=self,
        )
        self.is_first_load = False
        self.window.show_view(new_scene)

    # Funciones de Interacción con objetos
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
        closest_obj = arcade.get_closest_sprite(
            self.player.sprite, self._actual_area["items"]
        )
        if closest_obj and closest_obj[1] <= 50:
            item = closest_obj[0]
            self._actual_area["items"].remove(item)
            self.player.add_to_inventory(item.name, item.quantity)
            self.chunk_manager.chunks[self.player.chunk_key].sprites["items"].remove(
                item
            )
            return True

        return False

    def process_enemy_interaction(self) -> None:
        closest_obj = arcade.get_closest_sprite(
            self.player.sprite, self._actual_area["enemy"]
        )
        if closest_obj and closest_obj[1] <= 50:
            self.player.attack(closest_obj[0])
            return

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
                Dm.store_actual_data(self.player, "TEST")
                self.save_minerals()
                arcade.play_sound(Dm.get_sound("door.mp3"))
                self.callback(Constants.SignalCodes.CHANGE_VIEW, "LABORATORY")
                return True
            case "comerce":
                # Cambiar a la escena de compra
                return True
        return False

    def process_mineral_interaction(self, mineral: Mineral) -> bool:
        """Procesa la interacción con un mineral"""
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

    # Funciones de escena de arcade

    def on_draw(self) -> bool | None:
        # Función que se llama cada vez que se dibuja la escena
        self.clear()  # limpia la pantalla
        self.world_draw()
        self.gui_draw()

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        match symbol:
            case arcade.key.SPACE:
                if Constants.Game.DEBUG_MODE:
                    self.callback(Constants.SignalCodes.CHANGE_VIEW, "MENU")
                    return True
            case arcade.key.E:
                return self.handleInteractions()

            case arcade.key.ESCAPE:
                Dm.store_actual_data(self.player, "TEST")
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
                self.process_enemy_interaction()

        self.keys_pressed.add(symbol)
        return None

    def on_key_release(self, symbol: int, modifiers: int) -> bool | None:
        self.keys_pressed.discard(symbol)
        self.player.process_state(-symbol)

    def on_show_view(self) -> None:
        if self.is_first_load:
            self.camera.position = self.player.sprite.position

    def on_fixed_update(self, delta_time: float):
        self.player.update_animation(delta_time)
        for enemy in self._actual_area["enemy"]:
            enemy.update(delta_time, self.player.sprite.position, self._collision_list)

    def on_update(self, delta_time: float) -> bool | None:
        self.fps_text.text = f"{int(1 / delta_time)}"
        if self.player.lifes == 0:
            self.player.reset()
            self.callback(Constants.SignalCodes.CHANGE_VIEW, "MENU")
            return
        player = self.player.sprite
        lastPosition = (player.center_x, player.center_y)

        if self.keys_pressed:
            for key in self.keys_pressed:
                self.player.process_state(key)

        self.player.update_position()

        player_moved = (
            abs(player.center_x - lastPosition[0]) > 0
            or abs(player.center_y - lastPosition[1]) > 0
        )

        self.update_inventory()

        new_chunk_key = self.chunk_manager.get_chunk_key(
            player.center_x, player.center_y
        )
        if new_chunk_key != self.player.chunk_key:
            self.player.chunk_key = new_chunk_key
            self.update_actual_chunk()

        if player_moved:
            self.update_camera(player_moved)
            # Detección de colisiones
            if self.player_collides():
                self.player.sprite.center_x, self.player.sprite.center_y = lastPosition
                return

            if (
                self.player.sprite.top >= self._map_height
                or self.player.sprite.bottom < 0
                or self.player.sprite.left < 0
                or self.player.sprite.right > self._map_width
            ):
                self.player.sprite.center_x, self.player.sprite.center_y = lastPosition
                return

    def on_mouse_press(
        self, x: int, y: int, button: int, modifiers: int
    ) -> bool | None:
        if button == arcade.MOUSE_BUTTON_LEFT:
            items_hit = arcade.get_sprites_at_point((x, y), self.items_inventory)
            if items_hit:
                item = items_hit[-1]
                # Tiro el item al suelo
                assert isinstance(item, Item), "No se encontró el item"
                item.position = (
                    self.player.sprite.position[0] + 20,
                    self.player.sprite.position[1],
                )
                item.scale = 1
                self.chunk_manager.assign_sprite_chunk(item, "items")
                self.items_inventory.remove(item)
                self.player.throw_item(item.name)
                self.update_actual_chunk()
                return True
            # Manejo del estado del sonido por si tocan el boton de silencio
            signal = self.change_bg_sound_state((x, y))
            self.callback(signal)
            return True

        return False

    def player_collides(self) -> bool:
        """Función para detectar si hay colisiones"""
        if not self._collision_list:
            return False
        return any(
            arcade.check_for_collision_with_list(
                self.player.sprite, self._collision_list
            )
        )

    def clean_up(self) -> None:
        for chunk_list in self._actual_area.values():
            chunk_list.clear()

        self.chunk_manager.get_chunk_key.cache_clear()
        del self.chunk_manager
        del self.player
        del self.camera
        # del self.interact_objects
        del self._collision_list
        del self.collision_objects
        del self.last_inventory_hash
        del self.keys_pressed
        del self.inventory_dirty

        del self.characters_sprites
        del self.inventory_sprites
        del self.items_inventory
        del self.inventory_texts

        self._actual_area.clear()

    def get_screenshot(self, draw_ui: bool = False):
        self.clear()
        self.world_draw()
        if draw_ui:
            self.gui_draw()
        return arcade.get_image()
