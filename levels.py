"""Level layouts in the order they appear in the game."""

from block import Block
from randomColor import Color


class Level:
    def __init__(self, scrolling, farEnd, spikes, objects, flagPosX=1240, flagPosY=640):
        self.objects = objects
        self.spikes = spikes
        self.flagPos = (flagPosX, flagPosY)
        self.scrolling = scrolling
        self.farEnd = farEnd


LEVEL_COUNT = 9


def build_levels():
    return [
        Level(False, 0, [
            Block(550, 640, "#ff0000", "bottomleft", 20, 20),
            Block(0, 640, "#000000", "bottomleft", 30, 800)
        ], [
            Block(1250, 640, "#000000", "bottomleft", 30, 800)
        ]),
        Level(False, 0, [
            Block(0, 640, "#000000", "bottomleft", 30, 800),
            Block(350, 640, "#ff0000", "bottomleft", 20, 20),
            Block(550, 640, "#ff0000", "bottomleft", 20, 20)
        ], [
            Block(0, 640, "#000000", "bottomleft", 30, 800),
            Block(1250, 640, "#000000", "bottomleft", 30, 800)
        ]),
        Level(False, 0, [
            Block(0, 640, "#000000", "bottomleft", 30, 800),
            Block(350, 640, "#ff0000", "bottomleft", 20, 20),
            Block(450, 580, "#ff0000", "bottomleft", 20, 20),
            Block(550, 640, "#ff0000", "bottomleft", 20, 20)
        ], [
            Block(1250, 640, "#000000", "bottomleft", 30, 800)
        ]),
        Level(False, 0, [
            Block(0, 640, "#000000", "bottomleft", 30, 800),
            Block(350, 640, "#ff0000", "bottomleft", 50, 10),
            Block(400, 520, "#ff0000", "bottomleft", 50, 20),
            Block(450, 640, "#ff0000", "bottomleft", 50, 10)
        ], [
            Block(300, 640, Color(), "bottomleft", 50, 35),
            Block(400, 640, Color(), "bottomleft", 50, 70),
            Block(500, 640, Color(), "bottomleft", 50, 35),
            Block(1250, 640, "#000000", "bottomleft", 30, 800)
        ]),
        Level(True, 2000, [
            Block(0, 640, "#000000", "bottomleft", 30, 800),
            Block(350, 640, "#ff0000", "bottomleft", 50, 10),
            Block(500, 640, "#ff0000", "bottomleft", 50, 10),
            Block(650, 640, "#ff0000", "bottomleft", 50, 10),
            Block(740, 640, "#ff0000", "bottomleft", 40, 10),
            Block(820, 640, "#ff0000", "bottomleft", 40, 10),
            Block(900, 640, "#ff0000", "bottomleft", 40, 10),
            Block(980, 640, "#ff0000", "bottomleft", 40, 10),
            Block(1060, 640, "#ff0000", "bottomleft", 40, 10)
        ], [
            Block(250, 640, Color(), "bottomleft", 100, 30),
            Block(400, 640, Color(), "bottomleft", 100, 30),
            Block(550, 640, Color(), "bottomleft", 100, 30),
            Block(700, 640, Color(), "bottomleft", 40, 30),
            Block(780, 640, Color(), "bottomleft", 40, 30),
            Block(860, 640, Color(), "bottomleft", 40, 30),
            Block(940, 640, Color(), "bottomleft", 40, 60),
            Block(1020, 640, Color(), "bottomleft", 40, 60),
            Block(1100, 640, Color(), "bottomleft", 80, 60),
            Block(1970, 640, "#000000", "bottomleft", 30, 800)
        ], 1960),
        Level(False, 1280, [
            Block(0, 640, "#000000", "bottomleft", 30, 800),
            Block(460, 550, "#ff0000", "bottomleft", 15, 15),
            Block(575, 550, "#ff0000", "bottomleft", 15, 15),
            Block(725, 550, "#ff0000", "bottomleft", 75, 15),
            Block(850, 550, "#ff0000", "bottomleft", 75, 15)
        ], [
            Block(200, 640, Color(), "bottomleft", 50, 30),
            Block(250, 640, Color(), "bottomleft", 75, 60),
            Block(325, 640, Color(), "bottomleft", 75, 90),
            Block(400, 565, Color(), "bottomleft", 250, 15),
            Block(650, 640, Color(), "bottomleft", 100, 90),
            Block(675, 550, Color(), "bottomleft", 50, 30),
            Block(750, 565, Color(), "bottomleft", 150, 15),
            Block(800, 550, Color(), "bottomleft", 50, 30),
            Block(900, 640, Color(), "bottomleft", 100, 90),
            Block(925, 550, Color(), "bottomleft", 50, 30),
            Block(1000, 565, Color(), "bottomleft", 150, 15),
            Block(1250, 640, "#000000", "bottomleft", 30, 800)
        ]),
        Level(False, 1280, [
            Block(0, 640, "#000000", "bottomleft", 30, 800),
            Block(100, 610, "#ff0000", "bottomleft", 85, 15),
            Block(150, 550, "#ff0000", "bottomleft", 85, 15),
            Block(325, 500, "#ff0000", "bottomleft", 90, 45),
            Block(460, 550, "#ff0000", "bottomleft", 5, 15),
            Block(480, 500, "#ff0000", "bottomleft", 90, 45),
            Block(585, 550, "#ff0000", "bottomleft", 15, 15),
            Block(615, 500, "#ff0000", "bottomleft", 15, 45),
            Block(725, 550, "#ff0000", "bottomleft", 75, 15),
            Block(850, 550, "#ff0000", "bottomleft", 75, 15),
            Block(1175, 565, "#ff0000", "bottomleft", 75, 15)
        ], [
            Block(200, 640, Color(), "bottomleft", 50, 30),
            Block(250, 640, Color(), "bottomleft", 75, 60),
            Block(325, 640, Color(), "bottomleft", 75, 90),
            Block(400, 565, Color(), "bottomleft", 250, 15),
            Block(650, 640, Color(), "bottomleft", 100, 90),
            Block(675, 550, Color(), "bottomleft", 50, 30),
            Block(750, 565, Color(), "bottomleft", 150, 15),
            Block(800, 550, Color(), "bottomleft", 50, 30),
            Block(900, 640, Color(), "bottomleft", 100, 90),
            Block(925, 550, Color(), "bottomleft", 50, 30),
            Block(1000, 565, Color(), "bottomleft", 150, 15),
            Block(1250, 640, "#000000", "bottomleft", 30, 800)
        ]),
        Level(True, 5780, [
            Block(0, 640, "#000000", "bottomleft", 30, 800),
            Block(1450, 640, "#ff0000", "bottomleft", 20, 20),
            Block(1550, 580, "#ff0000", "bottomleft", 20, 20),
            Block(1650, 640, "#ff0000", "bottomleft", 20, 20),
            Block(1850, 640, "#ff0000", "bottomleft", 50, 10),
            Block(1900, 520, "#ff0000", "bottomleft", 50, 20),
            Block(1950, 640, "#ff0000", "bottomleft", 50, 10),
            Block(2350, 640, "#ff0000", "bottomleft", 50, 10),
            Block(2500, 640, "#ff0000", "bottomleft", 50, 10),
            Block(2650, 640, "#ff0000", "bottomleft", 50, 10),
            Block(2740, 640, "#ff0000", "bottomleft", 40, 10),
            Block(2820, 640, "#ff0000", "bottomleft", 40, 10),
            Block(2900, 640, "#ff0000", "bottomleft", 40, 10),
            Block(2980, 640, "#ff0000", "bottomleft", 40, 10),
            Block(3060, 640, "#ff0000", "bottomleft", 40, 10),
            Block(3660, 550, "#ff0000", "bottomleft", 15, 15), # second to last level
            Block(3775, 550, "#ff0000", "bottomleft", 15, 15),
            Block(3925, 550, "#ff0000", "bottomleft", 75, 15),
            Block(4050, 550, "#ff0000", "bottomleft", 75, 15),
            Block(4600, 610, "#ff0000", "bottomleft", 85, 15), # last part
            Block(4650, 550, "#ff0000", "bottomleft", 85, 15),
            Block(4825, 500, "#ff0000", "bottomleft", 90, 45),
            Block(4960, 550, "#ff0000", "bottomleft", 5, 15),
            Block(4980, 500, "#ff0000", "bottomleft", 90, 45),
            Block(5085, 550, "#ff0000", "bottomleft", 15, 15),
            Block(5115, 500, "#ff0000", "bottomleft", 15, 45),
            Block(5225, 550, "#ff0000", "bottomleft", 75, 15),
            Block(5350, 550, "#ff0000", "bottomleft", 75, 15),
            Block(5675, 565, "#ff0000", "bottomleft", 75, 15)
        ], [
            Block(600, 640, Color(), "bottomleft", 650, 30),
            Block(750, 610, Color(), "bottomleft", 500, 30),
            Block(1800, 640, Color(), "bottomleft", 50, 35),
            Block(1900, 640, Color(), "bottomleft", 50, 70),
            Block(2000, 640, Color(), "bottomleft", 50, 35),
            Block(2250, 640, Color(), "bottomleft", 100, 30),
            Block(2400, 640, Color(), "bottomleft", 100, 30),
            Block(2550, 640, Color(), "bottomleft", 100, 30),
            Block(2700, 640, Color(), "bottomleft", 40, 30),
            Block(2780, 640, Color(), "bottomleft", 40, 30),
            Block(2860, 640, Color(), "bottomleft", 40, 30),
            Block(2940, 640, Color(), "bottomleft", 40, 60),
            Block(3020, 640, Color(), "bottomleft", 40, 60),
            Block(3100, 640, Color(), "bottomleft", 80, 60),
            Block(3400, 640, Color(), "bottomleft", 50, 30), # second to last level
            Block(3450, 640, Color(), "bottomleft", 75, 60),
            Block(3525, 640, Color(), "bottomleft", 75, 90),
            Block(3600, 565, Color(), "bottomleft", 250, 15),
            Block(3850, 640, Color(), "bottomleft", 100, 90),
            Block(3875, 550, Color(), "bottomleft", 50, 30),
            Block(3950, 565, Color(), "bottomleft", 150, 15),
            Block(4000, 550, Color(), "bottomleft", 50, 30),
            Block(4100, 640, Color(), "bottomleft", 100, 90),
            Block(4125, 550, Color(), "bottomleft", 50, 30),
            Block(4200, 565, Color(), "bottomleft", 150, 15),
            Block(4400, 640, Color(), "bottomleft", 50, 30),
            Block(4700, 640, Color(), "bottomleft", 50, 30), #last part
            Block(4750, 640, Color(), "bottomleft", 75, 60),
            Block(4825, 640, Color(), "bottomleft", 75, 90),
            Block(4900, 565, Color(), "bottomleft", 250, 15),
            Block(5150, 640, Color(), "bottomleft", 100, 90),
            Block(5175, 550, Color(), "bottomleft", 50, 30),
            Block(5250, 565, Color(), "bottomleft", 150, 15),
            Block(5300, 550, Color(), "bottomleft", 50, 30),
            Block(5400, 640, Color(), "bottomleft", 100, 90),
            Block(5425, 550, Color(), "bottomleft", 50, 30),
            Block(5500, 565, Color(), "bottomleft", 150, 15),
            Block(5750, 640, "#000000", "bottomleft", 30, 800)
        ], 5740),
        Level(False, 0, [
            Block(0, 640, "#000000", "bottomleft", 30, 800)
        ], [
            Block(1250, 640, "#000000", "bottomleft", 30, 800)
        ])
        
    ]
