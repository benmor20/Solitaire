import pygame

from src.utils import constants
from src.interaction.controllers import KlondikeController
from src.model.models import KlondikeModel
from src.interaction.views import KlondikeView


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
