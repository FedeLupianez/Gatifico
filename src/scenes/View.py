import arcade
import Constants
from arcade.camera import Camera2D
from DataManager import get_path, texture_manager


class Object(arcade.SpriteSolidColor):
    def __init__(
        self,
        width: int,
        height: int,
        center_x: float,
        center_y: float,
        name,
        obj_type,
        props,
    ) -> None:
        super().__init__(
            width=width, height=height, center_x=center_x, center_y=center_y
        )
        self.name = name
        self.type = obj_type
        self.props = props


class View(arcade.View):
    def __init__(self, background_url: str | None, tilemap_url: str | None) -> None:
        super().__init__()

        if tilemap_url:
            self.tilemap = arcade.load_tilemap(tilemap_url)
            self.tilemap.use_spatial_hash = True
            self.tilemap._lazy = False

        self.scene = self.CreateScene(
            background_url=background_url,
            tilemap_url=tilemap_url,
        )
        self.camera = Camera2D()
        self.gui_camera = Camera2D()

        # constantes para precalcular las operacions para actualizar la camara
        self._screen_width = self.camera.viewport_width
        self._screen_height = self.camera.viewport_height
        self._half_w = (self._screen_width / self.camera.zoom) * 0.5
        self._half_h = (self._screen_height / self.camera.zoom) * 0.5

        # lista de ui
        self.ui_sprites: arcade.SpriteList = arcade.SpriteList(lazy=False)
        self.background_sprites = arcade.SpriteList(lazy=False)
        self.volume_sprite = arcade.Sprite(get_path("volume_active.png"), scale=2)
        self.volume_sprite.center_x = self._screen_width - 30
        self.volume_sprite.center_y = self._screen_height - 30
        setattr(self.volume_sprite, "state", True)
        self.ui_sprites.append(self.volume_sprite)

        self._item_mouse_text = arcade.Text(
            text="",
            x=0,
            y=0,
            anchor_x="center",
            anchor_y="center",
            align="center",
        )
        self._item_text_background = arcade.SpriteSolidColor(
            width=1,
            height=1,
            color=arcade.color.BLACK,
            center_x=0,
            center_y=0,
        )
        self.ui_sprites.append(self._item_text_background)

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
            background_image.center_x = Constants.Game.SCREEN_WIDTH * 0.5
            background_image.center_y = Constants.Game.SCREEN_HEIGHT * 0.5
            # Creo una lista de sprites dentro de la scene donde se van
            # a almacenar todos los sprites que vayan en el fondo
            scene = arcade.Scene()
            scene.add_sprite_list("BACKGROUND")
            scene["BACKGROUND"].append(background_image)
            return scene
        else:
            return arcade.Scene()

    def load_object_layers(
        self, layerName: str, tileMap: arcade.TileMap
    ) -> arcade.SpriteList:
        temp_list = arcade.SpriteList(use_spatial_hash=True, lazy=False)
        temp_layer = tileMap.object_lists[layerName]

        for obj in temp_layer:
            # Crear un sprite que represente el objeto
            # Por ejemplo, un rectángulo sólido con las dimensiones del objeto
            # Obtengo el ancho y alto del objeto :
            shape = obj.shape
            if len(shape) < 4:
                raise ValueError(f"Forma del objeto {obj.name} invalida")
            assert isinstance(shape, list)
            top_left, top_right, _, bottom_left = shape

            width: float = top_right[0] - top_left[0]
            height: float = top_left[1] - bottom_left[1]
            center_x: float = top_left[0] + (width) * 0.5
            center_y: float = bottom_left[1] + (height) * 0.5

            sprite = Object(
                int(width),
                int(height),
                center_x=center_x,
                center_y=center_y,
                name=obj.name,
                obj_type=obj.type,
                props=obj.properties,
            )
            temp_list.append(sprite)
        return temp_list

    def update_sizes(self, width: int, height: int) -> None:
        self.camera.match_window()
        self._screen_width = width
        self._screen_height = height
        self._half_w = (self._screen_width / self.camera.zoom) * 0.5
        self._half_h = (self._screen_height / self.camera.zoom) * 0.5

    def on_resize(self, width: int, height: int) -> bool | None:
        self.update_sizes(width, height)

    def change_bg_sound_state(self, mouse_pos: tuple[float, float]):
        if not self.volume_sprite.collides_with_point(mouse_pos):
            return
        state = getattr(self.volume_sprite, "state")
        signal = ""
        texture_path = "volume_inactive.png" if state else "volume_active.png"
        if state:
            signal = Constants.SignalCodes.SILENCE_BACKGROUND
        else:
            signal = Constants.SignalCodes.RESUME_BACKGROUND
        setattr(self.volume_sprite, "state", not state)
        self.volume_sprite.texture = texture_manager._load_or_get_texture(
            get_path(texture_path)
        )
        return signal

    def item_hover(self, mouse_pos: tuple[float, float], items_list: arcade.SpriteList):
        x, y = mouse_pos
        if item := arcade.get_sprites_at_point((x, y), items_list):
            print(item)
            self._item_mouse_text.text = item[0].name or ""
            text_width = len(item[0].name) * self._item_mouse_text.font_size
            self._item_mouse_text.x = x
            self._item_mouse_text.y = y + 15
            self._item_text_background.center_x = x
            self._item_text_background.center_y = y + 13
            self._item_text_background.width = text_width
            self._item_text_background.height = self._item_mouse_text.font_size + 5
        else:
            self._item_mouse_text.text = ""
            self._item_text_background.width = 0
            self._item_text_background.height = 0
