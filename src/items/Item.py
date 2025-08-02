import arcade
from typing import Dict, Literal
import DataManager

MineralsResources: Dict[
    str,
    Dict[
        Literal["big", "mid", "small", "item"],
        Dict[Literal["path", "touches"], str | int],
    ],
] = DataManager.loadData("Minerals.json")


class Item(arcade.Sprite):
    __slots__ = ["id", "name", "quantity", "container_id"]

    def __init__(self, name: str, quantity: int, scale: int = 1) -> None:
        path: str = str(MineralsResources[name]["item"]["path"])
        super().__init__(path, scale=scale)
        self.id: int = -1
        self.name = name
        self.quantity = quantity
        self.container_id: int = -1

    def change_position(self, center_x: float, center_y: float) -> None:
        self.center_x = center_x
        self.center_y = center_y

    def change_container(self, newContainerId: int) -> None:
        self.container_id = newContainerId

    def __str__(self):
        return f"Nombre : {self.name}, Cantidad : {self.quantity}\nID: {self.id} Container ID : {self.container_id}"
