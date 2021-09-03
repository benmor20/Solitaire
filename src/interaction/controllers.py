from abc import ABC, abstractmethod
import pygame
from pygame import locals
import time
from typing import Optional

import src.utils.constants as constants
from src.model.deck import Pile
from src.model.models import GameModel, KlondikeModel
from src.interaction.views import PygameView, KlondikeView


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
            self._last_move_frame = self._current_frame
            moved = self._move()
            if not moved:
                self._model.running = False

    @abstractmethod
    def _move(self) -> bool:
        pass


class PygameController(Controller):
    def __init__(self, model: GameModel, view: PygameView):
        super().__init__(model)
        self._view = view


class KlondikeController(PygameController):
    def __init__(self, model: KlondikeModel, view: KlondikeView):
        super().__init__(model, view)
        self._start_click: Optional[int] = None

    def update(self):
        if len(pygame.event.get(eventtype=locals.MOUSEBUTTONDOWN)) > 0:
            click_info = self._view.get_pile_from_click(pygame.mouse.get_pos())
            if click_info is not None:
                pile_type, pile_index = click_info
                self._model.pickup(pile_type, pile_index)
                self._start_click = time.time()
        elif len(pygame.event.get(eventtype=locals.MOUSEBUTTONUP)):
            if self._start_click is not None:
                if self._model.selected is None:  # This means pickup failed and therefore the user selected the deck
                    self._model.on_select('deck', 0)
                elif time.time() - self._start_click < 0.2:
                    _, pile_type, pile_index = self._model.selected
                    self._model.replace_selected()
                    self._model.on_select(pile_type, pile_index)
                else:
                    click_info = self._view.get_pile_from_click(pygame.mouse.get_pos())
                    if click_info is not None:
                        pile_type, pile_index = click_info
                        success = self._model.set_down_on(pile_type, pile_index)
                    else:
                        self._model.replace_selected()
                self._start_click = None


class KlondikeAIController(AIController):
    def __init__(self, model: KlondikeModel, view: KlondikeView):
        super().__init__(model)
        self._view = view

    def _move(self):
        for tab_index in range(7):
            if self._model.on_select('tableau', tab_index):
                return True
        if self._model.on_select('draw', 0):
            return True
        self._model.on_select('deck', 0)
        return True
