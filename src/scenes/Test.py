import arcade
from typing import Optional, Dict, Any, Callable


from scenes.View import View
import Constants
from characters.Player import Player
from items.Mineral import Mineral
import DataManager
from items.Item import Item
from .utils import add_containers_to_list, is_in_box
from .Chest import Chest

import random

_minerals_cache: Optional[Dict[str, Any]] = None


def get_minerals_resources() -> Dict[str, Any]:
    """Hago un Lazy loading de los recursos de los minerales con caché"""
    global _minerals_cache
    if _minerals_cache is None:
        _minerals_cache = DataManager.loadData("Minerals.json")
    return _minerals_cache


class Test(View):
    PLAYER_AREA_SIZE_X = 200
    PLAYER_AREA_SIZE_Y = 200

    def __init__(self, callback: Callable, player: Player) -> None:
        tileMapUrl = ":resources:Maps/Tests.tmx"
        super().__init__(background_url=None, tilemap_url=tileMapUrl)
        self.window.set_mouse_visible(False)

        self.callback = callback

        self.player = player  # Defino el personaje

        self.keys_pressed: set = set()
        # Flag para actualizaciones selectivas del inventario
        self.inventory_dirty = True
        # Hash para detectar cambios en el inventario
        self.last_inventory_hash = None
        self.mineral_active: Mineral | None
        self.mineral_interact_time: float = 0.0
        self.load_area = (
            self.player.sprite.center_y - self.PLAYER_AREA_SIZE_Y,  # Top
            self.player.sprite.center_y + self.PLAYER_AREA_SIZE_Y,  # Bottom
            self.player.sprite.center_x + self.PLAYER_AREA_SIZE_X,  # Right
            self.player.sprite.center_x - self.PLAYER_AREA_SIZE_X,  # Left
        )
        self._nearby_objects_cache: dict = {
            "interact": [],
            "mineral": [],
            "sprite_lists": {
                "interact": arcade.SpriteList(use_spatial_hash=True),
                "mineral": arcade.SpriteList(use_spatial_hash=True),
            },
        }
        self._view_hitboxes: bool = False
        self._setup_scene()

    def _setup_scene(self) -> None:
        """Configuración principal"""
        self.setup_spritelists()
        self.setup_scene_layer()
        self.setup_player()
        self.update_inventory_sprites()
        self.update_inventory_texts()

    def setup_spritelists(self):
        # Listas de Sprites
        self.player_sprite: arcade.SpriteList = arcade.SpriteList()
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
        self.player.setup((900, 700))
        self.player_sprite.append(self.player.sprite)
        # Camara para seguir al jugador :
        self.camera.zoom = Constants.Game.FOREST_ZOOM_CAMERA
        self.camera.position = self.player.sprite.position
        del player_data

    def setup_scene_layer(self) -> None:
        if not self.tilemap:
            raise ValueError("TileMap no puede set None")

        # Capas de vista :
        self.floor = self.scene["Piso"]
        self.walls = self.scene["Paredes"]
        self.background_objects = self.scene["Objetos"]
        # Capas de colisiones :
        self.collision_objects = self.load_object_layers("Colisiones", self.tilemap)
        self.interact_objects = self.load_object_layers("Interactuables", self.tilemap)
        self.minerals_layer = self.load_mineral_layer()
        # Variable para precomputar las listas de colisiones
        self._collision_list = [self.collision_objects, self.walls]
        # Precalculo la lista de colisiones interactuables
        self.interact_list = [self.interact_objects, self.minerals_layer]
        self.search_rect: arcade.SpriteSolidColor | None = None

    def load_mineral_layer(self) -> arcade.SpriteList:
        if "Minerales" not in self.tilemap.object_lists:
            return arcade.SpriteList()

        temp_layer = self.tilemap.object_lists["Minerales"]
        temp_list = arcade.SpriteList(use_spatial_hash=True)
        mineral_resources = get_minerals_resources()

        for obj in temp_layer:
            if not obj.name or not obj.properties:
                continue
            try:
                mineral = self.create_mineral_from_object(obj)
                temp_list.append(mineral)
            except ValueError as e:
                print(e)
        temp_list.extend(self.load_random_minerals(mineral_resources))
        return temp_list

    def create_mineral_from_object(self, obj: Any) -> Mineral:
        """Función para crear un minerl a partir de un objeto de Tilemap"""
        shape = obj.shape
        if len(shape) != 4:
            raise ValueError(f"Forma del objeto {obj.name} invalida")

        top_left, top_right, *_, bottom_left = shape[:4]
        width: float = top_right[0] - top_left[0]
        height: float = top_left[1] - bottom_left[1]
        center_x: float = top_left[0] + (width) / 2
        center_y: float = bottom_left[1] + (height) / 2
        size = str(obj.properties.get("size", "mid"))

        return Mineral(
            mineral=obj.name,
            size_type=size,
            center_x=center_x,
            center_y=center_y,
            mineral_attr=get_minerals_resources(),
        )

    def load_random_minerals(self, mineral_resources: Dict) -> arcade.SpriteList:
        temp_list = arcade.SpriteList()
        names = list(list(mineral_resources.keys()))
        sizes = ["big", "mid", "small"]
        # Pongo un límite en los intentos de crear
        # el mineral para evitar loops infinitos
        max_collision_attemps = 10
        collision_attemps = 0

        # en este loop creo 10 minerales con atributos random
        for _ in range(10):
            mineral = Mineral(
                mineral=random.choice(names),
                size_type=random.choice(sizes),
                center_x=random.randint(0, Constants.Game.SCREEN_WIDTH),
                center_y=random.randint(0, Constants.Game.SCREEN_HEIGHT),
                mineral_attr=mineral_resources,
            )

            while collision_attemps < max_collision_attemps:
                collisions = mineral.collides_with_list(self.collision_objects)
                if not collisions:
                    break
                mineral.center_x = random.randint(50, Constants.Game.SCREEN_WIDTH - 50)
                mineral.center_y = random.randint(50, Constants.Game.SCREEN_HEIGHT - 50)
                collision_attemps += 1
            if collision_attemps < 10:
                temp_list.append(mineral)
        return temp_list

    def word_draw(self):
        self.camera.use()
        self.scene.draw(pixelated=True)  # dibuja la escena
        self.player_sprite.draw(pixelated=True)  # dibuja el personaje
        self._nearby_objects_cache["sprite_lists"]["mineral"].draw(pixelated=True)
        if self._view_hitboxes:
            self.player.sprite.draw_hit_box(color=arcade.color.RED, line_thickness=2)
            for sprite in self.interact_objects:
                sprite.draw_hit_box(color=arcade.color.GREEN, line_thickness=2)

    def gui_draw(self):
        self.gui_camera.use()
        if self.inventory_dirty:
            self.inventory_sprites.draw(pixelated=True)
            self.items_inventory.draw(pixelated=True)
            for text in self.inventory_texts:
                text.draw()

    def on_draw(self) -> bool | None:
        # Función que se llama cada vez que se dibuja la escena
        self.clear()  # limpia la pantalla
        self.word_draw()
        self.gui_draw()

    def update_inventory_display(self) -> None:
        """Esta función se asegura de actualizar el inventario solo cuando hay cambios en este"""
        current_hash = hash(tuple(sorted(self.player.inventory.items())))

        # Si los hashes son iguales no actualiza la vista
        if self.last_inventory_hash == current_hash:
            return
        self.last_inventory_hash = current_hash
        self.update_inventory_sprites()
        self.update_inventory_texts()

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
                y=container.center_y - (container.height / 2 + 10),
                anchor_x="center",
                anchor_y="baseline",
            )
            self.inventory_texts.append(new_text)

    def update_nearby_cache(self):
        self._nearby_objects_cache["mineral"] = (
            self.minerals_layer.get_nearby_sprites_gpu(
                self.player.sprite.position,
                (Test.PLAYER_AREA_SIZE_X, Test.PLAYER_AREA_SIZE_Y),
            )
        )
        self._nearby_objects_cache["sprite_lists"]["mineral"].clear()
        for mineral in self._nearby_objects_cache["mineral"]:
            self._nearby_objects_cache["sprite_lists"]["mineral"].append(mineral)

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
        if symbol == arcade.key.SPACE and Constants.Game.DEBUG_MODE:
            DataManager.store_actual_data(self.player, "TEST")
            self.callback(Constants.SignalCodes.CHANGE_VIEW, "MENU")
            return True

        if symbol == arcade.key.E:
            return self.handleInteractions()

        if symbol == arcade.key.ESCAPE:
            DataManager.store_actual_data(self.player, "TEST")
            self.keys_pressed.clear()
            self.player.stop_state()
            self.callback(Constants.SignalCodes.PAUSE_GAME, "Pause Game")
            return True

        if symbol == arcade.key.H and Constants.Game.DEBUG_MODE:
            self._view_hitboxes = not self._view_hitboxes
            return True

        if symbol == arcade.key.T and Constants.Game.DEBUG_MODE:
            arcade.print_timings()

        self.keys_pressed.add(symbol)
        return None

    def handleInteractions(self):
        closest_obj = arcade.get_closest_sprite(
            self.player.sprite, self.interact_objects
        )
        if closest_obj and closest_obj[1] <= 50:
            return self.process_object_interaction(closest_obj[0])

        closest_obj = arcade.get_closest_sprite(self.player.sprite, self.minerals_layer)
        if closest_obj and closest_obj[1] <= 50:
            self.mineral_interact_time = 0.6
            self.mineral_active = closest_obj[0]
            return self.process_mineral_interaction(closest_obj[0])
        del closest_obj

        return False

    def process_object_interaction(self, interact_obj: arcade.Sprite) -> bool:
        """Procesa la interaccion con un objeto"""
        object_name = interact_obj.name.lower()
        self.keys_pressed.clear()
        self.player.stop_state()
        if object_name == "door":
            # Cambio de escena y guardo los datos actuales
            DataManager.store_actual_data(self.player, "TEST")
            self.callback(Constants.SignalCodes.CHANGE_VIEW, "LABORATORY")
            return True
        if "chest" in object_name:
            self.open_chest(chest_id=object_name)
            return True
        return False

    def process_mineral_interaction(self, mineral: Mineral) -> bool:
        mineral.setup()
        mineral.state_machine.process_state(arcade.key.E)
        self.player.add_to_inventory(mineral.mineral, 1)

        # Cambio el valor del hash del inventario para que se actualice
        self.last_inventory_hash = None

        if mineral.should_removed:
            mineral.remove_from_sprite_lists()
        return True

    def on_key_release(self, symbol: int, modifiers: int) -> bool | None:
        self.keys_pressed.discard(symbol)
        self.player.process_state(-symbol)

    def on_update(self, delta_time: float) -> bool | None:
        self.player.update_animation(delta_time)
        player = self.player.sprite
        lastPosition = player.center_x, player.center_y

        for key in self.keys_pressed:
            self.player.process_state(key)

        self.player.update_position()

        player_moved = (player.center_x != lastPosition[0]) or (
            player.center_y != lastPosition[1]
        )

        cam_lerp = 0.25 if (player_moved) else 0.06
        self.camera.position = arcade.math.lerp_2d(
            self.camera.position, self.player.sprite.position, cam_lerp
        )

        self.update_inventory_display()

        if player_moved:
            if not is_in_box(
                self.player.sprite.center_x,
                self.player.sprite.center_y,
                top=self.load_area[0],
                bottom=self.load_area[1],
                right=self.load_area[2],
                left=self.load_area[3],
            ):
                self.update_nearby_cache()

                self.load_area = (
                    self.player.sprite.center_y - self.PLAYER_AREA_SIZE_Y,  # Top
                    self.player.sprite.center_y + self.PLAYER_AREA_SIZE_Y,  # Bottom
                    self.player.sprite.center_x + self.PLAYER_AREA_SIZE_X,  # Right
                    self.player.sprite.center_x - self.PLAYER_AREA_SIZE_X,  # Left
                )

            # Detección de colisiones
            if self.check_collision():
                self.player.sprite.center_x, self.player.sprite.center_y = lastPosition

        if self.mineral_interact_time > 0 and self.mineral_active:
            self.mineral_active.update_flash(delta_time)
            self.mineral_interact_time -= delta_time

            if self.mineral_interact_time <= 0:
                self.mineral_active = None

    def check_collision(self) -> bool:
        """Función para detectar si hay colisiones"""
        player = self.player.sprite

        physical_collisions = arcade.check_for_collision_with_lists(
            self.player.sprite, self._collision_list
        )

        if physical_collisions:
            return True

        if arcade.check_for_collision_with_lists(
            player,
            [
                self.interact_objects,
                self._nearby_objects_cache["sprite_lists"]["mineral"],
            ],
        ):
            return True

        return False

    def clean_up(self) -> None:
        del self.player
        del self.camera
        del self.interact_objects
        del self.minerals_layer
        del self._collision_list
        del self.floor
        del self.walls
        del self.background_objects
        del self.collision_objects
        del self.last_inventory_hash
        del self.keys_pressed
        del self.inventory_dirty
        del self.interact_list

        del self.player_sprite
        del self.inventory_sprites
        del self.items_inventory
        del self.inventory_texts

        self._nearby_objects_cache.clear()

    def get_screenshot(self):
        self.clear()
        self.word_draw()
        return arcade.get_image()
