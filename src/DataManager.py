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


test_chests: ChestsData = {
    "chest_1": {"rubi": 4, "stone": 3},
    "chest_2": {},
    "chest_3": {},
}


# Función para leer un archivo json
def loadData(filename: str) -> dict:
    with open(DATAFILES_DIR + filename, "r") as file:
        return json.load(file)


game_data: dict = loadData("GameData.json")


def storeGameData(player_data: PlayerData, actualScene) -> None:
    global game_data
    print(player_data)
    with open(DATAFILES_DIR + "GameData.json", "w") as file:
        data = {
            "player": {
                "position": {
                    "center_x": player_data["Position"]["center_x"],
                    "center_y": player_data["Position"]["center_y"],
                },
                "inventory": player_data["Inventory"],
            },
            "scene": actualScene,
            "chests": test_chests,
        }
        game_data = data
        json.dump(data, file)


texture_manager = TextureCacheManager()
