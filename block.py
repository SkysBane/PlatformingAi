import pygame

class Block():
    def __init__(self, x, y, color, location = "midbottom", xSize = 10, ySize = 10) -> None:
        self.x = x
        self.y = y
        self.onGround = False
        self.surface = pygame.surface.Surface((xSize, ySize))
        if location == "midbottom":
            self.rect = self.surface.get_rect(midbottom = (x, y))
        elif location == "bottomleft":
            self.rect = self.surface.get_rect(bottomleft = (x, y))
        else:
            self.rect = self.surface.get_rect(midbottom = (x, y))

        
        self.color = color
        self.surface.fill(self.color)
