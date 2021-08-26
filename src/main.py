import pygame
from pygame import locals

import constants
from controllers import KlondikeController
from models import KlondikeModel
from views import KlondikeView


def main():
    model = KlondikeModel()
    model.setup()
    view = KlondikeView(model)
    view.setup()
    controller = KlondikeController(model, view)

    clock = pygame.time.Clock()
    while not model.is_done():
        controller.update()
        view.display_game()
        clock.tick(constants.FPS)

    model.teardown()
    view.teardown()


if __name__ == '__main__':
    main()
