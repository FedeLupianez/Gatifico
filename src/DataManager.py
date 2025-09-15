import json
import os
from typing import Dict, Literal, TypedDict
from arcade import TextureCacheManager
from time import time


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
seconds_to_save: int = 3


def store_actual_data(player, actualScene) -> None:
    global game_data, seconds_to_save
    actual_time = time()
    if actual_time - game_data["time_stamp"] < seconds_to_save:
        return
    data = {
        "player": {
            "position": {
                "center_x": player.sprite.center_x,
                "center_y": player.sprite.center_y,
            },
            "inventory": player.inventory,
        },
        "scene": actualScene,
        "time_stamp": actual_time,
    }
    game_data = data
    with open(DATAFILES_DIR + "Actual_Scene_Data.json", "w") as file:
        json.dump(data, file)


def store_chest_data(new_data: ChestsData, chest_id: str):
    global chests_data
    chests_data[chest_id] = new_data
    with open(DATAFILES_DIR + "Chests_Data.json", "w") as file:
        json.dump(chests_data, file)


def get_path(file_name: str) -> str:
    """Función que retorna el path absoluto desde la carpeta source al archivo"""
    for base_dir, carpetas, files in os.walk(BASE_DIR):
        if file_name in files:
            return os.path.abspath(os.path.join(base_dir, file_name))
    return ""


texture_manager = TextureCacheManager()
