from abc import ABC, abstractmethod
import pygame
from pygame import locals
from typing import Tuple, Union

from models import GameModel
import constants


class View(ABC):
    def __init__(self, model: GameModel):
        self._model = model

    def setup(self):
        return

    @abstractmethod
    def display_game(self):
        pass

    def teardown(self):
        return


class PygameView(View):
    def __init__(self, model: GameModel, screen: Union[Tuple[int], pygame.Surface] = constants.SCREEN_SIZE,
                 default_background: Tuple[int] = constants.BACKGROUND_COLOR):
        super().__init__(model)
        if not pygame.get_init():
            pygame.init()
        self._screen = screen if isinstance(screen, pygame.Surface) else pygame.display.set_mode(screen)
        self._background = default_background

    @property
    def screen(self):
        return self._screen

    def display_game(self):
        for event in pygame.event.get():
            if event.type == locals.QUIT:
                self._model.running = False
        self._screen.fill(self._background)
        self._draw()
        pygame.display.flip()

    def _draw(self):
        return
