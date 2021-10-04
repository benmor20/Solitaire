from abc import ABC, abstractmethod
import pygame
from pygame import locals
import time
from typing import Optional

import src.utils.constants as constants
from src.model.deck import *
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
    def __init__(self, model: GameModel, wait_time: float = 0):
        super().__init__(model)
        self._wait_frames = wait_time * constants.FPS
        self._last_move_frame = 0
        self._paused = False

    @property
    def can_move(self) -> bool:
        return not self._paused and self._last_move_frame + self._wait_frames <= self._current_frame

    def update(self):
        super().update()
        for event in pygame.event.get(locals.KEYUP):
            if event.key == locals.K_p:
                self._paused = not self._paused
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
                    self._model.on_select('draw', 1)
                elif time.time() - self._start_click < constants.SELECT_TIME:
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
        self._num_reshuffle_since_last_move = 0

    def _move(self):
        for src_index, src in enumerate(self._model.tableau):
            pile, remaining = src.split_by_stackable(self._model.stacking_method)
            for dest_index, dest in enumerate(self._model.tableau):
                if pile.can_stack_on(dest.peek(), self._model.stacking_method)\
                        and (len(remaining) > 0 or pile[-1].rank != Rank.KING)\
                        and (dest.peek() is None or dest.peek().rank > pile[-1].rank):
                    self._model.pickup('tableau', src_index)
                    self._model.set_down_on('tableau', dest_index)
                    self._num_reshuffle_since_last_move = 0
                    return True

        if self._model.draw_pile.num_visible > 0:
            for dest_index, dest in enumerate(self._model.tableau):
                if self._model.draw_pile.peek()[0].can_stack_on(dest, self._model.stacking_method):
                    self._model.pickup('draw', 0)
                    self._model.set_down_on('tableau', dest_index)
                    self._num_reshuffle_since_last_move = 0
                    return True

        for tab_index in range(7):
            if self._model.on_select('tableau', tab_index):
                self._num_reshuffle_since_last_move = 0
                return True

        if self._model.on_select('draw', 0):
            self._num_reshuffle_since_last_move = 0
            return True

        if self._model.draw_pile.deck_length == 0:
            if self._num_reshuffle_since_last_move == 2:
                print('No more moves')
                return False
            self._num_reshuffle_since_last_move += 1
        self._model.on_select('draw', 1)
        return True
