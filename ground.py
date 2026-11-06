import pygame

class Ground():
    def __init__(self, x, y, height):
        self.x = x
        self.y = y
        self.surface = pygame.surface.Surface((100000, height))
        self.rect = self.surface.get_rect(midtop = (self.x, self.y))
        self.surface.fill("#000000")