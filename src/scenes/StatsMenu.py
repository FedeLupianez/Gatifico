import arcade
from characters.Player import Player
from scenes.View import View
from typing import Literal
from Constants import Filter
from scenes.utils import apply_filter


class StatsMenu(View):
    BUTTON_SIZE = 30

    def __init__(self, previus_scene: View) -> None:
        super().__init__(background_url=None, tilemap_url=None)
        self.player = Player()
        self.previus_scene = previus_scene
        background_image = previus_scene.get_screenshot()
        # Le pongo filtro oscuro al fondo
        self.background_image = arcade.texture.Texture.create_empty(
            "pause_bg", size=(background_image.width, background_image.height)
        )
        self.background_image.image = apply_filter(background_image, Filter.DARK)

        self.antique_height = self.player.attack_level_sprite.height
        self.antique_state: dict[Literal["attack", "defence"], tuple[float, float]] = {
            "attack": (
                self.player.attack_level_sprite.left,
                self.player.attack_level_sprite.center_y,
            ),
            "defence": (
                self.player.defence_level_sprite.left,
                self.player.defence_level_sprite.center_y,
            ),
        }

        self.attack_sprite = self.player.attack_level_sprite
        self.defence_sprite = self.player.defence_level_sprite

        left = self.window.center_x - 100
        self.attack_sprite.left = left
        self.attack_sprite.center_y = self.window.center_y + 50
        self.attack_sprite.height = 20

        self.defence_sprite.left = left
        self.defence_sprite.center_y = self.window.center_y - 50
        self.defence_sprite.height = 20

        self.ui_sprites.append(self.attack_sprite)
        self.ui_sprites.append(self.defence_sprite)

        self.upgrade_attack = arcade.SpriteSolidColor(
            width=StatsMenu.BUTTON_SIZE,
            height=StatsMenu.BUTTON_SIZE,
            center_x=self.window.center_x + 100,
            center_y=self.attack_sprite.center_y,
            color=arcade.color.GREEN,
        )
        self.upgrade_defence = arcade.SpriteSolidColor(
            width=StatsMenu.BUTTON_SIZE,
            height=StatsMenu.BUTTON_SIZE,
            center_x=self.window.center_x + 100,
            center_y=self.defence_sprite.center_y,
            color=arcade.color.GREEN,
        )

        self.ui_sprites.append(self.upgrade_attack)
        self.ui_sprites.append(self.upgrade_defence)

    def on_draw(self) -> None:
        self.clear()
        self.camera.use()
        if self.background_image:
            arcade.draw_texture_rect(
                self.background_image,
                rect=arcade.rect.Rect(
                    left=0,
                    right=0,
                    top=0,
                    bottom=0,
                    width=self._screen_width,
                    height=self._screen_height,
                    x=self._half_w,
                    y=self._half_h,
                ),
                pixelated=True,
            )
        self.ui_sprites.draw(pixelated=True)

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.ESCAPE:
            self.window.show_view(self.previus_scene)
            self.clean_up()

    def on_mouse_press(
        self, x: int, y: int, button: int, modifiers: int
    ) -> bool | None:
        if button != arcade.MOUSE_BUTTON_LEFT:
            return False
        if self.upgrade_attack.collides_with_point((x, y)):
            self.player.update_stats(stat="attack", value=self.player.attack_level + 1)
            return True

        if self.upgrade_defence.collides_with_point((x, y)):
            self.player.update_stats(
                stat="defence", value=self.player.defence_level + 1
            )
            return True

    def clean_up(self):
        del self.upgrade_defence
        del self.upgrade_attack
        del self.player

        self.attack_sprite.left, self.attack_sprite.center_y = self.antique_state[
            "attack"
        ]
        self.defence_sprite.left, self.defence_sprite.center_y = self.antique_state[
            "defence"
        ]
        self.attack_sprite.height = self.antique_height
        self.defence_sprite.height = self.antique_height
        del self.attack_sprite
        del self.defence_sprite
