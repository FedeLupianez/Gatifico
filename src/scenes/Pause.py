import arcade
from .View import View
from Constants import Game


class Pause(View):
    def __init__(self, previus_scene: View, background_image: arcade.Texture):
        background_url = ":resources:Background/Texture/TX Plant.png"
        super().__init__(background_url, tileMapUrl=None)
        self.background_image = background_image
        self.window.set_mouse_visible(True)
        self.previus_scene = previus_scene
        self.setup()

    def setup(self) -> None:
        self.sprite_list = arcade.SpriteList()
        self.setup_buttons()

    def setup_buttons(self) -> None:
        self.resume_button = arcade.Sprite(":resources:UI/PlayButton.png", scale=1)
        self.exit_button = arcade.Sprite(":resources:UI/ExitButton.png", scale=1)
        self.resume_button.center_x = Game.SCREEN_WIDTH / 2
        self.exit_button.center_x = Game.SCREEN_WIDTH / 2
        self.resume_button.center_y = (Game.SCREEN_HEIGHT / 2) - 100
        self.exit_button.center_y = (Game.SCREEN_HEIGHT / 2) + 100
        self.sprite_list.append(self.resume_button)
        self.sprite_list.append(self.exit_button)

    def on_draw(self):
        self.camera.use()
        self.clear()
        self.sprite_list.draw(pixelated=True)
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
                    x=Game.SCREEN_WIDTH / 2,
                    y=Game.SCREEN_HEIGHT / 2,
                ),
                pixelated=True,
            )

    def clean_up(self) -> None:
        self.sprite_list.clear()
        del self.sprite_list
        del self.background_image

    def on_mouse_press(
        self, x: int, y: int, button: int, modifiers: int
    ) -> bool | None:
        if self.resume_button.collides_with_point((x, y)):
            self.clean_up()
            self.window.show_view(self.previus_scene)

        if self.exit_button.collides_with_point((x, y)):
            print("Salir al menu")
