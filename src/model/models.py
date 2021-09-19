from abc import ABC, abstractmethod
from typing import *

from src.model.board import *
from src.model.deck import *


class GameModel(ABC):
    def __init__(self, stacking_method: Optional[StackingMethod] = None):
        self.running = True
        self.deck = Pile()
        self._selected: Optional[Tuple[Pile, str, int]] = None
        self.stacking_method = stacking_method

    @property
    def selected(self) -> Optional[Tuple[Pile, str, int]]:
        return self._selected

    def setup(self):
        self.deck = Pile(start_full=True, shuffled=True)

    @abstractmethod
    def pickup(self, pile_type: str, pile_index: int = 0) -> bool:
        pass

    @abstractmethod
    def replace_selected(self) -> bool:
        pass

    @abstractmethod
    def set_down_on(self, pile_type: str, pile_index: int = 0) -> bool:
        pass

    @abstractmethod
    def on_select(self, pile_type: str, pile_index: int = 0) -> bool:
        pass

    @abstractmethod
    def has_won(self) -> bool:
        pass

    def is_done(self) -> bool:
        return not self.running

    def teardown(self):
        return


class KlondikeModel(GameModel):
    def __init__(self):
        super().__init__(StackingMethod(1, SuitStackMethod.ALTERNATING, stack_on_blank=lambda c: c.rank == Rank.KING))
        self.foundation = Foundation(Rank.ACE_LOW)
        self.tableau = Tableau(self.stacking_method, (1, 2, 3, 4, 5, 6, 7))
        self.draw_pile = DrawPile(self.deck)
        self.setup()

    def setup(self):
        super().setup()
        self.foundation.setup()
        self.tableau.setup(self.deck)
        self.draw_pile.setup(self.deck)

    def pickup(self, pile_type: str, pile_index: int = 0) -> bool:
        if self.selected is not None:
            return False
        pickup = None
        if pile_type == 'draw':
            pickup = Pile(self.draw_pile.pop(), visible=True)
        elif pile_type == 'tableau':
            pickup = self.tableau.pop_pile(pile_index)
        elif pile_type == 'foundation':
            pickup = Pile(self.foundation.pop(pile_index), visible=True)
        elif pile_type != 'deck':
            raise ValueError(f'Unrecognized pile type: {pile_type}')
        if pickup is not None:
            self.selected = pickup, pile_type, pile_index
            return True
        return False

    def replace_selected(self) -> bool:
        if self.selected is None:
            return False
        change = False
        if self.selected[1] == 'draw':
            self.draw_pile.replace(self.selected[0])
            change = len(self.selected) > 0
        elif self.selected[1] == 'tableau':
            self.tableau.replace(self.selected[0], self.selected[2])
            change = len(self.selected[0]) > 0
        elif self.selected[1] == 'foundation':
            if len(self.selected[0]) == 0:
                change = False
            else:
                self.foundation.add_card(self.selected[0][0], self.selected[2])
                change = True
        self.selected = None
        return change

    def set_down_on(self, pile_type, pile_index) -> bool:
        if self.selected is None:
            return False
        if pile_type == 'draw':
            success = False
        elif pile_type == 'tableau':
            tab_pile = self.tableau.peek(pile_index)
            if self.selected[0].can_stack_on(tab_pile, self.stacking_method):
                card = -1
                if len(tab_pile) > 0:
                    for card in range(len(self.selected[0])):
                        if self.tableau.peek(pile_index)[0] - self.selected[0][card] == 1:
                            break
                drawn = self.selected[0].draw(card + 1)
                if isinstance(drawn, Card):
                    drawn = Pile(drawn, visible=True)
                self.tableau.add_card(drawn, pile_index)
                success = True
            elif len(self.tableau.peek_all(pile_index)) == 0 and self.selected[0][-1].rank == Rank.KING:
                pile = self.selected[0].draw(0)
                if isinstance(pile, Card):  # This is the case when moving only a King
                    pile = Pile(pile, visible=True)
                self.tableau.add_card(pile, pile_index)
                success = True
            else:
                success = False
        elif pile_type == 'foundation':
            if self.selected[0][0].can_stack_on(self.foundation.peek(pile_index), self.stacking_method):
                self.foundation.add_card(self.selected[0].draw(), pile_index)
                success = True
            else:
                success = False
        elif pile_type != 'deck':
            raise ValueError(f'Unknown pile type: {pile_type}')
        self.replace_selected()
        self.tableau.show_top_cards()
        return success

    def on_select(self, pile_type: str, pile_index: int = 0) -> bool:
        if pile_type == 'draw':
            if self.draw_pile.peek() is None:
                return False
            if self.foundation.add_card(self.draw_pile.peek()[0]):
                self.draw_pile.pop()
                return True
            return False
        elif pile_type == 'tableau':
            top_card = self.tableau.peek_card(pile_index)
            if top_card is None:
                return False
            if self.foundation.add_card(top_card):
                self.tableau.pop_card(pile_index)
                self.tableau.show_top_cards()
                return True
            return False
        elif pile_type == 'deck':
            self.draw_pile.deal()
            return True
        elif pile_type == 'foundation':
            return False
        else:
            raise ValueError(f'Unrecognized pile type: {pile_type}')

    def has_won(self) -> bool:
        return self.foundation.has_won()


class LaBelleLucieModel(GameModel):
    def __init__(self):
        super().__init__(StackingMethod(1, SuitStackMethod.SUIT, stack_on_blank=False))
        self.foundation = Foundation(Rank.ACE_LOW)
        self.tableau = Tableau(self.stacking_method, tuple([3] * 17 + [1]))
        self.setup()

    def on_select(self, pile_type: str, pile_index: int = 0) -> bool:
        if pile_type == 'tableau':
            top_card = self.tableau.peek_card(pile_index)
            if top_card is None:
                return False
            if self.foundation.add_card(top_card):
                self.tableau.pop_card(pile_index)
                self.tableau.show_top_cards()
                return True
            return False
        elif pile_type == 'foundation':
            return False
        else:
            raise ValueError(f'Unknown pile type: {pile_type}')

    def pickup(self, pile_type: str, pile_index: int = 0) -> bool:
        if pile_type == 'tableau':
            if len(self.tableau[pile_index]) == 0:
                return False
            self._selected = (Pile(self.tableau.pop_card(pile_index)), 'tableau', pile_index)
            return True
        elif pile_type == 'foundation':
            if len(self.foundation[pile_index]) == 0:
                return False
            self._selected = (Pile(self.foundation.peek(pile_index)), 'foundation', pile_index)
            return True
        else:
            raise ValueError(f'Unknown pile type: {pile_type}')

    def replace_selected(self) -> bool:
        if self.selected is None:
            return False
        if self.selected[1] == 'tableau':
            self.tableau.replace(self.selected[0], self.selected[2])
        elif self.selected[1] == 'foundation':
            self.foundation.add_card(self.selected[0][0], self.selected[2])
        self._selected = None
        return True

    def set_down_on(self, pile_type: str, pile_index: int = 0) -> bool:
        if self.selected is None:
            return False
        success = False
        if pile_type == 'tableau':
            if self.selected[0].can_stack_on(self.tableau[pile_index], self.stacking_method):
                self.tableau.add_card(self.selected[0], pile_index)
                success = True
        elif pile_type == 'foundation':
            success = self.foundation.add_card(self.selected[0][0], pile_index)
        if success:
            self._selected = None
        else:
            self.replace_selected()
        return success

    def has_won(self) -> bool:
        return self.foundation.has_won()
