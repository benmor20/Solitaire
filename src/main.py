import pygame
from pygame import locals

import constants
from controllers import PlayerController
from models import GameModel
from views import PygameView


def main():
    model = GameModel()
    controller = PlayerController(model)
    view = PygameView(model)

    clock = pygame.time.Clock()
    while not model.is_done():
        controller.update()
        view.display_game()
        clock.tick(constants.FPS)


if __name__ == '__main__':
    main()
