from functools import cached_property

import pygame


class Block:
    def __init__(self, x, y, color, location="midbottom", xSize=10, ySize=10):
        self.x = x
        self.y = y
        self.onGround = False
        self.color = color
        self.rect = pygame.Rect(0, 0, xSize, ySize)
        if location == "bottomleft":
            self.rect.bottomleft = (x, y)
        else:
            self.rect.midbottom = (x, y)

    @cached_property
    def surface(self):
        surface = pygame.Surface(self.rect.size)
        surface.fill(self.color)
        return surface
