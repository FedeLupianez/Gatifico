import arcade
from enum import Enum

# Clase base para los estados
class State():
    # Va a tener un campo para el path de la sheet y otro para 
    # la cantidad de frames que tiene esta
    def __init__(self, sheetUrl: str, frameCount: int):
        self.sheetUrl = sheetUrl
        self.frameCount = frameCount
        
     
class Character(arcade.Sprite):
    def __init__(self, validStates, textureDict: dict[int, State]):
        self.textureDict = textureDict
        self.frames = None
        self.textureIndex = 0
        self.validStates = validStates
        self.actualState = None
        self.speed = 0
        self.animationTimer = 0
        
        if ('IDLE' in self.validStates.__members__):
            self.changeState(validStates.IDLE)

    def updateSprites(self):
        self.frames = arcade.load_spritesheet(
            file_name=self.textureDict[self.actualState].sheetUrl,
            count=self.textureDict[self.actualState].frameCount
        )
        
    
    def setup(self, width: int, height: int, speed: float):
        if (self.actualState not in self.textureDict):
            raise ValueError("estado no encontrado en el diccionario")

        self.speed = speed


    def changeState(self, newState: str):
        if (newState not in self.validStates):
            raise ValueError(f"El estado {newState} no existe en el personaje")
        # Veo si el estado actual es diferente al nuevo
        if (self.actualState != newState):
            self.actualState = newState
            if (newState in self.textureDict):
                # Cambio el sprite actual al primero del nuevo estado
                self.updateSprites()
        
    def update_animation(self, deltaTime: float):
        if not(self.state in self.textureDict):
            return (False)
        self.animationTimer += deltaTime 
        if (self.animationTimer > 0.1):
            self.animationTimer = 0
            # Obtengo el listado de sprites del estado actual
            frames = self.textureDict[self.actualState]
            self.textureIndex = (self.textureIndex + 1) % len(frames)
            self.set_texture(frames[self.textureIndex])
            self.draw()
            