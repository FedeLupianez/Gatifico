from typing import Callable


class StateMachine:
    def __init__(self):
        self.states: dict[str, Callable[..., str]] = {}
        self.actualState: str = "IDLE"

    def addState(self, name: str, state: Callable):
        self.states[name] = state

    def setState(self, newState: str):
        if newState not in self.states:
            raise ValueError("Estado no encontrado en la maquina")

        self.actualState = newState
        # Aplico los cambios del estado con 0 como neutro
        self.states[self.actualState](0)

    def processState(self, event):
        newState: str = self.states[self.actualState](event)
        if newState == self.actualState:
            print("Permanece en el estado : ", self.actualState)
            return
        print(f"cambiando al estado {newState}")
        self.setState(newState)
