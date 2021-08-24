from abc import ABC, abstractmethod
import constants
from models import GameModel


class Controller:
    def __init__(self, model: GameModel):
        self._model = model
        self._current_frame = 0

    def update(self):
        self._current_frame += 1


class PlayerController(Controller):
    def __init__(self, model: GameModel):
        super().__init__(model)


class AIController(Controller, ABC):
    def __init__(self, model: GameModel, wait_time: float = 0.2):
        super().__init__(model)
        self._wait_frames = wait_time * constants.FPS
        self._last_move_frame = 0

    @property
    def can_move(self) -> bool:
        return self._last_move_frame + self._wait_frames <= self._current_frame

    def update(self):
        super().update()
        if self.can_move:
            self._move()

    @abstractmethod
    def _move(self):
        pass
