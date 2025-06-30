# En este archivo vamos a poder manejar la lógica detras del guardado de datos.
# Por ejemplo, para guardar el nivel  items que tiene el usuario si se sale del juego
# o al cambiar de escena, aula, etc.

import json
import os

BASE_DIR = os.path.dirname(__file__)
MineralResourcesPath = os.path.join(BASE_DIR, "resources", "Data", "Minerals.json")


class DataManager:
    def __init__(self):
        pass

    def loadData(self, path: str) -> dict:
        with open(path, "r") as file:
            return json.load(file)


dataManager = DataManager()
