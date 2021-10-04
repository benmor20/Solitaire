from abc import ABC, abstractmethod
import pygame

from src.model.board import *
import src.utils.constants as constants
from src.model.deck import *


class Sprite(pygame.Surface, ABC):
    def __init__(self, size: Tuple[int, int], transparent: bool = True):
        if transparent:
            super().__init__(size, pygame.SRCALPHA)
        else:
            super().__init__(size)
        self.rect = self.get_rect()

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
            self.blit(large_text, large_text.get_rect(center=self._rect.center))
            small_offset = (3, 0)
            self.blit(small_text, small_text.get_rect(topleft=small_offset))
            self.blit(small_text_rot, small_text_rot.get_rect(bottomright=utils.subtract_tuples(self._rect.bottomright,
                                                                                                small_offset)))
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
        x_size = constants.CARD_SIZE[0] + abs(direction.value[0]) * (num_cards_shown - 1) * constants.NONOVERLAP_HORZ
        y_size = constants.CARD_SIZE[1] + abs(direction.value[1]) * (num_cards_shown - 1) * constants.NONOVERLAP_VERT
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
            pos = (pos[0] + constants.NONOVERLAP_VERT * self._direction.value[0],
                   pos[1] + constants.NONOVERLAP_VERT * self._direction.value[1])


class MultiPileSprite(Sprite, ABC):
    def __init__(self, size: Tuple[int, int]):
        super().__init__(size)
        self._piles: List[Optional[PileSprite]] = []
        self._pile_rects: List[Optional[pygame.rect.Rect]] = []
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
        for index, rect in enumerate(self._pile_rects):
            if rect.collidepoint(click_pos):
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
    def __init__(self, tableau: Tableau, size: Tuple[int, int], locations: List[Tuple[int, int]] = None,
                 stack_direction: PileSprite.StackDirection = PileSprite.StackDirection.DOWN):
        if locations is not None and len(tableau) != len(locations):
            raise ValueError(f'Tableau has {len(tableau)} piles but locations has {len(locations)} spaces given.')
        self._tableau = tableau
        self._locations = locations
        self._stack_direction = stack_direction
        if locations is None:
            location = (0, 0)
            loc_step = (constants.CARD_SIZE[0] + constants.CARD_GAP, 0) if stack_direction.value[0] == 0 else\
                (0, constants.CARD_SIZE[1] + constants.CARD_GAP)
            self._locations = [location]
            for i in range(1, len(tableau)):
                location = utils.add_tuples(location, loc_step)
                self._locations.append(location)
        else:
            self._locations = locations
        super().__init__(size)

    def _update_sprites(self):
        while len(self._piles) < self._tableau.num_piles:
            self._piles.append(None)
            self._pile_rects.append(None)
        pos = 0
        for index in range(self._tableau.num_piles):
            self._piles[index] = PileSprite(self._tableau.peek_all(index), self._stack_direction)
            self._pile_rects[index] = self._piles[index].get_rect(topleft=self._locations[index])


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
