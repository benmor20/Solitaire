import copy
from enum import Enum
import random
from typing import List, Union, Optional, Tuple


class Suit(Enum):
    SPADES = "♠", True
    HEARTS = "♥", False
    CLUBS = "♣", True
    DIAMONDS = "♦", False

    def __init__(self, symbol: str, is_black: bool):
        self.symbol = symbol
        self.is_black = is_black

    def __str__(self) -> str:
        return self.symbol

    def __repr__(self) -> str:
        return self.symbol


class Rank(Enum):
    ACE_LOW = " A", 1
    TWO = " 2", 2
    THREE = " 3", 3
    FOUR = " 4", 4
    FIVE = " 5", 5
    SIX = " 6", 6
    SEVEN = " 7", 7
    EIGHT = " 8", 8
    NINE = " 9", 9
    TEN = "10", 10
    JACK = " J", 11
    QUEEN = " Q", 12
    KING = " K", 13
    ACE_HIGH = " A", 14

    def __init__(self, abbv: str, rank: int):
        self.abbv = abbv
        self.rank = rank

    def __lt__(self, other: Union['Card', 'Rank']) -> bool:
        return self.rank < other.rank

    def __gt__(self, other: Union['Card', 'Rank']) -> bool:
        return self.rank > other.rank

    def __le__(self, other: Union['Card', 'Rank']) -> bool:
        return self.rank <= other.rank

    def __ge__(self, other: Union['Card', 'Rank']) -> bool:
        return self.rank >= other.rank

    def __eq__(self, other: Union['Card', 'Rank']) -> bool:
        return self.rank == other.rank

    def __int__(self):
        return self.rank

    def __str__(self):
        return self.abbv

    def __repr__(self):
        return self.abbv


class SuitStackMethod(Enum):
    ALTERNATING = 0,
    COLOR = 1,
    SUIT = 2,

class StackingMethod:
    def __init__(self, rank_diff: Optional[int], suit_method: Optional[SuitStackMethod]):
        self.rank_diff = rank_diff
        self.suit_method = suit_method


class Card:
    def __init__(self, suit: Suit, rank: Rank):
        self.suit = suit
        self.rank = rank

    @property
    def is_black(self) -> bool:
        return self.suit.is_black

    def can_stack_on(self, card: Union['Card', 'Pile'], method: StackingMethod) -> bool:
        if isinstance(card, Pile):
            if not card.is_visible(0):
                return False
            card = card[0]
        if method.rank_diff is not None and card - self != method.rank_diff:
            return False
        if method.suit_method == SuitStackMethod.ALTERNATING:
            return self.is_black ^ card.is_black
        elif method.suit_method == SuitStackMethod.COLOR:
            return self.is_black == card.is_black
        elif method.suit_method == SuitStackMethod.SUIT:
            return self.suit == card.suit
        return True

    def __sub__(self, other: 'Card') -> int:
        return int(self.rank) - int(other.rank)

    def __lt__(self, other: Union['Card', Rank]) -> bool:
        return self.rank < other.rank

    def __gt__(self, other: Union['Card', Rank]) -> bool:
        return self.rank > other.rank

    def __le__(self, other: Union['Card', Rank]) -> bool:
        return self.rank <= other.rank

    def __ge__(self, other: Union['Card', Rank]) -> bool:
        return self.rank >= other.rank

    def __eq__(self, other: Union['Card', Rank]) -> bool:
        if isinstance(other, Rank):
            return self.rank == other.rank
        return self.rank == other.rank and self.suit == other.suit

    def __int__(self) -> int:
        return int(self.rank)

    def __str__(self) -> str:
        return str(self.rank) + str(self.suit)

    def __repr__(self) -> str:
        return str(self)

    def __copy__(self) -> 'Card':
        return Card(self.suit, self.rank)


