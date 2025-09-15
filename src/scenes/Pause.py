import arcade
from DataManager import get_path
from .View import View
from Constants import Game, Filter, SignalCodes
from .utils import apply_filter


class Pause(View):
    def __init__(self, previus_scene: View, callback):
        super().__init__(background_url=None, tilemap_url=None)
        # Le pongo filtro oscuro al fondo
        background_image = previus_scene.get_screenshot()
        self.background_image = arcade.texture.Texture.create_empty(
            "pause_bg", size=(background_image.width, background_image.height)
        )
        self.background_image.image = apply_filter(background_image, Filter.DARK)
        self.window.set_mouse_visible(True)
        self.previus_scene = previus_scene
        self.buttons_scale = 3
        self.callback = callback
        self.setup()

    def setup(self) -> None:
        self.sprite_list = arcade.SpriteList()
        self.setup_buttons()

    def setup_buttons(self) -> None:
        self.resume_button = arcade.Sprite(
            get_path("PlayButton.png"), scale=self.buttons_scale
        )
        self.exit_button = arcade.Sprite(
            get_path("ExitButton.png"), scale=self.buttons_scale
        )
        self.resume_button.center_x = Game.SCREEN_CENTER_X
        self.exit_button.center_x = Game.SCREEN_CENTER_X
        self.resume_button.center_y = Game.SCREEN_CENTER_Y + 100
        self.exit_button.center_y = Game.SCREEN_CENTER_Y - 100
        self.sprite_list.append(self.resume_button)
        self.sprite_list.append(self.exit_button)

    def on_draw(self):
        self.camera.use()
        self.clear()
        if self.background_image:
            arcade.draw_texture_rect(
                self.background_image,
                rect=arcade.rect.Rect(
                    left=0,
                    right=0,
                    top=0,
                    bottom=0,
                    width=Game.SCREEN_WIDTH,
                    height=Game.SCREEN_HEIGHT,
                    x=Game.SCREEN_CENTER_X,
                    y=Game.SCREEN_CENTER_Y,
                ),
                pixelated=True,
            )
        self.sprite_list.draw(pixelated=True)

    def clean_up(self) -> None:
        self.sprite_list.clear()
        del self.sprite_list
        del self.background_image
        self.window.set_mouse_visible(False)

    def on_mouse_press(
        self, x: int, y: int, button: int, modifiers: int
    ) -> bool | None:
        if self.resume_button.collides_with_point((x, y)):
            self.clean_up()
            self.window.show_view(self.previus_scene)

        if self.exit_button.collides_with_point((x, y)):
            self.callback(SignalCodes.CLOSE_WINDOW, data="Close window")

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.ESCAPE:
            self.clean_up()
            self.window.show_view(self.previus_scene)
