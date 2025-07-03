# En este archivo vamos a poder manejar la lógica detras del guardado de datos.
# Por ejemplo, para guardar el nivel  items que tiene el usuario si se sale del juego
# o al cambiar de escena, aula, etc.

import json
import os

BASE_DIR = os.path.dirname(__file__)
DATAFILES_DIR = BASE_DIR + "/resources/Data/"


def loadData(filename: str) -> dict:
    with open(DATAFILES_DIR + filename, "r") as file:
        return json.load(file)
