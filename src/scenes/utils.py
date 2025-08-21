import arcade
from items.Container import Container
from items.Item import Item
from PIL import Image


def add_containers_to_list(
    point_list: list[tuple[int, int]],
    list_to_add: arcade.SpriteList | list,
    container_size: int,
    container_type: str | None = None,
    color: arcade.types.Color = arcade.color.GRAY,
    last_id: int = -1,
) -> None:
    id = last_id
    for x, y in point_list:
        tempSprite = Container(
            width=container_size,
            height=container_size,
            center_x=x,
            center_y=y,
            color=color,
        )
        tempSprite.item_placed = False
        if last_id > -1:
            tempSprite.id = id
            id += 1
        else:
            tempSprite.id = len(list_to_add)
        if container_type:
            tempSprite.type = container_type
        list_to_add.append(tempSprite)


def get_result(item_1: Item, item_2: Item, dict_to_find: dict) -> str | None:
    result = dict_to_find.get(item_1.name, {}).get(item_2.name, None)
    return result


def del_references_list(listToDel: arcade.SpriteList):
    for sprite in listToDel:
        del sprite


def apply_filter(image: Image.Image, filter: tuple[int, int, int, int]) -> Image.Image:
    overlay = Image.new("RGBA", image.size, filter)
    image_with_filter = Image.alpha_composite(image.convert("RGBA"), overlay)
    return image_with_filter


def is_in_box(
    x: float, y: float, top: float, bottom: float, right: float, left: float
) -> bool:
    return x > left and x < right and y > top and y < bottom
