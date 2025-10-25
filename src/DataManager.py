from functools import lru_cache
import json
import os
from typing import Dict, Literal, TypedDict
from arcade import TextureCacheManager, Sound
from time import time
from Constants import Game


BASE_DIR = os.path.dirname(__file__)
DATAFILES_DIR = BASE_DIR + "/resources/Data/"
SAVED_FILE = "Saved/saved.json"
CHEST_FILE = "Saved/Chests_Data.json"


# Función para leer un archivo json
def loadData(filename: str) -> dict:
    if not os.path.exists(DATAFILES_DIR + filename):
        # Si no existe creo el archivo
        os.makedirs(os.path.dirname(DATAFILES_DIR + filename), exist_ok=True)
        return {}
    with open(DATAFILES_DIR + filename, "r") as file:
        return json.load(file)


def reset_data():
    global game_data
    temp = {
        "player": {
            "position": {"center_x": 677.9216478540386, "center_y": 1244.99966327372},
            "inventory": {},
            "lifes": 5,
            "healt": 100,
        },
        "scene": "LABORATORY",
        "time_stamp": 0,
    }
    write_json(SAVED_FILE, temp)
    game_data = temp
    return temp


game_data: dict = loadData(SAVED_FILE)
if not game_data:
    game_data = reset_data()
chests_data: dict = loadData(CHEST_FILE)
sounds_loader: dict[str, Sound] = {}
mineral_resources: Dict[
    str,
    Dict[
        Literal["big", "mid", "small", "item"],
        Dict[Literal["path", "touches", "price"], str | int],
    ],
] = loadData("Minerals.json")
texture_manager = TextureCacheManager()

ChestsData = list[tuple[str, int, int]]


class PlayerData(TypedDict):
    Inventory: Dict[str, int]
    Position: Dict[Literal["center_x", "center_y"], float]


def read_file(filename: str):
    with open(DATAFILES_DIR + filename, "r") as file:
        for line in file:
            yield line.strip()


def write_file(filename: str, data: str, mode: Literal["a", "w"]) -> None:
    with open(DATAFILES_DIR + filename, mode) as file:
        file.write(data)


def write_json(file_name: str, data: dict) -> None:
    with open(DATAFILES_DIR + file_name, "w") as file:
        json.dump(data, file, indent=3)


def store_actual_data(player, actualScene: Literal["FOREST", "LABORATORY"]) -> None:
    if actualScene not in ["FOREST", "LABORATORY"]:
        return
    global game_data, seconds_to_save
    actual_time = time()
    if actual_time - game_data["time_stamp"] < Game.SAVE_INTERVAL:
        return
    data = {
        "player": {
            "position": {
                "center_x": player.sprite.center_x,
                "center_y": player.sprite.center_y,
            },
            "inventory": player.inventory,
            "lifes": player.lifes,
            "healt": player.healt,
        },
        "scene": actualScene,
        "time_stamp": actual_time,
    }
    game_data = data
    write_json(SAVED_FILE, data)


def store_chest_data(new_data: ChestsData, chest_id: str):
    global chests_data
    chests_data[chest_id] = new_data
    write_json(CHEST_FILE, chests_data)


@lru_cache(maxsize=100)
def get_path(file_name: str) -> str:
    """Función que retorna el path absoluto desde la carpeta source al archivo"""
    for base_dir, dirs, files in os.walk(BASE_DIR):
        if file_name in files:
            return os.path.abspath(os.path.join(base_dir, file_name))
    return ""


@lru_cache(maxsize=5)
def get_sound(file_name: str) -> Sound:
    global sounds_loader
    if file_name not in sounds_loader:
        sounds_loader[file_name] = Sound(get_path(file_name))
    return sounds_loader[file_name]
