import arcade
from DataManager import mineral_resources


class Item(arcade.Sprite):
    _resources = mineral_resources
    __slots__ = ["id", "name", "quantity", "container_id"]

    def __init__(self, name: str, quantity: int, scale: int = 1) -> None:
        path: str = str(Item._resources[name]["item"]["path"])
        super().__init__(path, scale=scale)
        self.id: int = -1
        self.name = name
        self.quantity = quantity
        self.container_id: int = -1
        self.price: int = int(Item._resources[name]["item"].get("price", 0))

    def change_position(self, center_x: float, center_y: float) -> None:
        self.center_x = center_x
        self.center_y = center_y

    def change_container(self, newContainerId: int) -> None:
        self.container_id = newContainerId

    def change_texture(self, new_texture: str) -> None:
        new_path: str = str(Item._resources[new_texture]["item"]["path"])
        self.texture = arcade.load_texture(new_path)

    def __str__(self):
        return f"Nombre : {self.name}, Cantidad : {self.quantity}\nID: {self.id} Container ID : {self.container_id}"
