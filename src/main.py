import pygame
import numpy as np
from matplotlib import pyplot as plt
import json

from src.utils import constants
from src.interaction.controllers import KlondikeAIController
from src.model.models import KlondikeModel
from src.interaction.views import KlondikeView


def main():
    nruns = 10
    ncards = np.array([])
    for _ in range(nruns):
        model = KlondikeModel()
        model.setup()
        view = KlondikeView(model)
        view.setup()
        controller = KlondikeAIController(model, view)

        clock = pygame.time.Clock()
        while not model.is_done():
            controller.update()
            view.display_game()
            clock.tick(constants.FPS)

        ncards = np.append(ncards, model.foundation.num_cards())
        model.teardown()
        view.teardown()

    with open('data/klondike_results.txt', 'w') as f:
        f.write(json.dumps(list(ncards)))

    wins = sum(ncards == 52)
    total_cards = sum(ncards)
    print(ncards)
    print(f'Won {wins} out of {nruns} games ({wins / nruns * 100}%), with an average of {total_cards / nruns} cards per game ({total_cards} total)')
    plt.hist(ncards)
    plt.show()


if __name__ == '__main__':
    main()
