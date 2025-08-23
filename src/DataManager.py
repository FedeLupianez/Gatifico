import json
import os
from typing import Dict, Literal, TypedDict
from arcade import TextureCacheManager


BASE_DIR = os.path.dirname(__file__)
DATAFILES_DIR = BASE_DIR + "/resources/Data/"


ChestsData = Dict[str, Dict[str, int]]


class PlayerData(TypedDict):
    Inventory: Dict[str, int]
    Position: Dict[Literal["center_x", "center_y"], float]


# Función para leer un archivo json
def loadData(filename: str) -> dict:
    with open(DATAFILES_DIR + filename, "r") as file:
        return json.load(file)


game_data: dict = loadData("Actual_Scene_Data.json")
chests_data: dict = loadData("Chests_Data.json")


def store_actual_data(player_data: PlayerData, actualScene) -> None:
    global game_data
    print(player_data)
    with open(DATAFILES_DIR + "Actual_Scene_Data.json", "w") as file:
        data = {
            "player": {
                "position": {
                    "center_x": player_data["Position"]["center_x"],
                    "center_y": player_data["Position"]["center_y"],
                },
                "inventory": player_data["Inventory"],
            },
            "scene": actualScene,
        }
        game_data = data
        json.dump(data, file)


def store_chest_data(new_data: ChestsData, chest_id: int):
    global chests_data
    chests_data[chest_id] = new_data
    with open(DATAFILES_DIR + "Chests_Data.json", "w") as file:
        json.dump(chests_data, file)


texture_manager = TextureCacheManager()
