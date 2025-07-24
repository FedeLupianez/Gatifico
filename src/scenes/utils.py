import arcade
from items.Container import Container
from items.Item import Item


def add_containers_to_list(
    point_list: list[tuple[int, int]],
    list_to_add: arcade.SpriteList,
    container_size: int,
    container_type: str | None = None,
    last_id: int = -1,
) -> None:
    id = last_id
    for x, y in point_list:
        tempSprite = Container(
            width=container_size,
            height=container_size,
            center_x=x,
            center_y=y,
            color=arcade.color.GRAY,
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
