import arcade
import Constants
from scenes.Keys import Keys
from scenes.Forest import Forest
from scenes.Sell import Sell
from scenes.Load_screen import Load_screen
from scenes.Menu import Menu
from scenes.Test import Test
from scenes.Pause import Pause
from scenes.Laboratory import Laboratory
import gc
from DataManager import get_sound


# Esta clase va a manejar la vista que se muestra en la pantalla
class ViewManager:
    current_scene_id = "MENU"

    def __init__(self, window: arcade.Window) -> None:
        self.window = window
        # Tiene su propia ventana
        self.background_sound = arcade.play_sound(
            get_sound("Menu_loop.mp3"), loop=True, volume=0.2
        )
        self.current_scene = Menu(self.callback)

        # Diccionario con los objetos de las escenas pero sin instanciar para ahorrar recursos
        self.scenes = {
            "MENU": Menu,
            "TEST": Test,
            "LABORATORY": Laboratory,
            "SELL": Sell,
            "FOREST": Forest,
            "KEYS": Keys,
        }
        self.window.show_view(
            self.current_scene
        )  # Pongo que se vea la view por default apenas se crea el manager, o sea el menu

    def callback(self, signal: int, data=None, **kwargs):
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
            self.pause_game()
            return
        if signal == Constants.SignalCodes.SILENCE_BACKGROUND:
            assert self.background_sound, "No hay sonido de fondo"
            self.background_sound.pause()
        if signal == Constants.SignalCodes.RESUME_BACKGROUND:
            assert self.background_sound, "No hay sonido de fondo"
            self.background_sound.play()

        if signal == Constants.SignalCodes.CHANGE_VIEW:
            self.current_scene_id = data

            # Garbage collector, lo fuerzo para que limpie la memoria
            self.current_scene.clean_up()
            gc.collect()
            del self.current_scene  # Libero los recursos ocupados anteriormente

            if not data:
                raise ValueError("Data no está disponible")
            # Creo una nueva escena
            self.current_scene = self.scenes[data](self.callback, **kwargs)

            if "load_screen" in kwargs:
                load_scene = Load_screen(self.current_scene)
                self.window.show_view(load_scene)
            else:
                self.window.show_view(
                    self.current_scene
                )  # Hago que la nueva escena se vea

    def pause_game(self) -> None:
        new_scene = Pause(
            previus_scene=self.current_scene,
            callback=self.callback,  # Le paso el callback del ViewManager para que pueda cerrar o cambiar a una escena
        )
        self.window.show_view(new_scene)
