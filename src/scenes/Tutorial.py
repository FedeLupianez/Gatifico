import arcade
from View import View
from characters.Player import Player


class Tutorial(View):
    def __init__(self) -> None:
        super().__init__(background_url=None, tilemap_url=None)
        self.player = Player()

    def on_draw(self) -> None:
        pass
