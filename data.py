from randomColor import Color

class Data():
    def __init__(self, color = Color(), newType = "empty") -> None:
        self.color = color
        self.type = newType
    