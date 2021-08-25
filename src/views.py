from abc import ABC, abstractmethod
from enum import Enum

import pygame
from pygame import locals
from typing import Tuple, Union

from deck import Rank, Suit, Card, Pile
from models import GameModel, KlondikeModel
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


class CardSprite(pygame.Surface):
    def __init__(self, card: Card, is_visible: bool = True):
        super().__init__(constants.CARD_SIZE, pygame.SRCALPHA)
        self.card = card
        self.is_visible = is_visible
        self.rect = self.get_rect()
        self.draw()

    def draw(self):
        pygame.draw.rect(self, constants.CARD_COLOR, self.rect, border_radius=constants.CARD_RADIUS)
        if self.is_visible:
            text = f'{self.card}'
            color = constants.BLACK if self.card.is_black else constants.RED
            large_text = constants.LARGE_TEXT.render(text, True, color)
            small_text = constants.SMALL_TEXT.render(text, True, color)
            small_text_rot = pygame.transform.rotate(small_text, 180)
            # pygame.transform.rotate(small_text_rot, 180)
            self.blit(large_text, large_text.get_rect(centerx=self.rect.centerx-3, centery=self.rect.centery-3))
            self.blit(small_text, small_text.get_rect(topleft=(0, 0)))
            self.blit(small_text_rot, small_text_rot.get_rect(bottomright=self.rect.bottomright))
        else:
            pygame.draw.rect(self, constants.CARD_BACK, (5, 5, constants.CARD_SIZE[0] - 10,
                                                              constants.CARD_SIZE[1] - 10),
                             border_radius=int(constants.CARD_RADIUS / 2))
        pygame.draw.rect(self, (0, 0, 0), self.rect, width=1, border_radius=constants.CARD_RADIUS)


class PileSprite(pygame.Surface):
    class StackDirection(Enum):
        UP = (0, -1)
        DOWN = (0, 1)
        LEFT = (-1, 0)
        RIGHT = (1, 0)

    def __init__(self, pile: Pile, direction: StackDirection, show_hidden: bool = True, max_shown: int = 0):
        if max_shown <= 0:
            max_shown = len(pile) + max_shown
        total_show = len(pile) - 1 if show_hidden else pile.get_last_visible_index()
        total_show = 0 if total_show is None else total_show
        num_cards_shown = min(total_show + 1, max_shown)
        x_size = constants.CARD_SIZE[0] + abs(direction.value[0]) * (num_cards_shown - 1) * constants.NONOVERLAP_DIST
        y_size = constants.CARD_SIZE[1] + abs(direction.value[1]) * (num_cards_shown - 1) * constants.NONOVERLAP_DIST
        super().__init__((x_size, y_size), pygame.SRCALPHA)
        self.pile = pile
        self.direction = direction
        self.num_cards_shown = num_cards_shown
        self.draw()

    def draw(self):
        increasing = sum(list(self.direction.value)) > 0
        pos = (0, 0) if increasing else\
            (self.get_size()[0] - constants.CARD_SIZE[0], self.get_size()[1] - constants.CARD_SIZE[1])
        for card_index in range(self.num_cards_shown - 1, -1, -1):
            self.blit(CardSprite(self.pile[card_index], self.pile.is_visible(card_index)), pos)
            pos = (pos[0] + constants.NONOVERLAP_DIST * self.direction.value[0],
                   pos[1] + constants.NONOVERLAP_DIST * self.direction.value[1])
