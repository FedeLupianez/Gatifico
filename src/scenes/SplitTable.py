import arcade.gui
from items.Container import Container
from items.Item import Item
import arcade
from scenes.View import View
import DataManager
from characters.Player import Player
from scenes.utils import add_containers_to_list, del_references_list, apply_filter
from Constants import Game, Filter


class SplitTable(View):
    RESOURCE = DataManager.loadData("SplitTableResources.json")
    # Centros de los contenedores
    INPUT_POSITION: tuple[int, int] = (350, 450)
    RESULT_INIT_POSITION: tuple[int, int] = (450, 450)
    CONTAINER_SIZE = 50

    ITEMS_INIT: tuple[int, int] = (100, 250)

    def __init__(
        self,
        background_scene: View,
    ) -> None:
        super().__init__(None, None)
        self.window.set_mouse_visible(True)

        background_image = background_scene.get_screenshot()

        self.background_image = arcade.texture.Texture.create_empty(
            "table_bg", size=(background_image.width, background_image.height)
        )

        self.background_image.image = apply_filter(background_image, Filter.DARK)
        self.background_scene = background_scene
        self.background_rect = arcade.rect.Rect(
            left=0,
            right=0,
            top=0,
            bottom=0,
            width=Game.SCREEN_WIDTH,
            height=Game.SCREEN_HEIGHT,
            x=Game.SCREEN_CENTER_X,
            y=Game.SCREEN_CENTER_Y,
        )
        self.rect_table = arcade.rect.Rect(
            left=Game.SCREEN_CENTER_X - (Game.SCREEN_CENTER_X / 3),
            right=Game.SCREEN_CENTER_X + (Game.SCREEN_CENTER_X / 3),
            top=Game.SCREEN_CENTER_Y + (Game.SCREEN_CENTER_Y * 0.5),
            bottom=Game.SCREEN_CENTER_Y - (Game.SCREEN_CENTER_Y * 0.5),
            width=Game.SCREEN_CENTER_X + (Game.SCREEN_CENTER_X / 3),
            height=Game.SCREEN_CENTER_Y,
            x=Game.SCREEN_CENTER_X,
            y=Game.SCREEN_CENTER_Y,
        )

        self.player = Player()
        self.items: dict = self.player.get_inventory() or {
            "rubi": 4,
            "piedra": 3,
            "azufre": 5,
        }
        self.next_item_id: int = 0
        self.camera.zoom = 1
        self.is_mouse_active: bool = False
        self.item_to_move: Item | None = None
        self.UIManager = arcade.gui.UIManager(self.window)
        self.UIManager.enable()
        self.setup()

    def setup(self) -> None:
        self._setup_lists()
        self._setup_containers()
        self._setup_items()
        self.setup_ui()

    def _setup_lists(self) -> None:
        self.item_sprites = arcade.SpriteList()
        self.container_sprites = arcade.SpriteList()
        self.item_texts: list[arcade.Text] = []
        self.input_container: Container
        self.result_containers: list[Container] = []

    def _setup_containers(self) -> None:
        positions = [
            (SplitTable.ITEMS_INIT[0] + 75 * i, SplitTable.ITEMS_INIT[1])
            for i in range(len(self.items))
        ]

        # Centrar los containers con la pantalla :
        # centro de la pantalla
        cant_containers = len(positions)
        screen_center_x = self.window.width * 0.5
        mid_container = int(cant_containers * 0.5)
        positions[mid_container] = (screen_center_x, SplitTable.ITEMS_INIT[1])

        for i in range(mid_container - 1, -1, -1):
            last_pos = positions[i + 1]
            positions[i] = (last_pos[0] - 75, SplitTable.ITEMS_INIT[1])

        for i in range(mid_container + 1, cant_containers):
            last_pos = positions[i - 1]
            positions[i] = (last_pos[0] + 75, SplitTable.ITEMS_INIT[1])

        add_containers_to_list(
            point_list=positions,
            list_to_add=self.container_sprites,
            container_size=SplitTable.CONTAINER_SIZE,
        )
        self.input_container = Container(
            width=SplitTable.CONTAINER_SIZE,
            height=SplitTable.CONTAINER_SIZE,
            center_x=SplitTable.INPUT_POSITION[0],
            center_y=SplitTable.INPUT_POSITION[1],
        )
        self.input_container.id = len(self.container_sprites)
        self.container_sprites.append(self.input_container)

    def _setup_items(self) -> None:
        for index, (name, quantity) in enumerate(self.items.items()):
            container: Container = self.container_sprites[index]
            container.item_placed = True
            new_item = Item(name=name, quantity=quantity, scale=3)
            new_item.id = self.next_item_id
            self.next_item_id += 1
            new_item.change_container(container.id)
            new_item.change_position(container.center_x, container.center_y)
            self.item_texts.append(self._create_item_text(new_item))
            self.item_sprites.append(new_item)

    def setup_ui(self) -> None:
        input_x, input_y = SplitTable.INPUT_POSITION
        self.mixButton = arcade.gui.UIFlatButton(
            x=input_x + SplitTable.CONTAINER_SIZE,
            y=input_y - SplitTable.CONTAINER_SIZE * 2,
            text="Separar",
        )

        @self.mixButton.event("on_click")
        def on_click(event):
            self.load_result()

        self.UIManager.add(self.mixButton)

    def _create_item_text(self, item: Item, fontSize: int = 11) -> arcade.Text:
        content = f"{item.name} x {item.quantity}"
        text_sprite = arcade.Text(
            text=content,
            font_size=fontSize,
            x=item.center_x,
            y=item.center_y - ((item.height * 0.5) + 15),
            anchor_x="center",
            anchor_y="baseline",
        )
        text_sprite.id = item.id
        return text_sprite

    def _reset_sprite_position(self, sprite: Item) -> None:
        original_container = self.container_sprites[sprite.container_id]
        sprite.change_position(original_container.center_x, original_container.center_y)

    def _move_sprite_to_container(self, sprite: Item, container: Container) -> None:
        sprite.change_position(container.center_x, container.center_y)
        sprite.change_container(container.id)

    def _find_element(self, list_to_find, attr: str, target):
        """
        Función para buscar un elemento de una lista que cumpla con un requisito
        Args:
            func (Callable): Función que devuelve True si el elemento cumple con el requisito
            list_to_find (list): Lista de elementos donde buscar
        """
        result = list(filter(self.item_contains_attr(attr, target), list_to_find))
        if not result:
            return
        return result[0]

    def item_contains_attr(self, attr: str, target):
        def is_item(sprite):
            if hasattr(sprite, attr):
                return getattr(sprite, attr) == target
            else:
                return False

        return is_item

    def _sync_item_text(self) -> None:
        for text_sprite in self.item_texts:
            item = self._find_element(
                self.item_sprites, attr="id", target=text_sprite.id
            )
            if not item:
                continue
            expected = f"{item.name} x {item.quantity}"
            if text_sprite.text != expected:
                text_sprite.text = expected

    def _update_text_position(self) -> None:
        for item in self.item_sprites:
            actual_text = self._find_element(self.item_texts, attr="id", target=item.id)
            if not (actual_text):
                return
            actual_text.x = item.center_x
            actual_text.y = item.center_y - (item.height * 0.5 + 15)

    def create_result_containers(self, containers_cant: int) -> None:
        # Creo los contenedores faltantes :
        if len(self.result_containers) < containers_cant:
            for _ in range(containers_cant):
                last_container: Container | None = None
                if len(self.result_containers) > 0:
                    last_container = self.result_containers[-1]
                center_x = 0
                if last_container:
                    center_x = last_container.center_x + SplitTable.CONTAINER_SIZE + 25
                else:
                    center_x = (
                        SplitTable.INPUT_POSITION[0] + SplitTable.CONTAINER_SIZE + 25
                    )

                new_container = Container(
                    width=SplitTable.CONTAINER_SIZE,
                    height=SplitTable.CONTAINER_SIZE,
                    center_x=center_x,
                    center_y=SplitTable.INPUT_POSITION[1],
                )
                new_container.id = len(self.container_sprites)

                self.result_containers.append(new_container)
                self.container_sprites.append(self.result_containers[-1])

    def load_result(self) -> None:
        input_item: Item | None = self._find_element(
            self.item_sprites, attr="container_id", target=self.input_container.id
        )
        if not input_item:
            return
        print("nombre del item de input : ", input_item.name)

        result = SplitTable.RESOURCE.get(input_item.name, {})
        if not (result):
            return
        print("Resultados : ", result)
        self.create_result_containers(len(result))

        actual_items: list[Item | None] = [
            self._find_element(
                self.item_sprites, attr="container_id", target=container.id
            )
            for container in self.result_containers
        ]
        actual_names: list[str] = [item.name for item in actual_items if item]
        # Cargo los items :
        for index, (name, quantity) in enumerate(result.items()):
            if name in actual_names:
                old_item = actual_items[actual_names.index(name)]
                if old_item:
                    print(f"Cambiando {name} a {old_item.quantity + quantity}")
                    old_item.quantity += quantity
            else:
                container: Container = self.result_containers[index]
                new_item = Item(name=name, quantity=quantity, scale=3)
                new_item.id = self.next_item_id
                new_item.container_id = container.id
                self.next_item_id += 1
                new_item.change_container(container.id)
                new_item.change_position(container.center_x, container.center_y)
                container.item_placed = True
                self.item_texts.append(self._create_item_text(new_item))
                self.item_sprites.append(new_item)
        input_item.quantity -= 1
        if input_item.quantity == 0:
            self.item_sprites.remove(input_item)
            self.item_texts.remove(
                self._find_element(self.item_texts, attr="id", target=input_item.id)
            )
            self.input_container.item_placed = False

    def save_results(self) -> None:
        # Guardo los items generados por el jugador
        # Veo si hay items en las casillas de resultados
        new_inventory: dict[str, int] = {}

        for container in self.container_sprites:
            item = self._find_element(
                self.item_sprites, attr="container_id", target=container.id
            )
            if not item:
                continue
            if not new_inventory.get(item.name):
                new_inventory[item.name] = item.quantity
            else:
                new_inventory[item.name] += item.quantity
        self.player.inventory = new_inventory

    def on_update(self, delta_time: float) -> bool | None:
        self._sync_item_text()
        self._update_text_position()

    def draw_background(self) -> None:
        if self.background_image:
            arcade.draw_texture_rect(
                self.background_image,
                rect=self.background_rect,
                pixelated=True,
            )
        arcade.draw_rect_filled(
            rect=self.rect_table,
            color=arcade.color.PALE_BROWN,
        )

    def on_draw(self) -> None:
        self.clear()
        self.camera.use()
        self.draw_background()
        self.container_sprites.draw(pixelated=True)
        self.item_sprites.draw(pixelated=True)
        for text in self.item_texts:
            text.draw()
        self.UIManager.draw()

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.ESCAPE:
            self.save_results()
            self.clean_up()
            self.window.show_view(self.background_scene)
            del self.background_scene

    def on_mouse_press(
        self, x: int, y: int, button: int, modifiers: int
    ) -> bool | None:
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.is_mouse_active = True
            sprites = arcade.get_sprites_at_point((x, y), self.item_sprites)
            self.item_to_move = sprites[-1] if sprites else None
            if self.item_to_move:
                print(self.item_to_move.id)

    def on_mouse_release(
        self, x: int, y: int, button: int, modifiers: int
    ) -> bool | None:
        if button != arcade.MOUSE_BUTTON_LEFT or not self.is_mouse_active:
            return
        self.is_mouse_active = False
        if not self.item_to_move:
            return
        collisions: list[Container] = arcade.check_for_collision_with_list(
            self.item_to_move, self.container_sprites
        )
        if not collisions:
            self._reset_sprite_position(self.item_to_move)
            self.item_to_move = None
            return

        new_container: Container = collisions[0]
        old_container: Container = self.container_sprites[
            self.item_to_move.container_id
        ]

        if new_container.id == old_container.id:
            self._reset_sprite_position(self.item_to_move)
            self.item_to_move = None
            return

        if not (new_container.item_placed):
            self._move_sprite_to_container(self.item_to_move, new_container)
            old_container.item_placed = False
            new_container.item_placed = True
        else:
            item: Item | None = self._find_element(
                self.item_sprites, attr="container_id", target=new_container.id
            )
            if not (item):
                return
            if item.name == self.item_to_move.name:
                text = self._find_element(self.item_texts, attr="id", target=item.id)
                if not text:
                    return
                self._move_sprite_to_container(self.item_to_move, new_container)
                old_container.item_placed = False
                new_container.item_placed = True
                self.item_to_move.quantity += item.quantity
                self.item_sprites.remove(item)
                self.item_texts.remove(text)
            self._reset_sprite_position(self.item_to_move)
        self.item_to_move = None

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> bool | None:
        if self.item_to_move and self.is_mouse_active:
            # Cambio la posición del sprite a la del mouse
            self.item_to_move.change_position(x, y)

    def clean_up(self) -> None:
        del self.background_image
        del_references_list(self.container_sprites)
        del self.container_sprites
        del_references_list(self.item_sprites)
        del self.item_sprites
        del self.item_texts
        del self.item_to_move
        del self.is_mouse_active
        del self.result_containers
        del self.UIManager