class Pile:
    def __init__(self, start_card: Union[Card, List[Card]] = None, aces_high: bool = False, start_full: bool = False,
                 shuffled: bool = True, visible: bool = False):
        self._cards = []
        if start_card is not None:
            if isinstance(start_card, Card):
                self._cards.append(copy.copy(start_card))
            elif isinstance(start_card, list):
                for card in start_card:
                    self._cards.append(copy.copy(card))
        elif start_full:
            for suit in Suit:
                for rank in Rank:
                    if (aces_high and rank == Rank.ACE_LOW) or (not aces_high and rank == Rank.ACE_HIGH):
                        continue
                    self._cards.append(Card(suit, rank))
            if shuffled:
                self.shuffle()
        self._visible_cards = set()
        if visible:
            for card in range(len(self._cards)):
                self._visible_cards.add(card)
        self._aces_high = aces_high

    @property
    def aces_high(self):
        return self._aces_high

    def shuffle(self):
        random.shuffle(self._cards)

    def draw(self, num_cards: int = 1) -> Optional[Union[Card, 'Pile']]:
        if len(self) == 0:
            return None
        if num_cards < 1:
            num_cards = len(self) + num_cards
        if num_cards == 1:
            card = self._cards[0]
            self._cards.remove(card)
            if 0 in self._visible_cards:
                self._visible_cards.remove(0)
            for index in range(1, len(self) + 1):
                if index in self._visible_cards:
                    self._visible_cards.remove(index)
                    self._visible_cards.add(index - 1)
            return card
        else:
            pile = Pile()
            pile = self.move_to(pile, num_cards)
            return pile

    def peek(self, num_cards: int = 1) -> Optional[Union[Card, 'Pile']]:
        if len(self) == 0:
            return None
        if num_cards == 1:
            return self[0]
        else:
            pile = Pile()
            for card in range(num_cards):
                pile += Pile(self[card], visible=self.is_visible(card))
            return pile

    def move_to(self, pile: 'Pile', num_cards: int = 1) -> 'Pile':
        for _ in range(num_cards):
            visible = 0 in self._visible_cards
            pile += Pile(self.draw(), visible=visible)
        return pile

    def flip(self, card: int):
        if card < 0:
            card = len(self) + card
        if card in self._visible_cards:
            self.make_hidden(card)
        else:
            self.make_visible(card)

    def flip_all(self):
        for index in range(len(self)):
            self.flip(index)

    def make_visible(self, card: int):
        if card < 0:
            card = len(self) + card
        self._visible_cards.add(card)

    def reveal_all(self):
        for index in range(len(self)):
            self.make_visible(index)

    def make_hidden(self, card: int):
        if card < 0:
            card = len(self) + card
        if card in self._visible_cards:
            self._visible_cards.remove(card)

    def hide_all(self):
        for index in range(len(self)):
            self.make_hidden(index)

    def is_visible(self, card: int) -> bool:
        if card < 0:
            card = len(self) + card
        return card in self._visible_cards

    def get_last_visible_index(self) -> Optional[int]:
        prev_card_index = None
        for card_index in range(len(self._cards)):
            if not self.is_visible(card_index):
                break
            prev_card_index = card_index
        return prev_card_index

    def get_last_visible(self) -> Optional[Card]:
        last_index = self.get_last_visible_index()
        return None if last_index is None else self[last_index]

    def split_by_visible(self) -> Tuple['Pile', 'Pile']:
        pile1, pile2 = Pile(aces_high=self.aces_high), Pile(aces_high=self.aces_high)
        last_vis = self.get_last_visible_index()
        last_vis = -1 if last_vis is None else last_vis
        for index in range(last_vis + 1):
            pile1 += Pile(self[index], visible=index in self._visible_cards)
        for index in range(last_vis + 1, len(self)):
            pile2 += Pile(self[index], visible=index in self._visible_cards)
        return pile1, pile2

    def split_by_stackable(self, method: StackingMethod)\
            -> Tuple['Pile', 'Pile']:
        pile1, pile2 = Pile(aces_high=self.aces_high), Pile(aces_high=self.aces_high)
        prev_card: Optional[Card] = None
        index = -1
        for index in range(len(self)):
            card = self[index]
            if prev_card is None or prev_card.can_stack_on(card, method):
                pile1 += Pile(card, visible=index in self._visible_cards)
            else:
                break
            prev_card = card
        if len(pile1) < len(self):
            for index2 in range(index, len(self)):
                pile2 += Pile(self[index2], visible=index2 in self._visible_cards)
        return pile1, pile2

    def can_stack_on(self, card: Union[Card, 'Pile'], method: StackingMethod) -> bool:
        prev_card = None
        for card_index in range(len(self)):
            curr_card = self[card_index]
            if not self.is_visible(card_index):
                return False
            if prev_card is not None and not prev_card.can_stack_on(curr_card, method):
                return False
            if curr_card.can_stack_on(card, method):
                return True
            prev_card = curr_card
        return False

    def __len__(self) -> int:
        return len(self._cards)

    def __getitem__(self, item: int) -> Card:
        return self._cards[item]

    def __add__(self, other: 'Pile') -> 'Pile':
        new_pile = Pile(aces_high=self.aces_high)
        for index in range(len(self)):
            new_pile._cards.append(self[index])
            if self.is_visible(index):
                new_pile.make_visible(index)
        else:
            for index in range(len(other)):
                new_pile._cards.append(other[index])
                if other.is_visible(index):
                    new_pile.make_visible(index + len(self))
        return new_pile

    def __contains__(self, item: Card):
        return item in self._cards

    def __str__(self):
        s = ""
        for index in range(len(self._cards)):
            s += f'{self[index]}{"V" if index in self._visible_cards else "H"} '
        return s[:-1]

    def __repr__(self):
        return str(self)

    def __copy__(self):
        copy = Pile(start_card=self._cards, aces_high=self.aces_high)
        for vis in self._visible_cards:
            copy.make_visible(vis)
        return copy

    def __reversed__(self) -> 'Pile':
        rev = Pile(aces_high=self.aces_high)
        for index in range(len(self)):
            rev = Pile(self[index], visible=index in self._visible_cards) + rev
        return rev

    def deal_between(self, piles: Union[int, List['Pile']], num_cards: int = None) -> List['Pile']:
        if num_cards is None:
            num_cards = len(self)
        elif num_cards < 0:
            num_cards = len(self) + num_cards
        if isinstance(piles, int):
            num_piles = piles
            piles = []
            for _ in range(num_piles):
                piles.append(Pile(aces_high=self.aces_high))
        else:
            num_piles = len(piles)
        for card_num in range(num_cards):
            piles[card_num % num_piles] += self.draw()
        return piles
