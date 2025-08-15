import arcade
import Constants
from arcade.camera import Camera2D


class View(arcade.View):
    def __init__(self, background_url: str | None, tilemap_url: str | None) -> None:
        super().__init__()

        if tilemap_url:
            self.tilemap = arcade.load_tilemap(tilemap_url)
            self.tilemap.use_spatial_hash = True

        self.scene = self.CreateScene(
            background_url=background_url,
            tilemap_url=tilemap_url,
        )
        self.camera = Camera2D()

    def CreateScene(
        self, background_url: str | None, tilemap_url: str | None = None
    ) -> arcade.Scene:
        """Función para crear una nueva escena
        Args :
            tile_map_url (string) : Url del tile map de la escena, este mapa sirve para las colisiones
            background_url (string) : Url del fondo para cargar la imagen
        """
        # Si se le pasa un tilemap
        if tilemap_url:
            return arcade.Scene.from_tilemap(self.tilemap)

        if background_url:
            # En cambio sino solo se pone el fondo:
            background_image = arcade.Sprite(background_url, scale=1)
            background_image.width = Constants.Game.SCREEN_WIDTH
            background_image.height = Constants.Game.SCREEN_HEIGHT
            # Centro la imagen
            background_image.center_x = Constants.Game.SCREEN_WIDTH / 2
            background_image.center_y = Constants.Game.SCREEN_HEIGHT / 2
            # Creo una lista de sprites dentro de la scene donde se van
            # a almacenar todos los sprites que vayan en el fondo
            scene = arcade.Scene()
            scene.add_sprite_list("BACKGROUND")
            scene["BACKGROUND"].append(background_image)
            return scene
        raise FileNotFoundError("Faltan argumentos")

    def load_object_layers(
        self, layerName: str, tileMap: arcade.TileMap
    ) -> arcade.SpriteList:
        temp_list = arcade.SpriteList(use_spatial_hash=True)
        temp_layer = tileMap.object_lists[layerName]

        for obj in temp_layer:
            # Crear un sprite que represente el objeto
            # Por ejemplo, un rectángulo sólido con las dimensiones del objeto
            # Obtengo el ancho y alto del objeto :
            shape = obj.shape
            if len(shape) != 4:
                raise ValueError(f"Forma del objeto {obj.name} invalida")
            top_left, top_right, _, bottom_left = shape[:4]

            width: float = top_right[0] - top_left[0]
            height: float = top_left[1] - bottom_left[1]
            center_x: float = top_left[0] + (width) / 2
            center_y: float = bottom_left[1] + (height) / 2

            sprite = arcade.SpriteSolidColor(
                int(width), int(height), center_x=center_x, center_y=center_y
            )
            sprite.__setattr__("name", obj.name)
            sprite.__setattr__("type", obj.type)
            sprite.__setattr__("props", obj.properties)
            temp_list.append(sprite)
        return temp_list
