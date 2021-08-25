import pygame
from pygame import locals

import constants
from controllers import PlayerController
from models import KlondikeModel
from views import KlondikeView


def main():
    model = KlondikeModel()
    model.setup()
    controller = PlayerController(model)
    view = KlondikeView(model)
    view.setup()

    print(len(model.tableau[1]))

    clock = pygame.time.Clock()
    while not model.is_done():
        controller.update()
        view.display_game()
        clock.tick(constants.FPS)

    model.teardown()
    view.teardown()


if __name__ == '__main__':
    main()
