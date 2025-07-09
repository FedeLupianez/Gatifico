import arcade
import Constants
from characters.Player import Player
from scenes.Menu import Menu
from scenes.Test import Test
from scenes.MixTable import MixTable
from scenes import SplitTable
from scenes.Chest import Chest


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
            "MIX_TABLE": MixTable,
            "SPLIT_TABLE": SplitTable,
            "CHEST": Chest,
        }
        self.window.show_view(
            self.current_scene
        )  # Pongo que se vea la view por default apenas se crea el manager, o sea el menu

    def callback(self, signal: int, data: str):
        """
        Función de la clase padre para recibir las señales
        signal (int) : Codigo de señal
        data (str) : La información que trae consigo la señal
        """
        print("Mensaje recibido : ", data)
        if signal == Constants.SignalCodes.CHANGE_VIEW:
            self.current_scene_id = data
            del self.current_scene  # Libero los recursos ocupados anteriormente

            # Cambio la variable anterior por la nueva escena
            if data in ["TEST", "MIX_TABLE", "SPLIT_TABLE"]:
                self.current_scene = self.scenes[data](self.callback, self.player)
            elif data[0] in ["CHEST"]:
                self.current_scene = self.scenes[data[0]](
                    self.callback, data[1], data[2]
                )
                print("cambiando a chest")
            else:
                self.current_scene = self.scenes[data](self.callback)
            self.window.show_view(self.current_scene)  # Hago que la nueva escena se vea

        if signal == Constants.SignalCodes.CLOSE_WINDOW:
            self.window.close()
