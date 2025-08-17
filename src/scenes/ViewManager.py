import arcade
import Constants
from characters.Player import Player
from scenes.Menu import Menu
from scenes.Test import Test
from scenes.MixTable import MixTable
from scenes.SplitTable import SplitTable
from scenes.Chest import Chest
from typing import Callable
from scenes.Pause import Pause
from scenes.Laboratory import Laboratory
import gc


# Esta clase va a manejar la vista que se muestra en la pantalla
class ViewManager:
    current_scene_id = "MENU"

    def __init__(self, player: Player, window: arcade.Window) -> None:
        self.window = window
        # Tiene su propia ventana
        self.current_scene = Menu(self.callback)
        self.player = player

        # Diccionario con los objetos de las escenas pero sin instanciar para ahorrar recursos
        self.scenes = {
            "MENU": Menu,
            "TEST": Test,
            "LABORATORY": Laboratory,
            "MIX_TABLE": MixTable,
            "SPLIT_TABLE": SplitTable,
            "CHEST": Chest,
        }
        self.window.show_view(
            self.current_scene
        )  # Pongo que se vea la view por default apenas se crea el manager, o sea el menu

    def callback(self, signal: int, data=None):
        """
        Función de la clase padre para recibir las señales
        signal (int) : Codigo de señal
        data (str) : La información que trae consigo la señal
        """

        if signal == Constants.SignalCodes.CLOSE_WINDOW:
            # Cierra la ventana
            self.window.close()
        if signal == Constants.SignalCodes.PAUSE_GAME:
            # Pausa el juego pasandole un callback de la funcion para obtener una screenshot
            self.pause_game(self.current_scene.get_screenshot)

        print("Mensaje recibido : ", data)
        if signal == Constants.SignalCodes.CHANGE_VIEW:
            self.current_scene_id = data

            # Garbage collector, lo fuerzo para que limpie la memoria
            gc.collect()
            self.current_scene.clean_up()
            del self.current_scene  # Libero los recursos ocupados anteriormente

            if not data:
                raise ValueError("Data no está disponible")
            # Cambio la variable anterior por la nueva escena
            if data == "MENU":
                self.current_scene = self.scenes[data](self.callback)
            else:
                self.current_scene = self.scenes[data](self.callback, self.player)
            self.window.show_view(self.current_scene)  # Hago que la nueva escena se vea

    def pause_game(self, screenshot_function: Callable) -> None:
        new_scene = Pause(
            previus_scene=self.current_scene,
            background_image=self.current_scene.get_screenshot(),
            callback=self.callback,  # Le paso el callback del ViewManager para que pueda cerrar o cambiar a una escena
        )
        self.window.show_view(new_scene)

    def update_camera_view(self):
        self.current_scene.camera.match_window()
