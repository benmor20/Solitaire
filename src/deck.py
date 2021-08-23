import copy
from enum import Enum
import random
from typing import List, Union, Optional


class Suit(Enum):
    SPADES = "♠", True
    HEARTS = "♡", False
    CLUBS = "♣", True
    DIAMONDS = "♢", False

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


class Card:
    def __init__(self, suit: Suit, rank: Rank):
        self.suit = suit
        self.rank = rank

    @property
    def is_black(self) -> bool:
        return self.suit.is_black

    def __add__(self, other: 'Pile') -> 'Pile':
        pile = Pile(start_card=self, aces_high=other.aces_high)
        pile += other
        return pile

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
        if visible:
            self._visible_cards = set()
            for card in self._cards:
                self._visible_cards.add(card)
        self._aces_high = aces_high

    @property
    def aces_high(self):
        return self._aces_high

    def shuffle(self):
        random.shuffle(self._cards)

    def draw(self, num_cards: int = 1) -> Union[Card, 'Pile']:
        if num_cards == 1:
            card = self._cards[0]
            self._cards.remove(card)
            self._visible_cards.remove(card)
            return card
        else:
            pile = Pile()
            self.add_to(pile, num_cards)
            return pile

    def peek(self, num_cards: int = 1) -> Union[Card, 'Pile']:
        if num_cards == 1:
            return self[0]
        else:
            pile = Pile()
            for card in range(num_cards):
                pile += self[card]
                if self.is_visible(card):
                    pile.make_visible(card)
            return pile

    def add_to(self, pile: 'Pile', num_cards: int = 1):
        for _ in range(num_cards):
            card = self.peek()
            pile += card
            if card in self._visible_cards:
                pile.make_visible(card)
            self.draw()

    def flip(self, card: Union[int, Card]):
        if isinstance(card, int):
            card = self._cards[card]
        if card in self._visible_cards:
            self.make_hidden(card)
        else:
            self.make_visible(card)

    def make_visible(self, card: Union[int, Card]):
        if isinstance(card, int):
            card = self._cards[card]
        self._visible_cards.add(card)

    def make_hidden(self, card: Union[int, Card]):
        if isinstance(card, int):
            card = self._cards[card]
        self._visible_cards.remove(card)

    def is_visible(self, card: Union[int, Card]) -> bool:
        if isinstance(card, int):
            card = self._cards[card]
        return card in self._visible_cards

    def get_last_visible(self) -> Optional[Card]:
        prev_card = None
        for card in self._cards:
            if not self.is_visible(card):
                break
            prev_card = card
        return prev_card

    def __len__(self) -> int:
        return len(self._cards)

    def __getitem__(self, item: int) -> Card:
        return self._cards[item]

    def __add__(self, other: Union[Card, 'Pile']) -> 'Pile':
        new_pile = Pile(aces_high=self.aces_high)
        for card in self._cards:
            new_pile._cards.append(card)
        if isinstance(other, Card):
            new_pile._cards.append(other)
        else:
            for card in other._cards:
                new_pile._cards.append(card)
        return new_pile

    def __contains__(self, item: Card):
        return item in self._cards

    def __str__(self):
        s = ""
        for card in self._cards:
            s += f'{card} '
        return s[:-1]

    def __repr__(self):
        return str(self)

    def __copy__(self):
        copy = Pile(start_card=self._cards, aces_high=self.aces_high)
        for vis in self._visible_cards:
            copy.make_visible(vis)
        return copy

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
