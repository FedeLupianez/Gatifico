import arcade
import Constants


class View(arcade.View):
    def __init__(self, backgroundUrl: str | None, tileMapUrl: str | None) -> None:
        super().__init__()

        self.tileMap: arcade.TileMap | None = None
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
        # Si se le pasa un tilemap
        if tileMapUrl:
            self.tileMap = arcade.load_tilemap(tileMapUrl)
            return arcade.Scene.from_tilemap(self.tileMap)

        if backgroundUrl:
            # En cambio sino solo se pone el fondo:
            backgroundImage = arcade.Sprite(backgroundUrl, scale=1)
            # Centro la imagen
            backgroundImage.center_x = Constants.Game.SCREEN_WIDTH / 2
            backgroundImage.center_y = Constants.Game.SCREEN_HEIGHT / 2
            # Creo una lista de sprites dentro de la scene donde se van
            # a almacenar todos los sprites que vayan en el fondo
            scene = arcade.Scene()
            scene.add_sprite_list(Constants.SpriteNames.BACKGROUND)
            scene[Constants.SpriteNames.BACKGROUND].append(backgroundImage)
            return scene
        raise FileNotFoundError("Faltan argumentos")

    def loadObjectLayers(
        self, layerName: str, tileMap: arcade.TileMap
    ) -> arcade.SpriteList:
        tempList = arcade.SpriteList()

        for obj in tileMap.object_lists.get(layerName, []):
            # Crear un sprite que represente el objeto
            # Por ejemplo, un rectángulo sólido con las dimensiones del objeto
            sprite = arcade.SpriteSolidColor(
                int(obj.width), int(obj.height), arcade.color.RED
            )
            sprite.center_x = obj.x + obj.width / 2
            sprite.center_y = obj.y + obj.height / 2
            tempList.append(sprite)
        return tempList
