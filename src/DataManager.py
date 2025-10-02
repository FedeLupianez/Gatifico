import json
import os
from typing import Dict, Literal, TypedDict
from arcade import TextureCacheManager, Sound
from time import time


BASE_DIR = os.path.dirname(__file__)
DATAFILES_DIR = BASE_DIR + "/resources/Data/"


ChestsData = Dict[str, Dict[str, int]]


class PlayerData(TypedDict):
    Inventory: Dict[str, int]
    Position: Dict[Literal["center_x", "center_y"], float]


# Función para leer un archivo json
def loadData(filename: str) -> dict:
    if not os.path.exists(DATAFILES_DIR + filename):
        # Si no existe creo el archivo
        os.makedirs(os.path.dirname(DATAFILES_DIR + filename), exist_ok=True)
        return {}
    with open(DATAFILES_DIR + filename, "r") as file:
        return json.load(file)


def read_file(filename: str):
    with open(DATAFILES_DIR + filename, "r") as file:
        return file.readlines()


def write_file(filename: str, data: str, mode: Literal["a", "w"]) -> None:
    with open(DATAFILES_DIR + filename, mode) as file:
        file.write(data)


game_data: dict = loadData("Saved/Actual_Scene_Data.json")
print(game_data)
chests_data: dict = loadData("Saved/Chests_Data.json")
sounds_loader: dict[str, Sound] = {}
mineral_resources: Dict[
    str,
    Dict[
        Literal["big", "mid", "small", "item"],
        Dict[Literal["path", "touches", "price"], str | int],
    ],
] = loadData("Minerals.json")
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
    with open(DATAFILES_DIR + "Saved/Actual_Scene_Data.json", "w") as file:
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


def get_sound(file_name: str) -> Sound:
    global sounds_loader
    if file_name not in sounds_loader:
        sounds_loader[file_name] = Sound(get_path(file_name))
    return sounds_loader[file_name]


texture_manager = TextureCacheManager()
