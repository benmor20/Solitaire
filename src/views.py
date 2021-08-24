from abc import ABC, abstractmethod
from models import GameModel


class View(ABC):
    def __init__(self, model: GameModel):
        self._model = model

    @abstractmethod
    def draw(self):
        pass
