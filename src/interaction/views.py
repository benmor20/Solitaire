import itertools

import pygame
from pygame import locals

from src.interaction.sprites import *
from src.model.models import *


class View(ABC):
    def __init__(self, model: GameModel):
        self._model = model

    def setup(self):
        return

    @abstractmethod
    def display_game(self):
        pass

    def teardown(self):
        return


class PygameView(View):
    def __init__(self, model: GameModel, sprites: Dict[str, MultiPileSprite], board_size: Tuple[int, int],
                 board_pos: Tuple[int, int] = (-1, 100),
                 screen_size: Union[Tuple[int], pygame.Surface] = constants.SCREEN_SIZE,
                 default_background: Tuple[int] = constants.BACKGROUND_COLOR):
        super().__init__(model)
        if not pygame.get_init():
            pygame.init()
        self._screen = screen_size if isinstance(screen_size, pygame.Surface) else pygame.display.set_mode(screen_size)
        self._background = default_background
        self._board = pygame.Surface(board_size, pygame.SRCALPHA)
        board_mid = constants.SCREEN_SIZE[0] // 2 if board_pos[0] == -1 else board_pos[0]
        self._board_rect = self._board.get_rect(midtop=(board_mid, board_pos[1]))
        self._sprites = sprites

    @property
    def screen(self):
        return self._screen

    def get_pile_from_click(self, click_pos: Tuple[int, int]) -> Optional[Tuple[str, int]]:
        adj_pos = utils.subtract_tuples(click_pos, self._board_rect.topleft)
        for name, sprite in self._sprites.items():
            if sprite.rect.collidepoint(adj_pos):
                index = sprite.pile_index_from_pos(utils.subtract_tuples(adj_pos, sprite.rect.topleft))
                return None if index is None else (name, index)
        return None

    def display_game(self):
        if len(pygame.event.get(eventtype=locals.QUIT)) > 0:
            self._model.running = False
        self._screen.fill(self._background)
        self._update_sprites()
        self._draw()
        pygame.display.flip()

    def _update_sprites(self):
        for sprite in self._sprites.values():
            sprite.draw()

    def _draw(self):
        self._board.fill((0, 0, 0, 0))
        for sprite in self._sprites.values():
            self._board.blit(sprite, sprite.rect)
        self._screen.blit(self._board, self._board_rect)
        if self._model.selected is not None:
            selected = PileSprite(self._model.selected[0])
            self._screen.blit(selected, selected.get_rect(midtop=pygame.mouse.get_pos()))


class KlondikeView(PygameView):
    def __init__(self, model: KlondikeModel):
        board_width = constants.CARD_SIZE[0] * 7 + constants.CARD_GAP * 6
        sprites = {}
        sprites['foundation'] = FoundationSprite(model.foundation)
        sprites['draw'] = DrawPileSprite(model.draw_pile)
        sprites['draw'].rect = sprites['draw'].get_rect(topright=(board_width, 0))
        sprites['tableau'] = TableauSprite(model.tableau, (constants.CARD_SIZE[0] * 7 + constants.CARD_GAP * 6, 500))
        sprites['tableau'].rect = sprites['tableau'].get_rect(topleft=
                                                              (0, constants.CARD_SIZE[1] + constants.CARD_GAP * 2))
        super().__init__(model, sprites, (board_width, 600))


class LaBelleLucieView(PygameView):
    def __init__(self, model: LaBelleLucieModel):
        sprites = {}
        sprites['foundation'] = FoundationSprite(model.foundation)
        hstep = constants.CARD_SIZE[0] + constants.NONOVERLAP_HORZ * 5 + constants.CARD_GAP
        vstep = constants.CARD_SIZE[1] + constants.CARD_GAP
        tab_locations = list(itertools.product(range(0, hstep*4, hstep), range(0, vstep*5, vstep)))[:-2]
        print(len(tab_locations))
        tab_width = max(tab_locations, key=lambda l: l[0])[0] + hstep
        tab_height = max(tab_locations, key=lambda l: l[1])[1] + vstep
        tab_size = (tab_width, tab_height)
        board_size = utils.add_tuples(tab_size, (0, constants.CARD_SIZE[1] + constants.CARD_GAP * 2))
        sprites['tableau'] = TableauSprite(model.tableau,tab_size, locations=tab_locations,
                                           stack_direction=PileSprite.StackDirection.RIGHT)
        sprites['foundation'].rect = sprites['foundation'].get_rect(midtop=(board_size[0] // 2, 0))
        sprites['tableau'].rect = sprites['tableau'].get_rect(topleft=
                                                              (0, constants.CARD_SIZE[1] + constants.CARD_GAP * 2))
        super().__init__(model, sprites, board_size, board_pos=(-1, 50))

