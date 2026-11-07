import pygame


class Ground:
    def __init__(self, x, y, height):
        self.rect = pygame.Rect(0, 0, 100000, height)
        self.rect.midtop = (x, y)
