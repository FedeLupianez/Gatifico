import arcade
from scenes.View import View
from characters.Player import Player


class Load_screen(View):
    def __init__(self, load_scene: View, time: float = 4) -> None:
        super().__init__(background_url=None, tilemap_url=None)
        self.load_scene = load_scene
        self.text: arcade.Text = arcade.Text(
            text="Cargando",
            x=self.window.width // 2 - len("Cargando") * 12,
            y=self.window.height // 2,
            font_size=24,
            color=arcade.color.WHITE,
        )
        self.limit_time = time
        self.update_time = 1
        self.current_time = 0
        self.player_draw_list = arcade.SpriteList()
        self.player = Player()
        self.setup_player_sprite()

    def setup_player_sprite(self):
        self.player.process_state(arcade.key.D)
        self.temp_sprite = arcade.Sprite(self.player.sprite.texture)
        self.temp_sprite.scale_x = -2
        self.temp_sprite.scale_y = 2
        self.temp_sprite.center_x = self.window.width // 7
        self.temp_sprite.center_y = self.window.height // 4
        self.player_draw_list.append(self.temp_sprite)

    def on_draw(self):
        self.clear(arcade.color.BLACK)
        self.text.draw()
        self.player_draw_list.draw(pixelated=True)

    def on_update(self, delta_time: float) -> None:
        self.update_time -= delta_time
        if self.update_time <= 0:
            self.text.text += "."
            self.update_time = 1

        self.current_time += delta_time
        self.player.update_animation(delta_time)
        self.temp_sprite.texture = self.player.sprite.texture

        if self.current_time >= self.limit_time:
            self.player.stop_state()
            self.window.show_view(self.load_scene)
            self.clean_up()

    def clean_up(self):
        del self.player
        del self.player_draw_list
        del self.text
        del self.load_scene
        del self.temp_sprite
