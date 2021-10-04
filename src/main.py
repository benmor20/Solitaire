import pygame
import numpy as np
from matplotlib import pyplot as plt
import json

from src.utils import constants
from src.interaction.controllers import *
from src.model.models import *
from src.interaction.views import *


def main():
    model = LaBelleLucieModel()
    model.setup()
    view = LaBelleLucieView(model)
    view.setup()
    controller = PygameController(model, view)

    clock = pygame.time.Clock()

    while not model.is_done():
        view.display_game()
        controller.update()
        clock.tick()


if __name__ == '__main__':
    main()
