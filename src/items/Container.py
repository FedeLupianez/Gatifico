import arcade
from arcade.types import RGBA


class Container(arcade.SpriteSolidColor):
    def __init__(
        self,
        width: int,
        height: int,
        center_x: float,
        center_y: float,
        color: RGBA = arcade.color.GRAY,
    ) -> None:
        super().__init__(
            width=width,
            height=height,
            center_x=center_x,
            center_y=center_y,
            color=color,
        )
        self.type: str = ""
        self.container_id: int = -1
        self.item_placed: bool = False
