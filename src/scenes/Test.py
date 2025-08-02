import arcade
from typing import Optional, Dict, Any

from scenes.View import View
import Constants
from characters.Player import Player
from typing import Callable
from items.Mineral import Mineral
import DataManager
from items.Item import Item
from Types import PlayerData
from .utils import add_containers_to_list
from .Chest import Chest
from .Pause import Pause

import random

_minerals_cache: Optional[Dict[str, Any]] = None
_nearby_objects_cache: dict[str, list] = {"interact": [], "mineral": []}


def get_minerals_resources() -> Dict[str, Any]:
    """Hago un Lazy loading de los recursos de los minerales con caché"""
    global _minerals_cache
    if _minerals_cache is None:
        _minerals_cache = DataManager.loadData("Minerals.json")
    return _minerals_cache


def is_near_to_sprite(
    sprite1: arcade.Sprite, sprite2: arcade.Sprite, tolerance: float = 16.0
) -> bool:
    dx = sprite1.center_x - sprite2.center_x
    dy = sprite1.center_y - sprite2.center_y
    return (dx * dx + dy * dy) <= (tolerance * tolerance)


class Test(View):
    def __init__(self, callback: Callable, player: Player) -> None:
        backgroundUrl = None
        tileMapUrl = ":resources:Maps/Tests.tmx"
        super().__init__(background_url=backgroundUrl, tilemap_url=tileMapUrl)
        self.window.set_mouse_visible(False)

        self.callback = callback

        self.player = player  # Defino el personaje
        self.gui_camera = arcade.Camera2D()

        self.keys_pressed: set = set()
        # Flag para actualizaciones selectivas del inventario
        self.inventory_dirty = True
        # Hash para detectar cambios en el inventario
        self.last_inventory_hash = None
        self.mineral_active: Mineral | None
        self.mineral_interact_time: float = 0.0
        self._chache_update_timer: float = 0.0
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
        self.player_sprites: arcade.SpriteList = arcade.SpriteList()
        self.background_sprites: arcade.SpriteList = arcade.SpriteList()
        self.inventory_sprites: arcade.SpriteList = arcade.SpriteList()
        self.items_inventory: arcade.SpriteList = arcade.SpriteList()
        self.inventory_texts: list[arcade.Text] = []
        self.setup_inventory_containers()

    def setup_inventory_containers(self) -> None:
        """Agrego los contenedores a la lista del inventario"""
        CONTAINER_SIZE = 50
        ITEMS_INIT = Constants.PlayerConfig.PLAYER_INVENTORY_POSITION
        positions = [(ITEMS_INIT[0] + 60 * i, ITEMS_INIT[1]) for i in range(5)]
        add_containers_to_list(
            positions, self.inventory_sprites, container_size=CONTAINER_SIZE
        )

    def setup_player(self) -> None:
        player_data = DataManager.game_data["player"]
        self.player.sprite.center_x = player_data["position"]["center_x"]
        self.player.sprite.center_y = player_data["position"]["center_y"]
        self.player.inventory = player_data["inventory"]
        self.player.setup()
        self.player_sprites.append(self.player.sprite)
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

    def load_mineral_layer(self) -> arcade.SpriteList:
        if "Minerales" not in self.tilemap.object_lists:
            return arcade.SpriteList()

        temp_layer = self.tilemap.object_lists["Minerales"]
        temp_list = arcade.SpriteList()
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

    def on_draw(self) -> bool | None:
        # Función que se llama cada vez que se dibuja la escena
        self.clear()  # limpia la pantalla
        self.camera.use()
        self.scene.draw(pixelated=True)  # dibuja la escena
        self.player_sprites.draw(pixelated=True)  # dibuja el personaje
        self.background_sprites.draw(pixelated=True)
        self.minerals_layer.draw(pixelated=True)
        self.player.sprite.draw_hit_box(color=arcade.color.RED, line_thickness=2)
        for sprite in self.interact_objects:
            sprite.draw_hit_box(color=arcade.color.GREEN, line_thickness=2)

        self.gui_camera.use()
        self.inventory_sprites.draw(pixelated=True)
        self.items_inventory.draw(pixelated=True)
        for text in self.inventory_texts:
            text.draw()

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
                y=container.center_y - (container.height / 2 + 15),
                anchor_x="center",
                anchor_y="baseline",
            )
            self.inventory_texts.append(new_text)

    def update_nearby_cache(self, delta_time: float):
        global _nearby_objects_cache
        self._chache_update_timer += delta_time
        if self._chache_update_timer >= 0.5:
            self._chache_update_timer = 0.0
            _nearby_objects_cache["interact"] = []
            _nearby_objects_cache["mineral"] = []

            for obj in self.interact_objects:
                if is_near_to_sprite(self.player.sprite, obj, tolerance=80):
                    _nearby_objects_cache["interact"].append(obj)

            for obj in self.minerals_layer:
                if is_near_to_sprite(self.player.sprite, obj, tolerance=100):
                    _nearby_objects_cache["mineral"].append(obj)
            print(_nearby_objects_cache)

    def get_screenshot(self):
        # Borro la lista de keys activas para que no se siga moviendo al volver a la escena
        self.keys_pressed.clear()
        self.player.update_state(-arcade.key.W)
        # Limpio la pantalla y dibujo solo el mundo para que no aparezcan los textos
        self.clear()
        self.camera.use()
        self.scene.draw(pixelated=True)
        self.player_sprites.draw(pixelated=True)
        self.background_sprites.draw(pixelated=True)
        self.minerals_layer.draw(pixelated=True)

        screenshot = arcade.get_image()
        return screenshot

    def pause_game(self) -> None:
        def change_to_menu() -> None:
            self.store_player_data()
            self.callback(Constants.SignalCodes.CHANGE_VIEW, "MENU")

        new_scene = Pause(
            previus_scene=self,
            background_image=self.get_screenshot(),
            callback=change_to_menu,
        )
        self.window.show_view(new_scene)

    def open_chest(self, chestId: str) -> None:
        new_scene = Chest(
            chestId=chestId,
            player=self.player,
            previusScene=self,
            background_image=self.get_screenshot(),
        )
        self.window.show_view(new_scene)

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.SPACE:
            self.store_player_data()
            self.callback(Constants.SignalCodes.CHANGE_VIEW, "MENU")
            return True

        if symbol == arcade.key.E:
            return self.handleInteractions()

        if symbol == arcade.key.ESCAPE:
            self.pause_game()
            return True

        self.keys_pressed.add(symbol)
        return None

    def handleInteractions(self):
        global _nearby_objects_cache
        interact_list = _nearby_objects_cache["interact"]
        for interact_obj in interact_list:
            if is_near_to_sprite(self.player.sprite, interact_obj, tolerance=50):
                return self.process_object_interaction(interact_obj)

        mineral_list = _nearby_objects_cache["mineral"]
        for mineral in mineral_list:
            if is_near_to_sprite(self.player.sprite, mineral, tolerance=35):
                self.mineral_interact_time = 0.6
                self.mineral_active = mineral
                return self.process_mineral_interaction(mineral)

        return False

    def store_player_data(self) -> None:
        playerData: PlayerData = {
            "Position": {
                "center_x": self.player.sprite.center_x,
                "center_y": self.player.sprite.center_y,
            },
            "Inventory": self.player.inventory,
        }
        DataManager.storeGameData(playerData, "TEST")

    def process_object_interaction(self, interact_obj: arcade.Sprite) -> bool:
        """Procesa la interaccion con un objeto"""
        object_name = interact_obj.name.lower()
        if object_name == "door":
            # Cambio de escena y guardo los datos actuales
            self.store_player_data()
            self.callback(Constants.SignalCodes.CHANGE_VIEW, "MENU")
            return True
        if "chest" in object_name:
            self.open_chest(chestId=object_name)
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
        self.player.update_state(-symbol)

    def on_update(self, delta_time: float) -> bool | None:
        self.player.update_animation(delta_time)
        lastPosition = self.player.sprite.center_x, self.player.sprite.center_y
        self.player.update_position()
        self.update_inventory_display()
        self.update_nearby_cache(delta_time)

        # Detección de colisiones
        if self.check_collision():
            self.player.sprite.center_x, self.player.sprite.center_y = lastPosition

        for key in self.keys_pressed:
            self.player.update_state(key)

        self.camera.position = arcade.math.lerp_2d(
            self.camera.position, self.player.sprite.position, 0.50
        )

        if self.mineral_interact_time > 0 and self.mineral_active:
            self.mineral_active.update_flash(delta_time)
            self.mineral_interact_time -= delta_time

            if self.mineral_interact_time <= 0:
                self.mineral_active = None

    def check_collision(self) -> bool:
        """Función para detectar si hay colisiones"""
        physicalCollisions = arcade.check_for_collision_with_lists(
            self.player.sprite, self._collision_list
        )
        if physicalCollisions:
            return True
        # Colisiones con cosas interactuables
        for spriteList in self.interact_list:
            for sprite in spriteList:
                if arcade.check_for_collision(self.player.sprite, sprite):
                    # No bloquea el movimiento, pero si registra la colisión
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

        del self.player_sprites
        del self.background_sprites
        del self.inventory_sprites
        del self.items_inventory
        del self.inventory_texts
