from typing import *
from deck import *
import utils


class Foundation:
    def __init__(self, starting_rank: Optional[Rank] = None):
        self._foundations: List[Pile] = []
        self.starting_rank = starting_rank
        self.setup()

    def setup(self):
        self._foundations = []
        for _ in range(4):
            self._foundations.append(Pile())

    def is_done(self) -> bool:
        for found in self._foundations:
            if len(found) < 13:
                return False
        return True

    def add_to(self, card: Card, foundation: int = -1) -> bool:
        if foundation == -1:
            empty_index = -1
            for index in range(len(self._foundations)):
                if len(self._foundations) == 0 and empty_index == -1:
                    empty_index = index
                elif len(self._foundations[index]) > 0 and self._foundations[index].peek().suit == card.suit:
                    foundation = index
            if foundation == -1:
                foundation = empty_index
        if (len(self._foundations[foundation]) == 0 and (self.starting_rank is None or card.rank == self.starting_rank))\
                or card.can_stack_on(self._foundations[foundation], StackingMethod(-1, SuitStackMethod.SUIT)):
            self._foundations[foundation] = Pile(card, visible=True) + self._foundations[foundation]
            return True
        return False

    def pop(self, foundation: int) -> Card:
        return self._foundations[foundation].draw()

    def peel(self, foundation: int) -> Card:
        return self._foundations[foundation].peek()


class Tableau:
    def __init__(self, deck: Pile, stacking_method: StackingMethod, pile_lens: Tuple[int, ...],
                 num_visible_on_init: Union[Tuple[int, ...], int] = 1, max_cards_moved: Optional[int] = None):
        self._tableau: List[Pile] = []
        self._num_tableau_piles = len(pile_lens)
        self._init_pile_lens = pile_lens
        self._stacking_method = stacking_method
        self._max_cards_moved = max_cards_moved
        if isinstance(num_visible_on_init, tuple):
            self._num_visible_on_init = num_visible_on_init
        elif num_visible_on_init < 0:
            self._num_visible_on_init = utils.add_tuples(pile_lens, num_visible_on_init + 1)
        else:
            self._num_visible_on_init = tuple([self._num_visible_on_init] * self._num_tableau_piles)
        self.setup(deck)

    @property
    def num_tableau_piles(self):
        return self._num_tableau_piles

    @property
    def init_pile_lens(self):
        return self._init_pile_lens

    def update_max_cards_moved(self, max_cards_moved: Optional[int]):
        self._max_cards_moved = max_cards_moved

    def setup(self, deck: Pile):
        self._tableau = []
        for pile in range(self.num_tableau_piles):
            if len(self._tableau) <= pile:
                self._tableau.append(Pile())
            if len(self._tableau[pile]) < self.init_pile_lens[pile]:
                self._tableau[pile] += deck.draw()
        for pile in range(self.num_tableau_piles):
            for card in range(len(self._num_visible_on_init[pile])):
                self._tableau[pile].make_visible(card)

    def pop(self, pile_index: int) -> Pile:
        ret, self._tableau[pile_index] = self._tableau[pile_index].split_by_stackable(self._stacking_method)
        return ret

    def peek(self, pile_index: int) -> Pile:
        return self._tableau[pile_index].split_by_visible()[0]

    def replace(self, pile: Pile, pile_index: int):
        self._tableau[pile_index] = pile + self._tableau[pile_index]

    def add_to(self, pile: Pile, pile_index: int) -> bool:
        if pile.can_stack_on(self._tableau[pile_index], self._stacking_method):
            self.replace(pile, pile_index)
            return True
        return False

    def show_top_cards(self, num_to_show: Optional[int] = None):
        for tab in range(len(self._tableau)):
            for index in range(min(self._num_visible_on_init[tab] if num_to_show is None else num_to_show,
                                   len(self._tableau[tab]))):
                self._tableau[tab].make_visible(index)


class DrawPile:
    def __init__(self, deck: Pile, flip_amount: int = 3, num_visible: int = -1):
        self._deck = deck
        self._draw = Pile()
        self._flip_amount = flip_amount
        self._num_visible = flip_amount if num_visible < 0 else num_visible
        self.setup(deck)

    @property
    def flip_amount(self) -> int:
        return self._flip_amount

    @property
    def num_visible(self) -> int:
        return self._num_visible

    def setup(self, deck: Pile):
        self._deck = deck
        self._draw = Pile()

    def deal(self):
        self._draw.hide_all()
        if len(self._deck) == 0:
            self._deck = reversed(self._draw)
        else:
            for _ in range(min(self.flip_amount, len(self._deck))):
                self._draw = self._deck.draw() + self._draw
            for index in range(self.num_visible):
                self._draw.make_visible(index)

    def pop(self) -> Optional[Card]:
        return None if len(self._draw) == 0 else self._draw.draw()

    def peek(self) -> Optional[Pile]:
        if len(self._draw) == 0:
            return None
        pile = Pile()
        for index in range(self.num_visible):
            pile += self._draw[index]
        return pile

    def replace(self, card: Pile):
        if len(card) > 1:
            raise ValueError('Cannot return more than one card')
        self._draw = card + self._draw
        self._draw.make_visible(0)
