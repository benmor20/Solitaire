from abc import ABC, abstractmethod
from enum import Enum

import pygame
from pygame import locals
from typing import Tuple, Union, List, Optional

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
    def get_pile_from_click(self, click_pos: Tuple[int, int]) -> Optional[Tuple[Pile, str, int]]:
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


class CardSprite(pygame.Surface):
    def __init__(self, card: Card, is_visible: bool = True):
        super().__init__(constants.CARD_SIZE, pygame.SRCALPHA)
        self._card = card
        self._is_visible = is_visible
        self._rect = self.get_rect()
        self.draw()

    def draw(self):
        pygame.draw.rect(self, constants.CARD_COLOR, self._rect, border_radius=constants.CARD_RADIUS)
        if self._is_visible:
            text = f'{self._card}'
            color = constants.BLACK if self._card.is_black else constants.RED
            large_text = constants.LARGE_TEXT.render(text, True, color)
            small_text = constants.SMALL_TEXT.render(text, True, color)
            small_text_rot = pygame.transform.rotate(small_text, 180)
            # pygame.transform.rotate(small_text_rot, 180)
            self.blit(large_text, large_text.get_rect(centerx=self._rect.centerx - 3, centery=self._rect.centery - 3))
            self.blit(small_text, small_text.get_rect(topleft=(0, 0)))
            self.blit(small_text_rot, small_text_rot.get_rect(bottomright=self._rect.bottomright))
        else:
            pygame.draw.rect(self, constants.CARD_BACK, (5, 5, constants.CARD_SIZE[0] - 10,
                                                              constants.CARD_SIZE[1] - 10),
                             border_radius=int(constants.CARD_RADIUS / 2))
        pygame.draw.rect(self, (0, 0, 0), self._rect, width=1, border_radius=constants.CARD_RADIUS)


class PileSprite(pygame.Surface):
    class StackDirection(Enum):
        UP = (0, -1)
        DOWN = (0, 1)
        LEFT = (-1, 0)
        RIGHT = (1, 0)

    def __init__(self, pile: Pile, direction: StackDirection = StackDirection.DOWN, show_hidden: bool = True,
                 max_shown: int = 0):
        if max_shown <= 0:
            max_shown = len(pile) + max_shown
        total_show = len(pile) - 1 if show_hidden else pile.get_last_visible_index()
        total_show = 0 if total_show is None else total_show
        num_cards_shown = min(total_show + 1, max_shown)
        x_size = constants.CARD_SIZE[0] + abs(direction.value[0]) * (num_cards_shown - 1) * constants.NONOVERLAP_DIST
        y_size = constants.CARD_SIZE[1] + abs(direction.value[1]) * (num_cards_shown - 1) * constants.NONOVERLAP_DIST
        super().__init__((x_size, y_size), pygame.SRCALPHA)
        self._pile = pile
        self._direction = direction
        self._num_cards_shown = num_cards_shown
        self.draw()

    def draw(self):
        increasing = sum(list(self._direction.value)) > 0
        pos = (0, 0) if increasing else\
            (self.get_size()[0] - constants.CARD_SIZE[0], self.get_size()[1] - constants.CARD_SIZE[1])
        for card_index in range(self._num_cards_shown - 1, -1, -1):
            self.blit(CardSprite(self._pile[card_index], self._pile.is_visible(card_index)), pos)
            pos = (pos[0] + constants.NONOVERLAP_DIST * self._direction.value[0],
                   pos[1] + constants.NONOVERLAP_DIST * self._direction.value[1])


class KlondikeView(PygameView):
    def __init__(self, model: KlondikeModel):
        super().__init__(model)
        self._foundations: List[Optional[PileSprite]] = [None] * 4
        self._found_rects: List[Optional[pygame.rect.Rect]] = [None] * 4
        self._tableau: List[Optional[PileSprite]] = [None] * 7
        self._tab_rects: List[Optional[pygame.rect.Rect]] = [None] * 7
        self._draw_pile: Optional[PileSprite] = None
        self._draw_rect: Optional[pygame.rect.Rect] = None
        self._deck: Optional[PileSprite] = None
        self._deck_rect: Optional[pygame.rect.Rect] = None
        self._board = pygame.Surface((constants.CARD_SIZE[0] * 7 + constants.CARD_GAP * 6, 500), pygame.SRCALPHA)
        self._board_rect = self._board.get_rect(midtop=(self._screen.get_rect().centerx, 100))
        self._selected: Optional[PileSprite] = None
        self._selected_rect: Optional[pygame.rect.Rect] = None
        self._update_sprites()

    def get_pile_from_click(self, click_pos: Tuple[int, int]) -> Optional[Tuple[Pile, str, int]]:
        adj_pos = (click_pos[0] - self._board_rect.left, click_pos[1] - self._board_rect.top)
        for index in range(len(self._foundations)):
            if self._found_rects[index].collidepoint(adj_pos):
                return self._model.foundations[index], 'foundation', index
        for index in range(len(self._tableau)):
            if self._tab_rects[index].collidepoint(adj_pos):
                return self._model.tableau[index], 'tableau', index
        if self._draw_rect.collidepoint(adj_pos):
            return self._model.draw_pile, 'draw', 0
        if self._deck_rect.collidepoint(adj_pos):
            return self._model.deck, 'deck', 0
        return None

    def _update_sprites(self):
        current_pos = (0, 0)
        for index in range(len(self._foundations)):
            self._foundations[index] = PileSprite(self._model.foundations[index], max_shown=1)
            self._found_rects[index] = self._foundations[index].get_rect(topleft=current_pos)
            current_pos = (current_pos[0] + constants.CARD_SIZE[0] + constants.CARD_GAP, current_pos[1])

        current_pos = (self._board_rect.width, 0)
        self._deck = PileSprite(self._model.deck, max_shown=1)
        self._deck_rect = self._deck.get_rect(topright=current_pos)

        current_pos = (current_pos[0] - constants.CARD_SIZE[0] - constants.CARD_GAP, current_pos[1])
        self._draw_pile = PileSprite(self._model.draw_pile, PileSprite.StackDirection.LEFT, max_shown=3)
        self._draw_rect = self._draw_pile.get_rect(topright=current_pos)

        current_pos = (0, current_pos[1] + constants.CARD_SIZE[1] + constants.CARD_GAP * 2)
        for index in range(len(self._tableau)):
            self._tableau[index] = PileSprite(self._model.tableau[index], PileSprite.StackDirection.DOWN)
            self._tab_rects[index] = self._tableau[index].get_rect(topleft=current_pos)
            current_pos = (current_pos[0] + constants.CARD_SIZE[0] + constants.CARD_GAP, current_pos[1])

        if self._model.selected is not None:
            self._selected = PileSprite(self._model.selected, PileSprite.StackDirection.DOWN)
            self._selected_rect = self._selected.get_rect(midtop=pygame.mouse.get_pos())
        else:
            self._selected = None
            self._selected_rect = None

    def _draw(self):
        self._board.fill((0, 0, 0, 0))
        for index in range(len(self._foundations)):
            self._board.blit(self._foundations[index], self._found_rects[index])
        for index in range(len(self._tableau)):
            self._board.blit(self._tableau[index], self._tab_rects[index])
        self._board.blit(self._draw_pile, self._draw_rect)
        self._board.blit(self._deck, self._deck_rect)
        self._screen.blit(self._board, self._board_rect)
        if self._selected is not None:
            self._screen.blit(self._selected, self._selected_rect)
