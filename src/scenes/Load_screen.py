import arcade
from scenes.View import View


class Load_screen(View):
    def __init__(self, load_scene: View, time: float = 4) -> None:
        super().__init__(background_url=None, tilemap_url=None)
        self.load_scene = load_scene
        self.text: arcade.Text = arcade.Text(
            text="Cargando",
            x=500,
            y=300,
            font_size=24,
            color=arcade.color.WHITE,
        )
        self.limit_time = 4
        self.update_time = 1
        self.current_time = 0

    def on_draw(self):
        self.clear(arcade.color.BLACK)
        self.text.draw()

    def on_update(self, delta_time: float) -> None:
        self.update_time -= delta_time
        if self.update_time <= 0:
            self.text.text += "."
            self.update_time = 1

        self.current_time += delta_time

        if self.current_time >= self.limit_time:
            self.window.show_view(self.load_scene)
