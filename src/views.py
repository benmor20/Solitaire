from abc import ABC, abstractmethod
import pygame
from pygame import locals
from typing import *

import constants
from sprites import *
from models import GameModel, KlondikeModel


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


class PygameView(View, ABC):
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

    @abstractmethod
    def get_pile_from_click(self, click_pos: Tuple[int, int]) -> Optional[Tuple[str, int]]:
        pass

    def display_game(self):
        if len(pygame.event.get(eventtype=locals.QUIT)) > 0:
            self._model.running = False
        self._screen.fill(self._background)
        self._update_sprites()
        self._draw()
        pygame.display.flip()

    @abstractmethod
    def _update_sprites(self):
        pass

    @abstractmethod
    def _draw(self):
        pass


class KlondikeView(PygameView):
    def __init__(self, model: KlondikeModel):
        super().__init__(model)
        board_width = constants.CARD_SIZE[0] * 7 + constants.CARD_GAP * 6
        self._board = pygame.Surface((board_width, 600), pygame.SRCALPHA)
        self._board_rect = self._board.get_rect(midtop=(int(constants.SCREEN_SIZE[0] / 2), 100))
        self._foundation = FoundationSprite(model.foundation)
        self._foundation_rect = self._foundation.get_rect(topleft=(0, 0))
        self._draw_pile = DrawPileSprite(model.draw_pile)
        self._draw_rect = self._draw_pile.get_rect(topright=(board_width, 0))
        self._tableau = TableauSprite(model.tableau)
        self._tableau_rect = self._tableau.get_rect(topleft=(0, constants.CARD_SIZE[1] + constants.CARD_GAP * 2))

    def get_pile_from_click(self, click_pos: Tuple[int, int]) -> Optional[Tuple[str, int]]:
        adj_pos = utils.subtract_tuples(click_pos, self._board_rect.topleft)
        if self._foundation_rect.collidepoint(adj_pos):
            index = self._foundation.pile_index_from_pos(utils.subtract_tuples(adj_pos, self._foundation_rect.topleft))
            if index is None:
                return None
            else:
                return 'foundation', index
        elif self._tableau_rect.collidepoint(adj_pos):
            index = self._tableau.pile_index_from_pos(utils.subtract_tuples(adj_pos, self._tableau_rect.topleft))
            if index is None:
                return None
            else:
                return 'tableau', index
        elif self._draw_rect.collidepoint(adj_pos):
            index = self._draw_pile.pile_index_from_pos(utils.subtract_tuples(adj_pos, self._draw_rect.topleft))
            if index is None:
                return None
            elif index == 0:
                return 'draw', 0
            elif index == 1:
                return 'deck', 0
        return None

    def _update_sprites(self):
        self._foundation.draw()
        self._foundation_rect = self._foundation.get_rect(topleft=(0, 0))
        self._draw_pile.draw()
        self._draw_rect = self._draw_pile.get_rect(topright=(self._board_rect.width, 0))
        self._tableau.draw()
        self._tableau_rect = self._tableau.get_rect(topleft=(0, constants.CARD_SIZE[1] + constants.CARD_GAP * 2))

    def _draw(self):
        self._board.fill((0, 0, 0, 0))
        self._board.blit(self._foundation, self._foundation_rect)
        self._board.blit(self._draw_pile, self._draw_rect)
        self._board.blit(self._tableau, self._tableau_rect)
        self._screen.blit(self._board, self._board_rect)
        if self._model.selected is not None:
            selected = PileSprite(self._model.selected[0])
            self._screen.blit(selected, selected.get_rect(midtop=pygame.mouse.get_pos()))
