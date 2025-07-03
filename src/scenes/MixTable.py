import arcade
import arcade.gui
from scenes.View import View
from characters.Player import Player
import DataManager
from typing import Callable, Dict, Literal
from Constants import SignalCodes

# Cargo los datos de los sprites de los minerales
MineralsResources: Dict[
    str,
    Dict[
        Literal["big", "mid", "small", "item"],
        Dict[Literal["path", "touches"], str | int],
    ],
] = DataManager.loadData("Minerals.json")

Combinations: Dict[str, Dict[str, str]] = DataManager.loadData("CombinationsTest.json")

# En esta linea se cargarían las combinaciones posibles entre minerales

# centros de los contenedores
ITEMS_POSITIONS: list[tuple[int, int]] = [(100, 100), (175, 100), (250, 100)]
MIXING_ITEMS_POSITIONS: list[tuple[int, int]] = [(300, 300), (400, 300)]
CONTAINER_SIZE = 50


class MixTable(View):
    def __init__(self, callback: Callable[[int, str], None], player: Player):
        backgroundUrl = ":resources:Background/Texture/TX Plant.png"
        super().__init__(backgroundUrl=backgroundUrl, tileMapUrl=None)

        # Configuraciones de cámara
        self.window.set_mouse_visible(True)
        self.camera.zoom = 1

        # Listas de sprites
        self.spriteList = arcade.SpriteList()
        self.inventorySrites = arcade.SpriteList()
        self.itemPlacements: arcade.SpriteList = arcade.SpriteList()

        # cosas de la UI
        self.UIManager = arcade.gui.UIManager(self.window)
        self.UIManager.enable()

        self.UIAnchorLayout = arcade.gui.UIAnchorLayout()
        self.UIManager.add(self.UIAnchorLayout)

        # Init de la clase
        self.callback = callback
        self.items: dict = player.getInventory() or {"rubi": 4, "rock": 3}
        self.inventoryItems: list[tuple[str, int]] = []
        self.resultPlace: arcade.SpriteSolidColor

        # Flags
        self.is_mouse_active: bool = False
        self.spriteToMove = None

    def _load_items_placements(self) -> None:
        index = 0
        for x, y in ITEMS_POSITIONS:
            tempSprite = arcade.SpriteSolidColor(
                width=CONTAINER_SIZE,
                height=CONTAINER_SIZE,
                center_x=x,
                center_y=y,
                color=arcade.color.GRAY,
            )
            tempSprite.item_placed = ""
            tempSprite.index = index
            self.itemPlacements.append(tempSprite)
            index += 1

        for x, y in MIXING_ITEMS_POSITIONS:
            tempSprite = arcade.SpriteSolidColor(
                width=CONTAINER_SIZE,
                height=CONTAINER_SIZE,
                center_x=x,
                center_y=y,
                color=arcade.color.GRAY,
            )
            tempSprite.item_placed = ""
            tempSprite.index = index
            self.itemPlacements.append(tempSprite)
            index += 1
        self.resultPlace = arcade.SpriteSolidColor(
            width=CONTAINER_SIZE,
            height=CONTAINER_SIZE,
            center_x=MIXING_ITEMS_POSITIONS[-1][0] + 100,
            center_y=MIXING_ITEMS_POSITIONS[-1][1],
        )
        self.resultPlace.index = index
        self.resultPlace.item_placed = ""
        self.itemPlacements.append(self.resultPlace)
        del index

    def _load_inventory(self) -> None:
        """
        Carga los items del inventario del personaje a las listas de la clase,
        con ello también genera los sprtes de los minerales y los containers
        """
        for index, (item, quantity) in enumerate(self.items.items()):
            container = self.itemPlacements[index]
            path: str = str(MineralsResources[item]["item"]["path"])
            mineral_sprite = arcade.Sprite(
                path, scale=3, center_x=container.center_x, center_y=container.center_y
            )
            # Guardo el indice de su container para después volverlo a su lugar
            mineral_sprite.container_index = container.index
            mineral_sprite.name = item
            # Agregando lo generado a las listas
            self.inventoryItems.append((item, quantity))
            self.inventorySrites.append(mineral_sprite)

    def _load_item_result(self):
        place_1, place_2 = self.itemPlacements[-3:-1]
        item_1 = place_1.item_placed
        item_2 = place_2.item_placed

        if not (item_1 and item_2):
            return

        firt_item_combinations = Combinations.get(item_1, None)
        if not firt_item_combinations:
            return

        result = firt_item_combinations.get(item_2, None)
        if not result:
            return

        path = str(MineralsResources[result]["item"]["path"])
        tempSprite = arcade.Sprite(
            path,
            center_x=self.resultPlace.center_x,
            center_y=self.resultPlace.center_y,
            scale=3,
        )
        tempSprite.container_index = self.resultPlace.index
        tempSprite.name = result
        self.inventorySrites.append(tempSprite)

    def on_show_view(self) -> None:
        self._load_items_placements()
        self._load_inventory()
        super().on_show_view()

    def on_draw(self):
        self.clear()  # limpia la pantalla
        self.camera.use()
        self.spriteList.draw(pixelated=True)

        for (name, quantity), sprite in zip(self.inventoryItems, self.inventorySrites):
            x = sprite.center_x
            y = sprite.center_y - sprite.height / 2 - 5
            text = arcade.Text(
                text=f"{name.capitalize()}x{quantity}",
                x=x,
                y=y,
                anchor_x="center",
                anchor_y="top",
            )
            text.draw()

        self.itemPlacements.draw(pixelated=True)
        self.inventorySrites.draw(pixelated=True)
        self.UIManager.draw(pixelated=True)

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.SPACE:
            self.callback(SignalCodes.CHANGE_VIEW, "MENU")

    def on_mouse_press(
        self, x: int, y: int, button: int, modifiers: int
    ) -> bool | None:
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.is_mouse_active = True
            sprites = arcade.get_sprites_at_point((x, y), self.inventorySrites)

            if not sprites:
                self.is_mouse_active = False
                return
            self.spriteToMove = sprites[-1]

    def on_mouse_release(
        self, x: int, y: int, button: int, modifiers: int
    ) -> bool | None:
        if button == arcade.MOUSE_BUTTON_LEFT and self.is_mouse_active:
            self.is_mouse_active = False  # desactivo el click
            if not self.spriteToMove:
                return

            isPlaced: list[arcade.Sprite] = arcade.check_for_collision_with_list(
                self.spriteToMove, self.itemPlacements
            )

            if isPlaced:
                self.spriteToMove.center_x = isPlaced[0].center_x
                self.spriteToMove.center_y = isPlaced[0].center_y
                isPlaced[0].item_placed = self.spriteToMove.name
                # Reseteo el contenido del antiguo contenedor
                self.itemPlacements[self.spriteToMove.container_index].item_placed = ""
                self.spriteToMove.container_index = isPlaced[0].index
                self._load_item_result()
            else:
                index = (
                    self.spriteToMove.container_index
                )  # obtengo el indice del contenedor al que pertenece
                # vuelvo el sprite a su posición original
                self.spriteToMove.center_x = self.itemPlacements[index].center_x
                self.spriteToMove.center_y = self.itemPlacements[index].center_y
            self.spriteToMove = None  # Pongo que no hay nngún sprite qe mover

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> bool | None:
        if self.spriteToMove:
            # Cambio la posición del sprite a la del mouse
            self.spriteToMove.center_x = x
            self.spriteToMove.center_y = y
