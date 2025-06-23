import arcade
import Constants
from scenes.Menu import Menu
from scenes.Test import Test


# Esta clase va a manejar la vista que se muestra en la pantalla
class ViewManager:
    window = arcade.Window(
        Constants.Game.SCREEN_WIDTH,
        Constants.Game.SCREEN_HEIGHT,
        title="Gatifico",
        update_rate=Constants.Game.FPS,
        draw_rate=Constants.Game.FPS,
    )
    current_scene_id = "MENU"

    def __init__(self) -> None:
        # Tiene su propia ventana
        self.current_scene = Menu(self.callback)

        # Diccionario con los objetos de las escenas pero sin instanciar para ahorrar recursos
        self.scenes = {"MENU": Menu, "TEST": Test}
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
            self.current_scene = self.scenes[data](
                self.callback
            )  # Cambio la variable anterior por la nueva escena
            self.window.show_view(self.current_scene)  # Hago que la nueva escena se vea
