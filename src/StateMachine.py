from typing import Callable


# Clase de maquina de estados reutilizable
class StateMachine:
    # Mejora de manejo de memoria para tener varias instancias
    __slots__ = ["states", "actualStateId", "lastStateId"]

    def __init__(self):
        # Diccionario con los estados
        # Estos son funciones
        self.states: dict[str, Callable[..., str]] = {}
        self.actualStateId: str = "IDLE"  # Id del estado actual
        self.lastStateId: str = ""

    def addState(self, id: str, state: Callable):
        """Agrega un estado a la maquina
        Args :
            id (str) : Id del estado
            state (Callable) : Funcion que representa el estado
        """
        self.states[id] = state

    def setState(self, newState: str):
        """Cambia el estado actual de la maquina
        Args :
            newState (str) : Id del nuevo estado
        """
        if newState not in self.states:
            raise ValueError("Estado no encontrado en la maquina")
        self.lastStateId = self.actualStateId
        self.actualStateId = newState
        # Aplico los cambios del estado con 0 como neutro
        self.states[self.actualStateId](0)

    def processState(self, event):
        # Ejecuto el estado actual
        # este debe retornar el estado al que debe cambiar o el mismo
        newState: str = self.states[self.actualStateId](event)
        # Si el estado es el mismo no hace ningún cambio
        if newState == self.actualStateId:
            return
        # Cambia al nuevo estado
        print(f"cambiando al estado {newState}")
        self.setState(newState)
