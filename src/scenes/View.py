import arcade
import Constants.Game
import Constants.SpriteNames


class View(arcade.View):
    def __init__(self, backgroundUrl: str | None, tileMapUrl: str | None) -> None:
        super().__init__()

        self.scene = self.CreateScene(
            backgroundUrl=backgroundUrl, tileMapUrl=tileMapUrl
        )

    def CreateScene(
        self, backgroundUrl: str | None, tileMapUrl: str | None = None
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

        if backgroundUrl:
            # En cambio sino solo se pone el fondo:
            backgroundImage = arcade.Sprite(backgroundUrl, scale=1)
            # Centro la imagen
            backgroundImage.center_x = Constants.Game.SCREEN_WIDTH / 2
            backgroundImage.center_y = Constants.Game.SCREEN_HEIGHT / 2
            # Creo una lista de sprites dentro de la scene donde se van
            # a almacenar todos los sprites que vayan en el fondo
            scene.add_sprite_list(Constants.SpriteNames.BACKGROUND)
            scene[Constants.SpriteNames.BACKGROUND].append(backgroundImage)
            return scene
        raise FileNotFoundError("Faltan argumentos")
