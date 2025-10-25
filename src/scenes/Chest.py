import arcade
import Constants
import DataManager
from characters.Player import Player
from .View import View

from items.Container import Container
from items.Item import Item
from .utils import add_containers_to_list, apply_filter
from DataManager import ChestsData, chests_data, get_sound, get_path

CONTAINER_SIZE = 50
ITEMS_INIT = (550, 300)
CONTAINER_UI_SCALE = 2.5
DISTANCE_BETWEEN_CONTAINERS = 57.5
GAP_ITEM_TEXT = 12


class Chest(View):
    def __init__(self, chest_id: str, previusScene: View) -> None:
        super().__init__(background_url=None, tilemap_url=None)
        background_image = previusScene.get_screenshot()

        # Le pongo filtro oscuro al fondo
        self.background_image = arcade.texture.Texture.create_empty(
            "pause_bg", size=(background_image.width, background_image.height)
        )
        self.background_image.image = apply_filter(
            background_image, Constants.Filter.DARK
        )

        self.window.set_mouse_visible(True)
        self.item_sprites: arcade.SpriteList = arcade.SpriteList()
        self.container_sprites = arcade.SpriteList()
        self.container_player_sprites = arcade.SpriteList()
        # SpriteList de los contenedores de ui
        self.container_ui_sprites: arcade.SpriteList = arcade.SpriteList()
        self.player_inventory_sprite: arcade.Sprite = arcade.Sprite(
            get_path("inventory_tools.png"), scale=3
        )
        self.player_inventory_sprite.scale_y = 3.2
        self.item_texts: list[arcade.Text] = []
        self.next_item_id: int = 0
        self.id: str = chest_id
        self.player = Player()
        self.is_mouse_active = False
        self.item_to_move: Item | None = None
        self.previus_scene = previusScene
        self.content: ChestsData = chests_data.get(self.id, [])

        self.player_container_index = 0
        self.background_rect = arcade.SpriteSolidColor(
            width=int(
                Constants.Game.SCREEN_CENTER_X + (Constants.Game.SCREEN_CENTER_X / 3)
            ),
            height=int(Constants.Game.SCREEN_CENTER_Y),
            center_x=self.window.center_x,
            center_y=self.window.center_y,
        )
        self._setup()
        arcade.play_sound(get_sound("open_chest.mp3"), volume=0.3)

    def _setup_containers(self) -> None:
        positions_1 = [
            (ITEMS_INIT[0] + DISTANCE_BETWEEN_CONTAINERS * i, ITEMS_INIT[1])
            for i in range(4)
        ]
        positions_2 = [
            (
                ITEMS_INIT[0] + DISTANCE_BETWEEN_CONTAINERS * i,
                ITEMS_INIT[1] + DISTANCE_BETWEEN_CONTAINERS,
            )
            for i in range(4)
        ]
        player_init_pos = Constants.PlayerConfig.INVENTORY_POSITION
        player_items = [
            (
                player_init_pos[0] + DISTANCE_BETWEEN_CONTAINERS * i,
                player_init_pos[1] + 5,
            )
            for i in range(Constants.PlayerConfig.INVENTORY_SELLS)
        ]
        add_containers_to_list(
            point_list=positions_1,
            list_to_add=self.container_sprites,
            container_size=CONTAINER_SIZE,
            container_type="chest",
            last_id=0,
        )
        add_containers_to_list(
            point_list=positions_2,
            list_to_add=self.container_sprites,
            container_size=CONTAINER_SIZE,
            container_type="chest",
            last_id=len(self.container_sprites),
        )
        self.player_container_index = len(self.container_sprites)
        add_containers_to_list(
            point_list=player_items,
            list_to_add=self.container_player_sprites,
            container_size=CONTAINER_SIZE,
            container_type="inventory",
            last_id=len(self.container_sprites),
        )

        for i in range(len(positions_1)):
            temp = arcade.Sprite(
                get_path("inventory_container.png"), scale=CONTAINER_UI_SCALE
            )
            temp.center_x = positions_1[i][0]
            temp.center_y = positions_1[i][1]
            self.container_ui_sprites.append(temp)

        for i in range(len(positions_2)):
            temp = arcade.Sprite(
                get_path("inventory_container.png"), scale=CONTAINER_UI_SCALE
            )
            temp.center_x = positions_2[i][0]
            temp.center_y = positions_2[i][1]
            self.container_ui_sprites.append(temp)
        self.player_inventory_sprite.center_x = self._half_w
        self.player_inventory_sprite.center_y = player_init_pos[1]
        self.container_ui_sprites.append(self.player_inventory_sprite)

    def _find_item_with_id(
        self, id: int, list_to_find: arcade.SpriteList | list, sprite_index: int = 0
    ):
        if sprite_index == len(list_to_find):
            return None
        sprite = list_to_find[sprite_index]
        if sprite.id == id:
            return sprite
        return self._find_item_with_id(id, list_to_find, sprite_index + 1)

    def _find_item_with_containerId(
        self, container_id: int, sprite_index: int = 0
    ) -> Item | None:
        if sprite_index == len(self.item_sprites):
            return None
        sprite: Item = self.item_sprites[sprite_index]
        if sprite.container_id == container_id:
            return sprite
        return self._find_item_with_containerId(container_id, sprite_index + 1)

    def _update_texts_position(self) -> None:
        for item in self.item_sprites:
            actual_text: arcade.Text | None = self._find_item_with_id(
                item.id, self.item_texts
            )
            if not (actual_text):
                continue
            actual_text.x = item.center_x
            actual_text.y = item.center_y - ((item.height * 0.5) + GAP_ITEM_TEXT)

    def _create_item_text(self, item: Item) -> arcade.Text:
        content = f"{item.quantity}"
        text_sprite = arcade.Text(
            text=content,
            font_size=9,
            x=item.center_x,
            y=item.center_y - ((item.height * 0.5) + GAP_ITEM_TEXT),
            anchor_x="center",
            anchor_y="baseline",
            color=arcade.color.BLACK,
            font_name=Constants.Assets.FONT_NAME,
        )
        text_sprite.id = item.id
        return text_sprite

    def _generate_item_sprites(self):
        for item, quantity, index in self.content:
            container: Container = self.container_sprites[index]
            new_item = Item(name=item, quantity=quantity, scale=2)
            new_item.id = self.next_item_id
            self.next_item_id += 1
            new_item.change_container(container.id)
            new_item.change_position(container.center_x, container.center_y)
            container.item_placed = True
            self.item_texts.append(self._create_item_text(new_item))
            self.item_sprites.append(new_item)

        for item, quantity, index in self.player.get_inventory():
            container: Container = self.container_player_sprites[index]
            new_item = Item(name=item, quantity=quantity, scale=2)
            new_item.id = self.next_item_id
            self.next_item_id += 1
            new_item.change_container(container.id)
            new_item.change_position(container.center_x, container.center_y)
            container.item_placed = True
            self.item_texts.append(self._create_item_text(new_item))
            self.item_sprites.append(new_item)

    def _sync_item_text(self) -> None:
        for text_sprite in self.item_texts:
            item = self._find_item_with_id(text_sprite.id, self.item_sprites)
            if item is None:
                continue
            expected = f"{item.quantity}"
            if text_sprite.text != expected:
                text_sprite.text = expected
            text_sprite.anchor_x = "center"
            text_sprite.anchor_y = "baseline"
        self._update_texts_position()

    def _reset_sprite_position(self, sprite: Item) -> None:
        if sprite.container_id < self.player_container_index:
            original_container = self._find_item_with_id(
                sprite.container_id, self.container_sprites
            )
        else:
            original_container = self._find_item_with_id(
                sprite.container_id, self.container_player_sprites
            )

        assert original_container is not None
        sprite.change_position(original_container.center_x, original_container.center_y)

    def _move_sprite_to_container(self, sprite: Item, container: Container) -> None:
        sprite.change_position(container.center_x, container.center_y)
        sprite.change_container(container.id)

    def _setup(self) -> None:
        self._setup_containers()
        self._generate_item_sprites()

    def on_update(self, delta_time: float) -> bool | None:
        self._sync_item_text()
        self._update_texts_position()

    def on_draw(self) -> None:
        self.clear()
        self.camera.use()
        if self.background_image:
            arcade.draw_texture_rect(
                self.background_image,
                rect=arcade.rect.Rect(
                    left=0,
                    right=0,
                    top=0,
                    bottom=0,
                    width=Constants.Game.SCREEN_WIDTH,
                    height=Constants.Game.SCREEN_HEIGHT,
                    x=Constants.Game.SCREEN_WIDTH * 0.5,
                    y=Constants.Game.SCREEN_HEIGHT * 0.5,
                ),
                pixelated=True,
            )
        self.container_ui_sprites.draw(pixelated=True)
        self.item_sprites.draw(pixelated=True)
        self.ui_sprites.draw(pixelated=True)
        for text in self.item_texts:
            text.draw()
        if self._item_mouse_text.text:
            self._item_mouse_text.draw()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.is_mouse_active = True
            sprites = arcade.get_sprites_at_point((x, y), self.item_sprites)
            self.item_to_move = sprites[-1] if sprites else None

    def on_mouse_release(
        self, x: int, y: int, button: int, modifiers: int
    ) -> bool | None:
        if button != arcade.MOUSE_BUTTON_LEFT or not self.is_mouse_active:
            return

        self.is_mouse_active = False  # desactivo el click

        if not self.item_to_move:
            return

        chest_container_collisions: list[Container] = (
            arcade.check_for_collision_with_list(
                self.item_to_move, self.container_sprites
            )
        )
        player_containers_collisions: list[Container] = (
            arcade.check_for_collision_with_list(
                self.item_to_move, self.container_player_sprites
            )
        )

        if not chest_container_collisions and not player_containers_collisions:
            self._reset_sprite_position(self.item_to_move)
            self.item_to_move = None
            return
        new_container: Container
        last_container_id: int = self.item_to_move.container_id
        old_container: Container = self._find_item_with_id(
            last_container_id, self.container_sprites
        ) or self._find_item_with_id(last_container_id, self.container_player_sprites)

        if chest_container_collisions and not player_containers_collisions:
            new_container: Container = chest_container_collisions[0]
        else:
            new_container: Container = player_containers_collisions[0]

        if new_container.id == old_container.id:
            self._reset_sprite_position(self.item_to_move)
            self.item_to_move = None
            return

        if not (new_container.item_placed):
            self._move_sprite_to_container(self.item_to_move, new_container)
            old_container.item_placed = False
            new_container.item_placed = True
        else:
            item: Item = self._find_item_with_containerId(new_container.id)
            if item.name == self.item_to_move.name:
                text: arcade.Text = self._find_item_with_id(item.id, self.item_texts)
                self._move_sprite_to_container(self.item_to_move, new_container)
                old_container.item_placed = False
                new_container.item_placed = True
                self.item_to_move.quantity += item.quantity
                self.item_sprites.remove(item)
                self.item_texts.remove(text)

            self._reset_sprite_position(self.item_to_move)

        self.item_to_move = None  # Pongo que no hay ningún sprite que mover

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> bool | None:
        if self.item_to_move:
            # Cambio la posición del sprite a la del mouse
            self.item_to_move.change_position(x, y)
        self.item_hover(mouse_pos=(x, y), items_list=self.item_sprites)

    def updateInventories(self):
        # Acá voy a actualizar los inventarios tanto del cofre como del personaje
        # Esta parte es del cofre
        new_chest_inventory = []
        for i in range(len(self.container_sprites)):
            container = self.container_sprites[i]
            item: Item | None = self._find_item_with_containerId(container.id)
            if item:
                # Name, quantity, index
                new_chest_inventory.append((item.name, item.quantity, i))

        self.content = new_chest_inventory
        # Ahora voy a actualizar el inventario del jugador
        new_player_inventory = []
        for i in range(len(self.container_player_sprites)):
            container = self.container_player_sprites[i]
            item: Item | None = self._find_item_with_containerId(container.id)
            if item:
                new_player_inventory.append((item.name, item.quantity, i))
        self.player.inventory = new_player_inventory
        DataManager.store_chest_data(self.content, self.id)

    def clean_up(self):
        # Limpio todas las listas de sprites
        self.item_sprites = arcade.SpriteList()
        self.container_sprites = arcade.SpriteList()
        self.container_player_sprites = arcade.SpriteList()
        self.item_texts = []
        # Elimino la textura del fondo
        del self.background_image
        # Elimno las referencias directas
        self.item_to_move = None
        self.player_inventory = None
        self.window.set_mouse_visible(False)

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.ESCAPE:
            self.updateInventories()
            self.clean_up()
            self.window.show_view(self.previus_scene)
