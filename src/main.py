from models import TestModel
from controllers import TestController
from views import TestView
import constants
import pygame
from pygame import locals


def main():
    pygame.init()
    screen = pygame.display.set_mode(constants.SCREEN_SIZE)
    model = TestModel()
    controller = TestController(model)
    view = TestView(model)

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == locals.QUIT:
                running = False
        controller.update()
        view.draw()
        clock.tick(constants.FPS)


if __name__ == '__main__':
    main()
