from enum import Enum
import random
from typing import List, Union


class Suit(Enum):
    SPADES = "♠"
    HEARTS = "♡"
    CLUBS = "♣"
    DIAMONDS = "♢"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


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

    def __lt__(self, other: Union['Card', 'Rank']):
        return self.rank < other.rank

    def __gt__(self, other: Union['Card', 'Rank']):
        return self.rank > other.rank

    def __le__(self, other: Union['Card', 'Rank']):
        return self.rank <= other.rank

    def __ge__(self, other: Union['Card', 'Rank']):
        return self.rank >= other.rank

    def __eq__(self, other: Union['Card', 'Rank']):
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

    def __add__(self, other: 'Pile'):
        pile = Pile(start_card=self, aces_high=other.aces_high)
        pile += other
        return pile

    def __lt__(self, other: Union['Card', Rank]):
        return self.rank < other.rank

    def __gt__(self, other: Union['Card', Rank]):
        return self.rank > other.rank

    def __le__(self, other: Union['Card', Rank]):
        return self.rank <= other.rank

    def __ge__(self, other: Union['Card', Rank]):
        return self.rank >= other.rank

    def __eq__(self, other: Union['Card', Rank]):
        return self.rank == other.rank

    def __int__(self):
        return self.rank

    def __str__(self):
        return str(self.rank) + str(self.suit)

    def __repr__(self):
        return str(self)


class Pile:
    def __init__(self, start_card: Union[Card, List[Card]] = None, aces_high: bool = False, start_full: bool = False,
                 shuffled: bool = True):
        self._cards = []
        if start_card is not None:
            if isinstance(start_card, Card):
                self._cards.append(start_card)
            elif isinstance(start_card, list):
                for card in start_card:
                    self._cards.append(card)
        elif start_full:
            for suit in Suit:
                for rank in Rank:
                    if (aces_high and rank == Rank.ACE_LOW) or (not aces_high and rank == Rank.ACE_HIGH):
                        continue
                    self._cards.append(Card(suit, rank))
            if shuffled:
                self.shuffle()
        self._aces_high = aces_high

    @property
    def aces_high(self):
        return self._aces_high

    def shuffle(self):
        random.shuffle(self._cards)

    def draw(self) -> Card:
        card = self._cards[0]
        self._cards.remove(card)
        return card

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
