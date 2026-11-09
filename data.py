from randomColor import Color


class Data:
    def __init__(self, color=None, newType="empty"):
        self.color = Color() if color is None else color
        self.type = newType
