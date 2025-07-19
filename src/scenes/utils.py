import arcade
from items.Container import Container
from items.Item import Item


def add_containers_to_list(
    pointList: list[tuple[int, int]],
    listToAdd: arcade.SpriteList,
    containerSize: int,
    containerType: str | None = None,
    lastId: int = -1,
) -> None:
    id = lastId
    for x, y in pointList:
        tempSprite = Container(
            width=containerSize,
            height=containerSize,
            center_x=x,
            center_y=y,
            color=arcade.color.GRAY,
        )
        tempSprite.item_placed = False
        if lastId > -1:
            tempSprite.id = id
            id += 1
        else:
            tempSprite.id = len(listToAdd)
        if containerType:
            tempSprite.type = containerType
        listToAdd.append(tempSprite)


def get_result(item_1: Item, item_2: Item, dictToFind: dict) -> str | None:
    result = dictToFind.get(item_1.name, {}).get(item_2.name, None)
    return result


def del_references_list(listToDel: arcade.SpriteList):
    for sprite in listToDel:
        del sprite
