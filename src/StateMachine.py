from typing import Callable


# Clase de maquina de estados reutilizable
class StateMachine:
    # Mejora de manejo de memoria para tener varias instancias
    __slots__ = ["states", "actual_state_id", "last_state_id"]

    def __init__(self, initial_id: str):
        # Diccionario con los estados
        # Estos son funciones
        self.states: dict[str, Callable[..., str]] = {}
        self.actual_state_id: str = initial_id  # Id del estado actual
        self.last_state_id: str = ""

    def add_state(self, id: str, state: Callable):
        """Agrega un estado a la maquina
        Args :
            id (str) : Id del estado
            state (Callable) : Funcion que representa el estado
        """
        self.states[id] = state

    def set_state(self, new_state: str):
        """Cambia el estado actual de la maquina
        Args :
            newState (str) : Id del nuevo estado
        """
        if new_state not in self.states:
            raise ValueError(f"Estado {new_state} no encontrado en la maquina")
        self.last_state_id = self.actual_state_id
        self.actual_state_id = new_state
        # Aplico los cambios del estado con 0 como neutro
        self.states[self.actual_state_id](0)

    def process_state(self, event):
        # Ejecuto el estado actual
        # este debe retornar el estado al que debe cambiar o el mismo
        new_state: str = self.states[self.actual_state_id](event)
        # Si el estado es el mismo no hace ningún cambio
        if new_state == self.actual_state_id:
            return
        # Cambia al nuevo estado
        self.set_state(new_state)
