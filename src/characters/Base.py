import arcade


# Clase base para los estados
class State:
    # Va a tener un campo para el path de la sheet y otro para
    # la cantidad de frames que tiene esta
    def __init__(self, sheetUrl: str, frameCount: int, scale: int):
        self.texturePath: str = sheetUrl
        self.frameCount: int = frameCount
        self.scale = scale


class Character(arcade.Sprite):
    def __init__(self, validStates, initialState, statesDict: dict):
        super().__init__()
        self.validStates = validStates
        self.actualState = None
        self.statesInfo = statesDict
        self.frames = []
        self.textureIndex = 1
        self.animationTimer = 0
        self.changeState(initialState)

    def updateSpriteList(self):
        for i in range(1, self.statesInfo[self.actualState].frameCount + 1):
            route = self.statesInfo[self.actualState].texturePath.replace("{}", str(i))
            self.frames.append(arcade.load_texture(route))
        self.textureIndex = 1

    def updateFrame(self):
        self.texture = self.frames[self.textureIndex]

    def changeState(self, newState):
        print(f"cambiando a {newState}...")
        if newState not in self.validStates:
            raise ValueError(f"El estado {newState} no existe en el personaje")

        # Veo si el estado actual es diferente al nuevo
        if self.actualState == newState:
            return

        self.actualState = newState
        self.scale = self.statesInfo[newState].scale

        self.updateSpriteList()
        self.updateFrame()
        # Cambio el sprite actual al primero del nuevo estado

    def update_animation(self, deltaTime: float):
        if not self.frames:
            return
        self.animationTimer += deltaTime
        if self.animationTimer > 0.1:
            self.animationTimer = 0
            self.textureIndex = (self.textureIndex + 1) % len(self.frames)
            self.texture = self.frames[self.textureIndex]
