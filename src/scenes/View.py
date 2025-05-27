import arcade
import Constants
import scenes.SpriteNames as SpriteNames


class View(arcade.View):
    Window = arcade.Window(
        Constants.SCREEN_WIDTH,
        Constants.SCREEN_HEIGHT,
        title="Prueba",
        update_rate=Constants.FPS,
        center_window=True,
    )

    def __init__(self, backgroundUrl: str, tileMapUrl: str | None) -> None:
        super().__init__(window=self.Window)
        # Camara para dibujar los elementos
        self.cameraGui = arcade.Camera2D(window=self.Window)

        self.scene = self.CreateScene(
            backgroundUrl=backgroundUrl, tileMapUrl=tileMapUrl
        )

    def CreateScene(
        self, backgroundUrl: str, tileMapUrl: str | None = None
    ) -> arcade.Scene:
        """Función para crear una nueva escena
        Args :
            tile_map_url (string) : Url del tile map de la escena, este mapa sirve para las colisiones
            background_url (string) : Url del fondo para cargar la imagen
        """

        scene = arcade.Scene()
        # Si se le pasa un tilemap
        if tileMapUrl:
            tempTileMap = arcade.TileMap(map_file=tileMapUrl)
            scene.from_tilemap(tempTileMap)
            del tileMapUrl
            return scene
        # En cambio sino solo se pone el fondo:
        backgroundImage = arcade.Sprite(backgroundUrl, scale=1)
        scene.add_sprite_list(SpriteNames.BACKGROUND)
        scene[SpriteNames.BACKGROUND].append(backgroundImage)
        return scene
