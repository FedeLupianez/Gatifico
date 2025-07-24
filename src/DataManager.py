# En este archivo vamos a poder manejar la lógica detras del guardado de datos.
# Por ejemplo, para guardar el nivel  items que tiene el usuario si se sale del juego
# o al cambiar de escena, aula, etc.

import json
import os
from Types import ChestsData, PlayerData

BASE_DIR = os.path.dirname(__file__)
DATAFILES_DIR = BASE_DIR + "/resources/Data/"

test_chests: ChestsData = {
    "chest_1": {"rubi": 4, "rock": 3},
    "chest_2": {},
    "chest_3": {},
}


def loadData(filename: str) -> dict:
    with open(DATAFILES_DIR + filename, "r") as file:
        return json.load(file)


game_data: dict = loadData("GameData.json")


def storeGameData(playerData: PlayerData, actualScene) -> None:
    global game_data
    print(playerData)
    with open(DATAFILES_DIR + "GameData.json", "w") as file:
        data = {
            "player": {
                "position": {
                    "center_x": playerData["Position"]["center_x"],
                    "center_y": playerData["Position"]["center_y"],
                },
                "inventory": playerData["Inventory"],
            },
            "scene": actualScene,
            "chests": test_chests,
        }
        game_data = data
        json.dump(data, file)
