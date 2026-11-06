from randomColor import Color
from block import Block
from data import Data

class Item():
    def __init__(self, player, type = "empty", data = Data()) -> None:
        self.itemType = type
        self.data = data
        self.player = player
        if data.type == "wood":
            self.data.color = "#8c6f1d"

    
    def use(self):
        if self.itemType == "empty":
            pass
        if self.itemType == "block":
            return Block(self.player.x, self.player.y, self.data.color)