import arcade
import arcade.gui
from typing import Tuple
from scenes.View import View
import Constants
from characters.Player import Player
from typing import Callable
from minerals.Mineral import Mineral
from DataManager import dataManager

MineralsResources = dataManager.loadData("Minerals.json")


def is_near_to_sprite(
    sprite1: arcade.Sprite, sprite2: arcade.Sprite, tolerance: float = 16.0
) -> bool:
    return arcade.get_distance_between_sprites(sprite1, sprite2) <= tolerance


class Test(View):
    def __init__(self, callback: Callable, player: Player) -> None:
        backgroundUrl = None
        tileMapUrl = ":resources:Maps/Tests.tmx"
        super().__init__(backgroundUrl=backgroundUrl, tileMapUrl=tileMapUrl)
        self.window.set_mouse_visible(False)

        self.uiManager = arcade.gui.UIManager(self.window)
        self.uiManager.enable()

        self.uiAnchorLayout = arcade.gui.UIAnchorLayout()
        self.uiManager.add(self.uiAnchorLayout)

        self.callback = callback

        self.player = player  # Defino el personaje

        self.setupSpriteLists()
        self.setupSceneLayers()
        self.setupPlayer()

        self.keysPressed: set = set()
        self.inventoryEnabled = False

    def setupSpriteLists(self):
        # Listas de Sprites
        self.playerSpritesList: arcade.SpriteList = arcade.SpriteList()
        self.backgroundSpriteList: arcade.SpriteList = arcade.SpriteList()

    def setupPlayer(self) -> None:
        self.player.sprite.center_x = Constants.Game.SCREEN_WIDTH // 2
        self.player.sprite.center_y = Constants.Game.SCREEN_HEIGHT // 2
        self.player.setup()
        self.playerSpritesList.append(self.player.sprite)
        # Camara para seguir al jugador :
        self.camera.zoom = 2.5

    def setupSceneLayers(self) -> None:
        assert self.tileMap is not None
        # Capas de vista :
        self.floor = self.scene["Piso"]
        self.walls = self.scene["Paredes"]
        self.backgroundObjects = self.scene["Objetos"]
        # Capas de colisiones :
        self.collisionSprites = self.loadObjectLayers("Colisiones", self.tileMap)
        self.interactSprites = self.loadObjectLayers("Interactuables", self.tileMap)
        self.mineralsLayer = self.loadMineralLayer()

    def loadMineralLayer(self) -> arcade.SpriteList:
        tempLayer = self.tileMap.object_lists["Minerales"]
        tempList = arcade.SpriteList()

        for obj in tempLayer:
            assert obj.name is not None
            assert obj.properties is not None
            shape: Tuple[
                Tuple[float, float],
                Tuple[float, float],
                Tuple[float, float],
                Tuple[float, float],
            ] = obj.shape

            topLeft, topRight, bottomRight, bottomLeft = shape
            width: float = topRight[0] - topLeft[0]
            height: float = topLeft[1] - bottomLeft[1]
            center_x: float = topLeft[0] + (width) / 2
            center_y: float = bottomLeft[1] + (height) / 2
            size = str(obj.properties.get("size"))

            newObj = Mineral(
                obj.name,
                size,
                center_x=center_x,
                center_y=center_y,
                mineralAttributes=MineralsResources,
            )
            tempList.append(newObj)
        return tempList

    def on_show_view(self) -> None:
        return super().on_show_view()

    def on_draw(self) -> bool | None:
        # Función que se llama cada vez que se dibuja la escena
        self.clear()  # limpia la pantalla
        self.camera.use()
        self.scene.draw(pixelated=True)  # dibuja la escena
        self.playerSpritesList.draw(pixelated=True)  # dibuja el personaje
        self.backgroundSpriteList.draw(pixelated=True)
        self.mineralsLayer.draw(pixelated=True)

        self.uiManager.draw(pixelated=True)

    def showInventory(self):
        self.window.set_mouse_visible(True)
        self.inventoryEnabled = True
        self.uiAnchorLayout.clear()

        background = arcade.load_image(":resources:UI/inventory_background.png")
        texture = arcade.Texture(image=background)

        inventoryBackground = arcade.gui.UIImage(
            center_x=self.window.center_x,
            center_y=self.window.center_y,
            texture=texture,
        )
        self.uiAnchorLayout.add(child=inventoryBackground)

        inventoryGrid = arcade.gui.UIGridLayout(
            column_count=5, row_count=5, horizontal_spacing=5, vertical_spacing=5
        )

        col, row = 0, 4
        for itemName, quantity in self.player.inventory.items():
            label = arcade.gui.UILabel(text=f"{itemName} x {quantity}", font_size=11)
            inventoryGrid.add(column=col, row=row, child=label)
            col += 1
            if col >= 5 and row > 0:
                col = 0
                row -= 1

        inventoryBox = arcade.gui.UIBoxLayout(vertical=True, space_between=10)
        inventoryBox.add(
            arcade.gui.UILabel(text="Inventario", font_size=20, align="center")
        )
        inventoryBox.add(child=inventoryGrid)

        closeButton = arcade.gui.UIFlatButton(text="Cerrar", width=100)

        @closeButton.event("on_click")
        def on_click(event):
            self.closeInventory()

        inventoryBox.add(child=closeButton)
        self.uiAnchorLayout.add(
            child=inventoryBox, anchor_x="center", anchor_y="center"
        )

    def closeInventory(self):
        self.uiAnchorLayout.clear()
        self.uiManager.remove(self.uiAnchorLayout)  # 🔥 Eliminar layout del UIManager
        self.uiAnchorLayout = arcade.gui.UIAnchorLayout()  # 🔁 Crear uno nuevo limpio
        self.uiManager.add(self.uiAnchorLayout)  # ➕ Agregar el nuevo layout
        self.inventoryEnabled = False
        self.window.set_mouse_visible(False)

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.SPACE:
            self.callback(Constants.SignalCodes.CHANGE_VIEW, "MENU")
            return

        if symbol == arcade.key.E:
            if self.handleInteractions():
                return

        if symbol == arcade.key.I:
            if not self.inventoryEnabled:
                self.showInventory()
            else:
                self.closeInventory()
            return

        self.keysPressed.add(symbol)

    def handleInteractions(self):
        for interactObject in self.interactSprites:
            if is_near_to_sprite(self.player.sprite, interactObject, tolerance=40):
                print(interactObject.name)
                if interactObject.name.lower() == "door":
                    self.callback(Constants.SignalCodes.CHANGE_VIEW, "MENU")
                    return True

        for mineral in self.mineralsLayer:
            if is_near_to_sprite(self.player.sprite, mineral, tolerance=35):
                mineral.setup()
                mineral.stateMachine.processState(arcade.key.E)
                self.player.addToInventory(mineral.mineral, 1)

                if mineral.should_removed:
                    mineral.remove_from_sprite_lists()
                return True
        return False

    def on_key_release(self, symbol: int, modifiers: int) -> bool | None:
        self.keysPressed.discard(symbol)
        self.player.updateState(-symbol)

    def on_update(self, delta_time: float) -> bool | None:
        self.player.update_animation(delta_time)
        lastPosition = self.player.sprite.center_x, self.player.sprite.center_y
        self.player.updatePosition()

        # Colisiones físicas solo con capas físicas reales
        collisions = arcade.check_for_collision_with_lists(
            self.player.sprite,
            [
                self.collisionSprites,
                self.walls,
            ],
        )

        # Chequeo manual de colisión "física" con interactuables (sin bloquear interacción)
        for obj in self.interactSprites:
            if arcade.check_for_collision(self.player.sprite, obj):
                collisions.append(obj)
        for mineral in self.mineralsLayer:
            if arcade.check_for_collision(self.player.sprite, mineral):
                collisions.append(mineral)

        if collisions:
            self.player.sprite.center_x, self.player.sprite.center_y = lastPosition

        for key in self.keysPressed:
            self.player.updateState(key)

        self.camera.position = arcade.math.lerp_2d(
            self.camera.position, self.player.sprite.position, 0.50
        )
