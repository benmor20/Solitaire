from enum import Enum
from random import shuffle


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

    def __lt__(self, other):
        return self.rank < other.rank

    def __gt__(self, other):
        return self.rank > other.rank

    def __le__(self, other):
        return self.rank <= other.rank

    def __ge__(self, other):
        return self.rank >= other.rank

    def __eq__(self, other):
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

    def __lt__(self, other):
        return self.rank < other.rank

    def __gt__(self, other):
        return self.rank > other.rank

    def __le__(self, other):
        return self.rank <= other.rank

    def __ge__(self, other):
        return self.rank >= other.rank

    def __eq__(self, other):
        return self.rank == other.rank

    def __int__(self):
        return self.rank

    def __str__(self):
        return str(self.rank) + str(self.suit)

    def __repr__(self):
        return str(self)


class Deck:
    def __init__(self, shuffled: bool = True, aces_high: bool = False):
        self.cards = []
        for suit in Suit:
            for rank in Rank:
                if (aces_high and rank == Rank.ACE_LOW) or (not aces_high and rank == Rank.ACE_HIGH):
                    continue
                self.cards.append(Card(suit, rank))
        if shuffled:
            shuffle(self.cards)

    def __len__(self):
        return len(self.cards)

    def __getitem__(self, item):
        return self.cards[item]
