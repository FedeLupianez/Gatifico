import arcade
import arcade.gui
from scenes.View import View
from characters.Player import Player
from DataManager import dataManager

MineralsResources = dataManager.loadData("Minerals.json")


class MixTable(View):
    def __init__(self, callback, player: Player):
        backgroundUrl = ":resources:Background/Texture/TX Plant.png"
        super().__init__(backgroundUrl=backgroundUrl, tileMapUrl=None)
        print("hola desde mix table")

        self.window.set_mouse_visible(True)
        self.camera.zoom = 1

        self.spriteList = arcade.SpriteList()

        self.UIManager = arcade.gui.UIManager(self.window)
        self.UIManager.enable()
        self.callback = callback
        self.items: dict = player.getInventory()

        self.UIAnchorLayout = arcade.gui.UIAnchorLayout()
        self.items_place = arcade.gui.UIButtonRow()
        self.UIAnchorLayout.add(child=self.items_place)

        self.UIManager.add(self.UIAnchorLayout)

    def on_draw(self):
        self.clear()  # limpia la pantalla
        self.camera.use()
        self.UIManager.draw(pixelated=True)

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        print("tecla presionada : ", symbol)
