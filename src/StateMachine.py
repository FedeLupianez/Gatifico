from typing import Callable


# Clase de maquina de estados reutilizable
class StateMachine:
    # Mejora de manejo de memoria para tener varias instancias
    __slots__ = ["states", "actual_state_id", "last_state_id", "unregistered_states"]

    def __init__(self, initial_id: str, unregistered_states: list[str] = []):
        # Diccionario con los estados
        # Estos son funciones
        self.states: dict[str | int, Callable[..., str]] = {}
        self.actual_state_id: str = initial_id  # Id del estado actual
        self.last_state_id: str = self.actual_state_id
        self.unregistered_states: list[str] = unregistered_states

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
        if new_state == self.actual_state_id:
            return
        if self.actual_state_id not in self.unregistered_states:
            self.last_state_id = self.actual_state_id

        self.actual_state_id = new_state
        # Aplico los cambios del estado con 0 como neutro
        self.states[self.actual_state_id](0)

    def process_state(self, event):
        # Ejecuto el estado actual
        # este debe retornar el estado al que debe cambiar o el mismo
        function = self.states[self.actual_state_id]
        new_state: str = function(event)
        if new_state not in self.states:
            raise ValueError(f"Estado {new_state} no encontrado en la maquina")
        # Cambia al nuevo estado
        self.set_state(new_state)
