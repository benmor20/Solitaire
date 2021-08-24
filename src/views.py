from abc import ABC, abstractmethod
from models import GameModel, TestModel


class View(ABC):
    def __init__(self, model: GameModel):
        self._model = model

    @abstractmethod
    def draw(self):
        pass

class TestView(View):
    def __init__(self, model: TestModel):
        super().__init__(model)

    def draw(self):
        if self._model.key_pressed:
            print("Key pressed")
