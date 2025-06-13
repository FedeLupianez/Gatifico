import arcade
import Constants
import scenes.Menu as MenuScene
import scenes.House as HouseScene


# Esta clase va a manejar la vista que se muestra en la pantalla
class ViewManager:
    window = arcade.Window(
        Constants.Game.SCREEN_WIDTH,
        Constants.Game.SCREEN_HEIGHT,
        title="A coloquio",
        update_rate=Constants.Game.FPS,
        draw_rate=Constants.Game.FPS,
    )
    current_scene_id = "MENU"

    def __init__(self) -> None:
        # Tiene su propia ventana
        self.current_scene = MenuScene.Menu(self.callback)

        # Diccionario con los objetos de las escenas pero sin instanciar para ahorrar recursos
        self.scenes = {"MENU": MenuScene.Menu, "HOUSE": HouseScene.House}
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
