from abc import ABC, abstractmethod
import pygame
from typing import *

from board import *
import constants
from deck import *


class Sprite(pygame.Surface, ABC):
    def __init__(self, size: Tuple[int, int], transparent: bool = True):
        if transparent:
            super().__init__(size, pygame.SRCALPHA)
        else:
            super().__init__(size)

    @abstractmethod
    def draw(self):
        pass


class CardSprite(Sprite):
    def __init__(self, card: Card, is_visible: bool = True):
        super().__init__(constants.CARD_SIZE)
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
            self.blit(large_text, large_text.get_rect(centerx=self._rect.centerx - 3, centery=self._rect.centery - 3))
            self.blit(small_text, small_text.get_rect(topleft=(0, 0)))
            self.blit(small_text_rot, small_text_rot.get_rect(bottomright=self._rect.bottomright))
        else:
            pygame.draw.rect(self, constants.CARD_BACK, (5, 5, constants.CARD_SIZE[0] - 10,
                                                         constants.CARD_SIZE[1] - 10),
                             border_radius=int(constants.CARD_RADIUS / 2))
        pygame.draw.rect(self, (0, 0, 0), self._rect, width=1, border_radius=constants.CARD_RADIUS)


class PileSprite(Sprite):
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
        super().__init__((x_size, y_size))
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


class MultiPileSprite(Sprite, ABC):
    def __init__(self, size: Tuple[int, int]):
        super().__init__(size)
        self._piles: List[PileSprite] = []
        self._pile_rects: List[pygame.rect.Rect] = []
        self.draw()

    @abstractmethod
    def _update_sprites(self):
        pass

    def draw(self):
        self._update_sprites()
        self.fill((0, 0, 0, 0))
        for index in range(len(self._piles)):
            self.blit(self._piles[index], self._pile_rects[index])

    def pile_index_from_pos(self, click_pos) -> Optional[int]:
        for index in range(len(self._pile_rects)):
            if self._pile_rects[index].collidepoint(click_pos):
                return index
        return None


class FoundationSprite(MultiPileSprite):
    def __init__(self, foundation: Foundation):
        self._foundation = foundation
        super().__init__((constants.CARD_SIZE[0] * 4 + constants.CARD_GAP * 3, constants.CARD_SIZE[1]))

    def _update_sprites(self):
        while len(self._piles) < 4:
            self._piles.append(None)
            self._pile_rects.append(None)
        pos = 0
        for index in range(4):
            self._piles[index] = PileSprite(Pile(self._foundation.peek(index), visible=True))
            self._pile_rects[index] = self._piles[index].get_rect(topleft=(pos, 0))
            pos += constants.CARD_SIZE[0] + constants.CARD_GAP


class TableauSprite(MultiPileSprite):
    def __init__(self, tableau: Tableau):
        self._tableau = tableau
        super().__init__((constants.CARD_SIZE[0] * tableau.num_piles + constants.CARD_GAP * (tableau.num_piles - 1),
                          500))

    def _update_sprites(self):
        # print(f'updating tableau')
        while len(self._piles) < self._tableau.num_piles:
            self._piles.append(None)
            self._pile_rects.append(None)
        pos = 0
        for index in range(self._tableau.num_piles):
            # print(f'Length of tableau {index} is {self._tableau.pile_len(index)}')
            self._piles[index] = PileSprite(self._tableau.peek_all(index))
            self._pile_rects[index] = self._piles[index].get_rect(topleft = (pos, 0))
            pos += constants.CARD_SIZE[0] + constants.CARD_GAP


class DrawPileSprite(MultiPileSprite):
    def __init__(self, draw_pile: DrawPile):
        self._draw_pile = draw_pile
        super().__init__((constants.CARD_SIZE[0] * 2 + constants.NONOVERLAP_DIST * 2 + constants.CARD_GAP,
                          constants.CARD_SIZE[1]))

    def _update_sprites(self):
        while len(self._piles) < 2:
            self._piles.append(None)
            self._pile_rects.append(None)
        draw = self._draw_pile.peek()
        self._piles[0] = PileSprite(Pile() if draw is None else draw, PileSprite.StackDirection.LEFT, max_shown=3)
        if self._draw_pile.deck_length > 0:
            self._piles[1] = PileSprite(Pile(Card(Suit.SPADES, Rank.ACE_LOW)))
        else:
            self._piles[1] = PileSprite(Pile())
        self._pile_rects[0] = self._piles[0].get_rect(topleft=(0, 0))
        self._pile_rects[1] = self._piles[1].get_rect(topright=(self.get_size()[0], 0))
