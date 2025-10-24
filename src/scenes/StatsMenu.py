import arcade
from characters.Player import Player
from scenes.View import View
from typing import Literal
from Constants import Filter
from scenes.utils import apply_filter
from DataManager import get_path


class StatsMenu(View):
    BUTTON_SIZE = 30

    def __init__(self, previus_scene: View) -> None:
        super().__init__(background_url=None, tilemap_url=None)
        self.player = Player()
        self.player_ui = self.player.ui
        self.previus_scene = previus_scene
        background_image = previus_scene.get_screenshot()
        # Le pongo filtro oscuro al fondo
        self.background_image = arcade.texture.Texture.create_empty(
            "pause_bg", size=(background_image.width, background_image.height)
        )
        self.background_image.image = apply_filter(background_image, Filter.DARK)
        menu_background = arcade.Sprite(get_path("stats_bg.png"), scale=10)
        menu_background.center_x = self._half_w
        menu_background.center_y = self._half_h
        self.ui_sprites.append(menu_background)

        self.antique_height = self.player_ui.attack_sprite.height
        self.antique_state: dict[Literal["attack", "defence"], tuple[float, float]] = {
            "attack": (
                self.player_ui.attack_sprite.left,
                self.player_ui.attack_sprite.center_y,
            ),
            "defence": (
                self.player_ui.defence_sprite.left,
                self.player_ui.defence_sprite.center_y,
            ),
        }

        self.attack_sprite = self.player_ui.attack_sprite
        self.defence_sprite = self.player_ui.defence_sprite

        left = self.window.center_x - 100
        self.attack_sprite.left = left
        self.attack_sprite.center_y = self.window.center_y + 50
        self.attack_sprite.height = 20

        self.defence_sprite.left = left
        self.defence_sprite.center_y = self.window.center_y - 50
        self.defence_sprite.height = 20

        self.ui_sprites.append(self.attack_sprite)
        self.ui_sprites.append(self.defence_sprite)

        # Textos :
        self.attack_text = arcade.Text(
            text=f"Ataque : {self.player.attack_level}",
            x=self.attack_sprite.left,
            y=self.attack_sprite.center_y + 40,
            font_size=16,
            color=arcade.color.WHITE,
        )

        self.defence_text = arcade.Text(
            text=f"Defensa : {self.player.defence_level}",
            x=self.defence_sprite.left,
            y=self.defence_sprite.center_y + 40,
            font_size=16,
            color=arcade.color.WHITE,
        )

        # Botones
        self.upgrade_attack = arcade.Sprite(get_path("upgrade_button.png"), scale=2)
        self.upgrade_attack.center_x = self._half_w + 100
        self.upgrade_attack.center_y = self.attack_sprite.center_y

        self.upgrade_defence = arcade.Sprite(get_path("upgrade_button.png"), scale=2)
        self.upgrade_defence.center_x = self._half_w + 100
        self.upgrade_defence.center_y = self.defence_sprite.center_y

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
        self.attack_text.draw()
        self.defence_text.draw()

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
            self.player_ui.update_attack(self.player.attack_level)
            self.attack_text.text = f"Ataque : {self.player.attack_level}"
            return True

        if self.upgrade_defence.collides_with_point((x, y)):
            self.player.update_stats(
                stat="defence", value=self.player.defence_level + 1
            )
            self.player_ui.update_defence(self.player.defence_level)
            self.defence_text.text = f"Defensa : {self.player.defence_level}"
            return True

    def clean_up(self):
        del self.upgrade_defence
        del self.upgrade_attack
        del self.player
        del self.attack_text
        del self.defence_text

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
