import pygame
from block import Block
import math
import sys
from player import Player
from ground import Ground
from randomColor import Color
import numpy as np
from NN import NeuralNetwork


class SpecialRect():
        def __init__(self, rect, xvel):
            self.rect = rect
            self.xVelocity = xvel

class CollisionType():
    def __init__(self, rect, coltype):
            self.rect = rect
            self.type = coltype

class Level():
    def __init__(self, scrolling = False, farEnd = 1280, spikes = [], objectz = [Block(600, 640, Color(), "bottomleft", 30, 30)], flagPosX = 1240, flagPosY = 640) -> None:
        self.objects = objectz
        self.spikes = spikes
        self.flagPos = (flagPosX, flagPosY)
        self.scrolling = scrolling
        self.farEnd = farEnd

class Flag():
    def __init__(self) -> None:
        self.surface = pygame.surface.Surface((10, 20))
        self.rect = self.surface.get_rect()
        self.flagPartOne = pygame.surface.Surface((10, 7))
        self.flagPartOne.fill("#1cfc03")
        self.flagPartTwo = pygame.surface.Surface((3, 20))
        self.flagPartTwo.fill("#1cfc03")
        self.surface.fill("#ffffff")
        self.surface.blit(self.flagPartOne, self.flagPartOne.get_rect())
        self.surface.blit(self.flagPartTwo, self.flagPartTwo.get_rect())



