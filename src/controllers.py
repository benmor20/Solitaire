from abc import ABC, abstractmethod
import pygame
from pygame import locals
from typing import Optional, Union, Tuple

import constants
from models import GameModel, KlondikeModel
from views import PygameView, KlondikeView
from deck import StackingMethod, Pile


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


class PygameController(Controller):
    def __init__(self, model: GameModel, view: PygameView):
        super().__init__(model)
        self._view = view


class KlondikeController(PygameController):
    def __init__(self, model: KlondikeModel, view: KlondikeView):
        super().__init__(model, view)
        self.selected_source: Optional[Union[str, Tuple[str, int]]] = None

    def update(self):
        if len(pygame.event.get(eventtype=locals.MOUSEBUTTONDOWN)) > 0:
            click_info = self._view.get_pile_from_click(pygame.mouse.get_pos())
            if click_info is not None:
                pile, pile_type = click_info
                if pile_type == 'tableau':
                    self._model.selected, remaining = pile.split_by_stackable(1, StackingMethod.ALTERNATING)
                    for index in range(7):
                        if pile == self._model.tableau[index]:
                            self._model.tableau[index] = remaining
                            break
                    self.selected_source = pile_type, index
                elif pile_type == 'draw' and len(self._model.draw_pile) > 0:
                    self._model.selected = Pile(self._model.draw_pile.draw(), visible=True)
                    self.selected_source = pile_type
                elif pile_type == 'deck':
                    self._model.deal()
        elif len(pygame.event.get(eventtype=locals.MOUSEBUTTONUP)):
            if self.selected_source is not None:
                if isinstance(self.selected_source, tuple):
                    self._model.tableau[self.selected_source[1]] = self._model.selected\
                                                                   + self._model.tableau[self.selected_source[1]]
                elif self.selected_source == 'draw':
                    self._model.draw_pile = self._model.selected + self._model.draw_pile
                self._model.selected = None
                self.selected_source = None
