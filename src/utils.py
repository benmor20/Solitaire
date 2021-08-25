from enum import Enum
from typing import Union, Tuple
from deck import Card, Pile


class StackingMethod(Enum):
    ALTERNATING = 0,
    COLOR = 1,
    SUIT = 2,


def can_stack(card1: Union[Card, Pile], card2: Union[Card, Pile], rank_diff: Union[int, None],
              suit_method: Union[StackingMethod, None]) -> bool:
    if isinstance(card1, Card):
        if isinstance(card2, Pile):
            if not card2.is_visible(0):
                return False
            card2 = card2[0]
        if rank_diff is not None and card2 - card1 != rank_diff:
            return False
        if suit_method == StackingMethod.ALTERNATING:
            return card1.is_black ^ card2.is_black
        elif suit_method == StackingMethod.COLOR:
            return card1.is_black == card2.is_black
        elif suit_method == StackingMethod.SUIT:
            return card1.suit == card2.suit
        return True
    elif isinstance(card1, Pile):
        prev_card = None
        for card_index in range(len(card1)):
            card = card1[card_index]
            if not card1.is_visible(card_index):
                return False
            if prev_card is not None and not can_stack(prev_card, card, rank_diff, suit_method):
                return False
            if can_stack(card, card2, rank_diff, suit_method):
                return True
            prev_card = card
        return False
