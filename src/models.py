import copy
from typing import Union
from deck import Card, Pile
import utils


class GameModel:
    def __init__(self):
        self.running = True
        self.deck = Pile()

    def setup(self):
        self.deck = Pile(start_full=True, shuffled=True)

    def is_done(self) -> bool:
        return not self.running

    def teardown(self):
        return


class FoundationModel(GameModel):
    def __init__(self):
        super().__init__()
        self.foundations = []

    def setup(self):
        super().setup()
        self.foundations = []
        for _ in range(4):
            self.foundations.append(Pile())

    def is_done(self) -> bool:
        done = True
        for found in self.foundations:
            if len(found) < 13:
                done = False
        if done:
            self.running = False
        return super().is_done()

    def to_foundation(self, card: Union[Card, Pile], foundation: int) -> bool:
        pile = None
        if isinstance(card, Pile):
            pile = copy.copy(card)
            card = pile.peek()
        if utils.can_stack(card, self.foundations[foundation], -1, utils.StackingMethod.SUIT):
            self.foundations[foundation] = card + self.foundations[foundation]
            if pile is not None:
                pile.draw()
            return True
        return False


class KlondikeModel(FoundationModel):
    def __init__(self):
        super().__init__()
        self.tableau = []
        self.draw_pile = Pile()
        self.selected = None
        self.setup()

    def setup(self):
        super().setup()
        self.tableau = []
        self.draw_pile = Pile()
        self.selected = None
        for tab in range(7):
            self.tableau.append(Pile())
            self.tableau[tab] = self.deck.move_to(self.tableau[tab], tab + 1)
            self.tableau[tab].flip(0)

    def move(self, src: int, dest: int) -> bool:
        if utils.can_stack(self.tableau[src], self.tableau[dest], 1, utils.StackingMethod.ALTERNATING):
            card_index = 0
            card = self.tableau[src][card_index]
            while self.tableau[dest][0] - card != 1:
                card_index += 1
                card = self.tableau[src][card_index]
            self.tableau[dest] = self.tableau[src]._draw(card_index + 1) + self.tableau[dest]
            return True
        return False

    def to_foundation(self, card: Union[Card, Pile, int], foundation: int) -> bool:
        if isinstance(card, int):
            card = self.tableau[card]
        return super().to_foundation(card, foundation)

    def deal(self):
        if len(self.deck) == 0:
            self.deck = self.draw_pile._draw(0)
        self.draw_pile = self.deck._draw(min(3, len(self.deck))) + self.draw_pile
