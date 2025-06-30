from typing import Optional
import arcade
import Constants
from arcade.camera import Camera2D


class View(arcade.View):
    def __init__(self, backgroundUrl: str | None, tileMapUrl: str | None) -> None:
        super().__init__()

        if tileMapUrl:
            self.tileMap = arcade.load_tilemap(tileMapUrl)

        self.scene = self.CreateScene(
            backgroundUrl=backgroundUrl, tileMapUrl=tileMapUrl
        )
        self.camera = Camera2D()

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
        tempLayer = tileMap.object_lists[layerName]

        for obj in tempLayer:
            # Crear un sprite que represente el objeto
            # Por ejemplo, un rectángulo sólido con las dimensiones del objeto
            # Obtengo el ancho y alto del objeto :
            topLeft, topRight, bottomRight, bottomLeft = obj.shape

            width: float = topRight[0] - topLeft[0]
            height: float = topLeft[1] - bottomLeft[1]
            center_x: float = topLeft[0] + (width) / 2
            center_y: float = bottomLeft[1] + (height) / 2

            sprite = arcade.SpriteSolidColor(
                int(width), int(height), center_x=center_x, center_y=center_y
            )
            sprite.name = obj.name
            sprite.type = obj.type
            sprite.props = obj.properties
            tempList.append(sprite)
        return tempList
