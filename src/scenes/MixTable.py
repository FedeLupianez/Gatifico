import arcade
import arcade.gui
from scenes.View import View
from characters.Player import Player
from DataManager import dataManager
from typing import Callable, Dict, Literal
from Constants import SignalCodes

# Cargo los datos de los sprites de los minerales
MineralsResources: Dict[
    str,
    Dict[
        Literal["big", "mid", "small", "item"],
        Dict[Literal["path", "touches"], str | int],
    ],
] = dataManager.loadData("Minerals.json")

# En esta linea se cargarían las combinaciones posibles entre minerales
# MineralsCombinations: Dict[str, str]=dataManager.loadData("Combinations.json")

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

        # cosas de la UI
        self.UIManager = arcade.gui.UIManager(self.window)
        self.UIManager.enable()

        self.UIAnchorLayout = arcade.gui.UIAnchorLayout()
        self.UIManager.add(self.UIAnchorLayout)

        # Init de la clase
        self.callback = callback
        self.items: dict = player.getInventory() or {"rubi": 4, "rock": 3}
        self.inventoryItems: list[tuple[str, int]] = []
        self.containerList: list[arcade.Rect] = []
        self.itemPlacements: list[arcade.Rect] = []

        # Flags
        self.is_mouse_active: bool = False
        self.spriteToMove = None

    def _load_items_placements(self) -> None:
        for x, y in MIXING_ITEMS_POSITIONS:
            tempSprite = arcade.SpriteSolidColor(
                width=CONTAINER_SIZE,
                height=CONTAINER_SIZE,
                center_x=x,
                center_y=y,
                color=arcade.color.GRAY,
            )
            tempSprite.type = "item_placement"
            tempSprite.item_placed = ""
            self.spriteList.append(tempSprite)

    def _load_inventory(self) -> None:
        """
        Carga los items del inventario del personaje a las listas de la clase,
        con ello también genera los sprtes de los minerales y los containers
        """
        for index, ((item, quantity), (x, y)) in enumerate(
            zip(self.items.items(), ITEMS_POSITIONS)
        ):
            container = arcade.Rect(
                left=0,
                right=0,
                bottom=0,
                top=0,
                width=CONTAINER_SIZE,
                height=CONTAINER_SIZE,
                x=x - CONTAINER_SIZE,
                y=y + CONTAINER_SIZE,
            )
            path: str = str(MineralsResources[item]["item"]["path"])
            mineral_sprite = arcade.Sprite(path, scale=3)

            # Guardo el indice de su container para después volverlo a su lugar
            mineral_sprite.container_index = index
            mineral_sprite.name = item
            mineral_sprite.center_x, mineral_sprite.center_y = container.center
            # Agregando lo generado a las listas
            self.inventoryItems.append((item, quantity))
            self.containerList.append(container)
            self.inventorySrites.append(mineral_sprite)

    def on_show_view(self) -> None:
        self._load_items_placements()
        self._load_inventory()
        super().on_show_view()

    def on_draw(self):
        self.clear()  # limpia la pantalla
        self.camera.use()
        self.spriteList.draw()

        for containerIndex, ((name, quantity), sprite) in enumerate(
            zip(self.inventoryItems, self.inventorySrites)
        ):
            container = self.containerList[containerIndex]
            arcade.draw_lbwh_rectangle_filled(
                left=container.x - CONTAINER_SIZE / 2,
                bottom=container.y - CONTAINER_SIZE / 2,
                width=CONTAINER_SIZE,
                height=CONTAINER_SIZE,
                color=arcade.color.DARK_GRAY,
            )
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
            if sprites:
                self.spriteToMove = sprites[-1]

    def on_mouse_release(
        self, x: int, y: int, button: int, modifiers: int
    ) -> bool | None:
        if button == arcade.MOUSE_BUTTON_LEFT and self.is_mouse_active:
            self.is_mouse_active = False  # desactivo el click
            if not self.spriteToMove:
                return

            isPlaced: list[arcade.Sprite] = arcade.check_for_collision_with_list(
                self.spriteToMove, self.spriteList
            )
            if isPlaced and isPlaced[0].type == "item_placement":
                self.spriteToMove.center_x = isPlaced[0].center_x
                self.spriteToMove.center_y = isPlaced[0].center_y
                isPlaced[0].item_placed = self.spriteToMove.name
                print(isPlaced[0].item_placed)
            else:
                index = (
                    self.spriteToMove.container_index
                )  # obtengo el indice del contenedor al que pertenece
                # vuelvo el sprite a su posición original
                self.spriteToMove.center_x = self.containerList[index].center_x
                self.spriteToMove.center_y = self.containerList[index].center_y
            self.spriteToMove = None  # Pongo que no hay nngún sprite qe mover

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> bool | None:
        if self.spriteToMove:
            # Cambio la posición del sprite a la del mouse
            self.spriteToMove.center_x = x
            self.spriteToMove.center_y = y