class Main():
    def __init__(self, startLevel = 0, repeatLevelForever = False, playerXOveride = None, playerYOveride = None, playerXvelOveride = None, playerYvelOveride = None, display = True, rayCastOnly = False, bonusStats = False, timedDeath=True, timeDeathAmount = 30, stateBased = False, controlledByNN = False, populationSize=1, nnTimeTick=False):
        CAPTION = "Prototype Platformer"
        
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))#, pygame.FULLSCREEN)
        pygame.display.set_caption(CAPTION)
        self.clock = pygame.time.Clock()
        self.timeElapsed = 0
        self.myTime = 0
        self.deltaTime = self.clock.get_time()
        self.displayRecordCooldown = 0
        self.recordMargin = 0
        self.display = display
        self.rayCastOnly = rayCastOnly
        self.bonusStats = bonusStats
        self.timedDeath = timedDeath
        self.timeDeathAmount = timeDeathAmount
        self.stateBased = stateBased
        self.controlledByNN = controlledByNN
        self.populationSize = populationSize
        self.nnTimeTick = nnTimeTick

        self.RECORDFILENAME = "records.txt"

        self.openRecordFile("r")
        self.closeRecordsFile()

        self.reset = False
        self.done = False
        self.gameState = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 11, 30]#, -1000, 0]

        self.currentReward = 0
        self.won = False
        self.score = 0

        self.leftRight = 0
        self.right = 0
        self.left = 0
        self.up = -1
        self.down = -1
        self.used = False
        self.alreadyUsed = False
        self.otherright = False
        self.otherleft = False
        self.otherup = False
        self.otherdown = False

        self.returnTime = 0

        self.spawnPoint = (100, 640)

        if playerXOveride is not None and playerYOveride is not None:
            if playerXvelOveride is not None and playerYvelOveride is not None:
                self.players = [Player(playerXOveride, playerYOveride, 10, 0.3, 1, 4, 10, self, playerXvelOveride, playerYvelOveride)]
            else:
                self.players = [Player(playerXOveride, playerYOveride, 10, 0.3, 1, 4, 10, self)]
        else:
            self.players = [Player(self.spawnPoint[0], self.spawnPoint[1], 10, 0.3, 1, 4, 10, self)]
        self.objects = []
        self.ground = Ground(600, self.screen.get_height() - 80, 80)
        self.programRunning = False
        self.font = pygame.font.Font(None, 25)
        self.text = self.font.render("hello", False, "#000000")
        self.flagRender = Flag()
        self.canContinue = True

        self.cameraX = 0
        self.lastx = self.players[0].x


        self.repeatLevelForever = repeatLevelForever
        self.activeLevel = startLevel
        self.levels = [
            Level(False, 0, [
                Block(550, 640, "#ff0000", "bottomleft", 20, 20),
                Block(0, 640, "#000000", "bottomleft", 30, 800)
            ], [
                Block(1250, 640, "#000000", "bottomleft", 30, 800)
            ]),
            #Level(False, 0, [
            #    Block(0, 640, "#000000", "bottomleft", 30, 800)
            #], [
            #    Block(1250, 640, "#000000", "bottomleft", 30, 800)
            #]),
            #evel(False, 0, [
            #    Block(0, 640, "#000000", "bottomleft", 30, 800)
            #], [
            #    Block(600, 640, Color(), "bottomleft", 650, 30),
            #    Block(750, 610, Color(), "bottomleft", 500, 30),
            #    Block(1250, 640, "#000000", "bottomleft", 30, 800)
            #], 1240, 580),
            #Level(True, 2000, [
            #    Block(0, 640, "#000000", "bottomleft", 30, 800)
            #], [
            #    Block(600, 640, Color(), "bottomleft", 650, 30),
            #    Block(750, 610, Color(), "bottomleft", 400, 30),
            #   Block(1970, 640, "#000000", "bottomleft", 30, 800)
            #], 1960),
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
                #Block(1200, 640, Color(), "bottomleft", 50, 30),
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
                #Block(1200, 640, Color(), "bottomleft", 50, 30),
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
                #Block(5700, 640, Color(), "bottomleft", 50, 30),
                Block(5750, 640, "#000000", "bottomleft", 30, 800)
            ], 5740),
            Level(False, 0, [
                Block(0, 640, "#000000", "bottomleft", 30, 800)
            ], [
                Block(1250, 640, "#000000", "bottomleft", 30, 800)
            ])
            
        ]

        if self.controlledByNN:
            spawnX, spawnY = self.players[0].rect.midbottom
            self.players = []

            for i in range(self.populationSize):
                player = Player(spawnX, spawnY, 10, 0.3, 1, 4, 10, self)

                # 21 inputs, 16 for raycasts (8 numerical 8 one-hot), 2 for velocities, 2 for goal direction, and 1 grounded boolean
                player.brain = NeuralNetwork(21, 3, 1, 21)
                player.alive = True
                player.finished = False
                player.fitness = 0
                player.framesAlive = 0
                player.bestX = player.rect.centerx
                player.startX = player.rect.centerx
                player.lastX = player.startX - 100
                player.lastY = player.rect.centery

                self.players.append(player)
        

    def quitPygame(self):
        pygame.quit()

    def getPlayerStats(self):
        return self.players[0].x, self.players[0].y, self.players[0].xVelocity, self.players[0].yVelocity

    def tick(self, amount = 60):
        self.clock.tick(amount)

    def res(self):
        pygame.quit()

    def step(self, inputs = []):
        # [left/right, jump] or [right, left, jump] work perfectly
        
        self.currentReward = 0

        self.lastx = self.players[0].x
        if len(inputs) == 3:
            if inputs[1] == 1:
                inputs[0] = 0
            else:
                inputs[0] = 1
            inputs[1] = inputs[2]
            inputs.pop()
        self.done = False
        if self.clock.get_time() != 0:
                self.myTime += self.clock.get_time() / (self.clock.get_time() * 0.064)
        self.returnTime = self.myTime
        #self._checkEvents()
        self.gameState = self.update(inputs)
        #self.score = self.players[0].x / 100

        if self.players[0].xVelocity > 0 and self.currentReward == 0:
            self.currentReward = 0.0001

        #print(gameState)
        self.drawBackground()
        self.drawAll(self.gameState)
        pygame.display.update()
        if self.display:
            self.clock.tick(60)
        else:
            self.clock.tick()
        if self.done:
            self.currentReward = -10
        if not self.stateBased:
            return self.gameState, self.currentReward, self.done, self.won, self.score, (self.returnTime+0.001) / 1000
        else:
            return self.gameState, self.currentReward, self.done, self.won, self.score, (self.returnTime+0.001) / 1000, (self.players[0].xVelocity, self.players[0].yVelocity)

    def run(self):

        # do our own thing if it's NN
        if self.controlledByNN:
            return self.runNN()

        self.programRunning = True
        self.resetTime()
        while self.programRunning:
            #if self.clock.get_time() != 0:
            #    self.myTime += self.clock.get_time() / (self.clock.get_time() * 0.064)
            self._checkEvents()
            inputs = [self.leftRight, self.up]
            self.step(inputs)
            #self.update(inputs)
            #self.drawBackground()
            #self.drawAll()

            #pygame.display.update()

            #if self.otherright:
            #    self.cameraX += 1
            #if self.otherleft:
            #    self.cameraX -= 1

            #self.clock.tick(60)
        self.recordsFile.close()

    def openRecordFile(self, permission):
        try:
            self.recordsFile = open(self.RECORDFILENAME, permission)
            return self.recordsFile
        except:
            print("could not find record file (missing records.txt)")
            sys.exit()

    def closeRecordsFile(self):
        try:
            self.recordsFile.close()
        except:
            print("file error, possibly no record file there (missing records.txt)")
            sys.exit()

    def checkWin(self):
        if self.players[0].rect.colliderect(self.flagRender.rect):
            self.resetLevel()
            self.checkRecord()
            self.resetTime()
            #self.done = True
            #self.won = True
            self.score += 1
            self.currentReward = 10
            if self.canContinue and not self.repeatLevelForever:
                self.activeLevel += 1
                if self.activeLevel+1 == len(self.levels):
                    self.canContinue = True
                elif self.activeLevel == len(self.levels):
                    self.canContinue = True
                    self.activeLevel = 0
    
    def checkLoss(self):
        if self.timedDeath and self.timeDeathAmount < (self.myTime + 0.001) / 1000:
            self.resetLevel()
            self.resetTime()
            self.done = True
            self.won = False
        for i in self.levels[self.activeLevel].spikes:
            if self.players[0].rect.colliderect(i.rect):
                self.resetLevel()
                self.resetTime()
                self.done = True
                self.won = False
        

    def resetLevel(self):
        self.players[0].rect.midbottom = self.spawnPoint
        self.players[0].xVelocity = 0
        self.players[0].yVelocity = 0


        
    def checkRecord(self):
        time = math.floor(self.myTime)
        pastRecords = self.openRecordFile("r").read().splitlines()
        if self.activeLevel >= len(pastRecords):
            pastRecords.append(str(time))
            for i in range(len(pastRecords)):
                if pastRecords[i] == "":
                    pastRecords.pop(i)
                else:
                    pastRecords[i] += "\n"
            self.closeRecordsFile()
            self.openRecordFile("w")
            self.recordsFile.writelines(pastRecords)
            self.closeRecordsFile()
            return
        pastRecord = pastRecords[self.activeLevel]
        self.displayRecordCooldown = 150
        self.recordMargin = (time-int(pastRecord)) / 1000
        if int(pastRecord) > time:
            pastRecords[self.activeLevel] = str(time)
            for i in range(len(pastRecords)):
                if pastRecords[i] == "":
                    pastRecords.pop(i)
                else:
                    pastRecords[i] += "\n"
            self.closeRecordsFile()
            self.openRecordFile("w")
            self.recordsFile.writelines(pastRecords)
            self.closeRecordsFile()


    def resetTime(self):
        self.timeElapsed = pygame.time.get_ticks()
        self.myTime = 0

    def checkGround(self, thing):
        groundTop = self.ground.rect.top
        if thing.rect.bottom >= groundTop:
            thing.rect.bottom = groundTop
            thing.onGround = True
            return True
        else:
            return False


    def checkPlayerCollision(self, rect):
        collisions = []
        #ignore player-player collision when training/running  models
        if not self.controlledByNN:
            for player in self.players:
                if player.rect is rect:
                    continue
                if rect.colliderect(player.rect):
                    collisions.append(player.rect)
        for thing in self.objects:
            if thing.rect is rect:
                continue
            if rect.colliderect(thing.rect):
                collisions.append(thing.rect)
        for i in self.levels[self.activeLevel].objects:
            if i.rect is rect:
                continue
            if rect.colliderect(i.rect):
                collisions.append(i.rect)
        if rect.colliderect(self.ground.rect):
            collisions.append(self.ground.rect)
        if len(collisions) > 0:
            return True, collisions
        else:
            return False, []
        
    def checkPointCollision(self, pointX, pointY, thisPlayer):
        #ignore raycast contact with other players if training models
        if not self.controlledByNN:
            for player in self.players:
                if thisPlayer is player:
                    continue
                if player.rect.collidepoint(pointX, pointY):
                    return True, 0
        for thing in self.objects:
            if thing.rect.collidepoint(pointX, pointY):
                return True, 0
        for i in self.levels[self.activeLevel].objects:
            if i.rect.collidepoint(pointX, pointY):
                return True, 0
        for i in self.levels[self.activeLevel].spikes:
            if i.rect.collidepoint(pointX, pointY):
                return True, 1
        if self.ground.rect.collidepoint(pointX, pointY):
            return True, 0
        return False, 0
        
    def getDeltaTime(self):
        return self.deltaTime

    def _checkEvents(self):
        #self.up = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._keyDownEvents(event)
            elif event.type == pygame.KEYUP:
                self._keyUpEvents(event)
        
    def _keyDownEvents(self, event):
        if event.key == pygame.K_q:
            self.programRunning = False
        if event.key == pygame.K_o:
            self.display = not self.display
        if event.key == pygame.K_r:
            self.reset = True
        if event.key == pygame.K_RIGHT:
            self.leftRight = 1
        if event.key == pygame.K_LEFT:
            self.leftRight = -1
        if event.key == pygame.K_UP:
            self.up = 1
        if event.key == pygame.K_DOWN:
            self.down = 1
        if event.key == pygame.K_d:
            self.otherright = True
        if event.key == pygame.K_a:
            self.otherleft = True
        if event.key == pygame.K_w:
            self.otherup = True
        if event.key == pygame.K_s:
            self.otherdown = True
        if event.key == pygame.K_SPACE:
            self.used = True
        

    def _keyUpEvents(self, event):
        if event.key == pygame.K_RIGHT and self.leftRight == 1:
            self.leftRight = 0
        if event.key == pygame.K_LEFT and self.leftRight == -1:
            self.leftRight = 0
        if event.key == pygame.K_UP:
            self.up = -1
        if event.key == pygame.K_DOWN:
            self.down = -1
        if event.key == pygame.K_d:
            self.otherright = False
        if event.key == pygame.K_a:
            self.otherleft = False
        if event.key == pygame.K_w:
            self.otherup = False
        if event.key == pygame.K_s:
            self.otherdown = False
        if event.key == pygame.K_SPACE:
            self.used = False
            self.alreadyUsed = False

    def drawBackground(self):
        self.screen.fill("#ffffff")

    def drawAll(self, gamestate, framesAlive = 0):
        if self.rayCastOnly:
            rad_increment = 2*math.pi / len(self.players[0].sensingLinesData)
            for i in range(len(self.players[0].sensingLinesData)):
                radians = rad_increment * i
                if self.players[0].sensingLinesDanger[i] == 0:
                    color = "#008000"
                else:
                    color = "#f00000"
                pygame.draw.line(self.screen, color, (self.players[0].rect.centerx - self.cameraX, self.players[0].rect.centery), (self.players[0].rect.centerx - self.cameraX + math.cos(radians)*(1-self.players[0].sensingLinesData[i])*140, self.players[0].rect.centery + math.sin(radians)*(1-self.players[0].sensingLinesData[i])*140), 2)
            """
            for b in range(math.floor(len(self.players[0].verticalLinesData) / 2)):
                if self.players[0].verticalLinesDanger[b] == 0:
                    color = "#000000"
                else:
                    color = "#f00000"
                pygame.draw.circle(self.screen, color, (self.players[0].rect.centerx - self.cameraX + (b+1)*self.players[0].verticalCheckSpacing, self.players[0].rect.centery + self.players[0].verticalLinesData[b*2]*140), 2)
                pygame.draw.circle(self.screen, color, (self.players[0].rect.centerx - self.cameraX + (b+1)*self.players[0].verticalCheckSpacing, self.players[0].rect.centery + self.players[0].verticalLinesData[b*2+1]*140), 2)
                """

        if True:#not self.rayCastOnly:
            self.screen.blit(self.ground.surface, self.ground.rect)

        self.flagRender.rect.midbottom = self.levels[self.activeLevel].flagPos

        if True:#not self.rayCastOnly:
            self.drawThing(self.flagRender.surface, self.flagRender.rect)

            for i in self.players:
                self.drawThing(i.surface, i.rect)
            for i in self.objects:
                self.drawThing(i.surface, i.rect)
            for i in self.levels[self.activeLevel].objects:
                self.drawThing(i.surface, i.rect)
            for i in self.levels[self.activeLevel].spikes:
                self.drawThing(i.surface, i.rect)
        
            #self.text = self.font.render(str(self.players[0].sensingLinesDanger), False, "#000000")
        self.text = self.font.render("time: " + str(math.floor(self.myTime)/1000), False, "#000000")
        self.screen.blit(self.text, (60, 200))
        self.text = self.font.render("fps: " + str(math.floor(self.clock.get_fps()*10)/10), False, "#000000")
        self.screen.blit(self.text, (60, 170))
        self.text = self.font.render("score: " + str(self.score), False, "#000000")
        self.screen.blit(self.text, (800, 140))
        self.text = self.font.render("reward: " + str(self.currentReward), False, "#000000")
        self.screen.blit(self.text, (800, 170))
        #self.players[0].x - self.levels[self.activeLevel].flagPos[0]
        if self.bonusStats:
            self.text = self.font.render("score/time: " + str(self.score / ((self.myTime+0.001) / 1000)), False, "#000000")
            self.screen.blit(self.text, (800, 110))
            self.text = self.font.render("gameState: " + str(self.gameState), False, "#000000")
            self.screen.blit(self.text, (60, 270))
            self.text = self.font.render("right: " + str(self.gameState[0]) + ", " + str(self.gameState[1]), False, "#000000")
            self.screen.blit(self.text, (60, 110))
            self.text = self.font.render("left: " + str(self.gameState[int(len(self.gameState)/2)]) + ", " + str(self.gameState[int(len(self.gameState)/2 + 1)]), False, "#000000")
            self.screen.blit(self.text, (60, 80))
            self.text = self.font.render("bottom: " + str(self.gameState[int(len(self.gameState)/4)]) + ", " + str(self.gameState[int(len(self.gameState)/4 + 1)]), False, "#000000")
            self.screen.blit(self.text, (400, 110))
            self.text = self.font.render("top: " + str(self.gameState[int(len(self.gameState)/4 * 3)]) + ", " + str(self.gameState[int(len(self.gameState)/4 * 3 + 1)]), False, "#000000")
            self.screen.blit(self.text, (400, 80))
        else:
            self.text = self.font.render("x dist: " + str(self.players[0].x - self.levels[self.activeLevel].flagPos[0]), False, "#000000")
            self.screen.blit(self.text, (800, 110))
            self.text = self.font.render("y dist: " + str(self.players[0].y - self.levels[self.activeLevel].flagPos[1]), False, "#000000")
            self.screen.blit(self.text, (60, 110))

        if self.controlledByNN:
            self.text = self.font.render("frame: " + str(framesAlive), False, "#000000")
            self.screen.blit(self.text, (800, 270))
        
        #pygame.draw.line(self.screen, "#008000", (self.players[0].rect.centerx - self.cameraX, self.players[0].rect.centery), (self.players[0].rect.centerx - self.cameraX + (1-self.players[0].sensingLinesData[0])*140, self.players[0].rect.centery), 4)
        #abs(self.players[0].sensingLinesData[i]-1)
        #self.text = self.font.render("newInput: " + str(gamestate), False, "#000000")
        #self.screen.blit(self.text, (60, 140))
        #textToRender = "time: " + str((pygame.time.get_ticks()-self.timeElapsed) / 1000)
        #self.text = self.font.render(textToRender, False, "#000000")
        #self.screen.blit(self.text, (60, 200))
        if self.displayRecordCooldown > 0:
            if self.recordMargin <= 0:
                recordColor = "#0c22c7"
            else:
                recordColor = "#b50b0b"
            recordText = "      ( " + str(self.recordMargin) + " )"
            self.text = self.font.render(recordText, False, recordColor)
            self.screen.blit(self.text, (60, 230))

        
                



    def drawThing(self, surface, pos):
        self.screen.blit(surface, (pos.x - self.cameraX, pos.y))

    def update(self, inputs):
        #print(str(inputs))
        self.deltaTime = self.clock.get_time()
        self.displayRecordCooldown -= 1
        #self.checkMainPlayerEvents(self.players[0])
        self.checkPlayerEvents(self.players, inputs)
        if self.reset:
            self.resetLevel()
            self.resetTime()
            self.reset = False
        self.checkWin()
        self.checkLoss()

        if self.players[0].rect.x > self.levels[self.activeLevel].farEnd - self.screen.get_width()/2 and self.levels[self.activeLevel].scrolling:
            self.cameraX += (self.levels[self.activeLevel].farEnd - self.screen.get_width() - self.cameraX) / 10
            if abs(self.cameraX - (self.levels[self.activeLevel].farEnd - self.screen.get_width())) < 0.001:
                self.cameraX = self.levels[self.activeLevel].farEnd - self.screen.get_width()
        elif self.players[0].rect.x > self.screen.get_width()/2 and self.levels[self.activeLevel].scrolling:
            self.cameraX += (self.players[0].rect.x - self.screen.get_width()/2 - self.cameraX) / 10
            if abs(self.cameraX - (self.players[0].rect.x - self.screen.get_width()/2)) < 0.001:
                self.cameraX = self.players[0].rect.x - self.screen.get_width()/2
        else:
            self.cameraX += (0 - self.cameraX) / 10
            if self.cameraX < 0.001:
                self.cameraX = 0
        newInputs = []#(self.players[0].x - self.flagRender.rect.x)/(self.flagRender.rect.x+0.0000001)-1]
        for i in range(self.players[0].sensingLinesCount):
            newInputs.append(abs(self.players[0].sensingLinesData[i]-1))
            newInputs.append(self.players[0].sensingLinesDanger[i])
        if not self.stateBased:
            newInputs.append(self.players[0].xVelocity)
            newInputs.append(self.players[0].yVelocity)
            newInputs.append(self.timeDeathAmount - ((self.myTime + 0.001) / 1000))
            #newInputs.append(self.players[0].x - self.levels[self.activeLevel].flagPos[0])
            #newInputs.append(self.players[0].y - self.levels[self.activeLevel].flagPos[1])
        return newInputs


    def checkMainPlayerEvents(self, player, inputs):
        if inputs[0] > 0:
            player.right = True
            player.move(1)
        else:
            player.right = False

        if inputs[0] < 0:
            player.left = True
            player.move(-1)
        else:
            player.left = False
            
        if inputs[1] > 0:
            player.jump()

    def checkPlayerActivate(self, player):
        if self.used and not self.alreadyUsed:
            self.alreadyUsed = True
            player.use()
        else:
            return
            #player.activate = False
        
    def checkPlayerEvents(self, players, inputs):
        f = 0
        for i in players:
            if not i == self.players[0]:
                if self.otherright:
                    i.right = True
                    i.move(1)
                else:
                    i.right = False
                if self.otherleft:
                    i.left = True
                    i.move(-1)
                else:
                    i.left = False
                if self.otherup:
                    i.jump()
            else:
                self.checkMainPlayerEvents(self.players[0], inputs)
            f += 1
            i.updatePosition()
            if i == self.players[0]:
                #self.checkPlayerActivate(i)
                i.updateSensingLines()
            #print(str(f) + ": " + i.item.itemType)
            #print(str(f) + ": " + i.toString())

    def getNNInputs(self, player):
        inputs = []

        # raycasts. final amount is 2x the amount of raycasts we have. 8 casts = 16 data points
        for distance, danger in zip(
            player.sensingLinesData,
            player.sensingLinesDanger
        ):
            inputs.append(1-distance)
            inputs.append(danger)

        # Normalized velocities
        inputs.append(player.xVelocity / player.MAX_SPEED)
        inputs.append(player.yVelocity / player.TERMINAL_VELOCITY)

        # Goal direction
        goalX, goalY = self.levels[self.activeLevel].flagPos

        dx = goalX - player.rect.centerx
        dy = goalY - player.rect.centery

        # we don't care about the detail of the distance if it's more than 600 left-right or 300 up-down
        inputs.append(np.clip(dx / 600, -1, 1))
        inputs.append(np.clip(dy / 300, -1, 1))
            
        # grounded flag
        inputs.append(float(player.onGround))

        return np.asarray(inputs, dtype=float)

    def nnFrame(self, maxFrames = 1800):
        level = self.levels[self.activeLevel]

        # making sure we set the rect of the flag before we check if we won or not
        # normally isn't set until first drawing frame for some reason
        self.flagRender.rect.midbottom = level.flagPos

        for player in self.players:

            # ignore the dead ones
            if not player.alive:
                continue

            # update player's raycast data
            player.updateSensingLines()

            # get inputs from NN
            inputs = self.getNNInputs(player)
            # ask NN what to do with those
            outputs = player.brain.forward(inputs)

            #model spits out numbers between -1 and 1. We will do stuff if the number is greater than 0.3
            left, right, jump = outputs > 0.3

            # set movement states for the player
            player.left = bool(left)
            player.right = bool(right)

            # actually move
            if left:
                player.move(-1)

            if right:
                player.move(1)

            if jump:
                player.jump()

            # run the physics with our new inputs
            player.updatePosition()
            player.framesAlive += 1

            # track progress
            player.bestX = max(player.bestX, player.rect.centerx)

            # judge it harshly. further right is just better always
            player.fitness = player.bestX - player.startX

            # did it win
            if player.rect.colliderect(self.flagRender.rect):
                player.alive = False
                player.finished = True

                # less frames alive is faster and a higher fitness. should account for flag distance without biasing what side of the flag you touched
                player.fitness = level.flagPos[0] - player.startX + 10000 + maxFrames - player.framesAlive

            # did it die?
            elif any(player.rect.colliderect(spike.rect) for spike in level.spikes):
                player.alive = False
            elif player.lastX == player.rect.centerx and player.lastY == player.rect.centery and player.onGround:
                player.alive = False


            elif player.framesAlive >= maxFrames:
                player.alive = False

            player.lastX = player.rect.centerx
            player.lastY = player.rect.centery

    def runNN(self, maxFrames = 1800):
        self.programRunning = True

        for frame in range(maxFrames):

            # did human close the game
            self._checkEvents()
            if not self.programRunning:
                return False

            # omg are all subjects dead
            if not any(p.alive for p in self.players):
                break

            # ok whew some are still alive

            # let's get rolling then
            self.nnFrame(maxFrames)

            # human watching?
            if self.display:
                leader = max(self.players, key=lambda p: p.rect.centerx)
                level = self.levels[self.activeLevel]

                if level.scrolling:
                    maxCamera = max(0, level.farEnd - self.screen.get_width())
                    self.cameraX = max(0, min(maxCamera, leader.rect.centerx - 640))

                self.drawBackground()
                self.drawAll(self.gameState, frame)
                pygame.display.flip()
                if self.nnTimeTick:
                    self.clock.tick(60)
                else:
                    self.clock.tick(0)

        # we're done here, dump the data
        return [(p.brain, p.fitness, p.finished) for p in self.players]

    def resetAndRestartNNBrains(self, brains):
        self.players = []

        for brain in brains:
            player = Player(self.spawnPoint[0], self.spawnPoint[1], 10, 0.3, 1, 4, 10, self)

            player.brain = brain
            player.alive = True
            player.finished = False
            player.fitness = 0
            player.framesAlive = 0
            player.bestX = player.rect.centerx
            player.startX = player.rect.centerx
            player.lastX = player.startX - 100
            player.lastY = player.rect.centery
            
            self.players.append(player)

        self.cameraX = 0
        self.score = 0
        self.currentReward = 0
        self.done = False
        self.won = False
        self.reset = False
        self.programRunning = True

        self.resetTime()