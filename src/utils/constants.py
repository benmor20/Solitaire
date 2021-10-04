import pygame

pygame.font.init()


FPS = 60
SCREEN_SIZE = (800, 600)

BACKGROUND_COLOR = (0, 100, 0)
CARD_SIZE = (50, 70)
CARD_RADIUS = 6
LARGE_TEXT = pygame.font.SysFont("segoeuisymbol", 30)
SMALL_TEXT = pygame.font.SysFont("segoeuisymbol", 12)
CARD_COLOR = (240, 240, 240)
CARD_BACK = (0, 0, 150)
BLACK = (0, 0, 0)
RED = (200, 0, 0)

NONOVERLAP_VERT = 15
NONOVERLAP_HORZ = 20
CARD_GAP = 10

SELECT_TIME = 0.2
