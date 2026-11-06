import pygame
import sys
import math
from item import Item
from randomColor import Color
from data import Data

class Player():
    def __init__(self, x, y, JUMP_POWER, MOVE_SPEED, GRAVITATIONAL_CONSTANT, MAX_SPEED, TERMINAL_VELOCITY, Main, xVel = 0, yVel = 0):
        self.xVelocity = xVel
        self.yVelocity = yVel
        self.x = x
        self.y = y
        self.onGround = False
        self.lastFrameOnGround = False
        self.surface = pygame.surface.Surface((10, 20))
        self.rect = self.surface.get_rect(midbottom = (x, y))
        self.color = Color()
        self.surface.fill(self.color)
        self.main = Main
        self.JUMP = 0 - JUMP_POWER
        self.SPEED = MOVE_SPEED
        self.GRAVITY = GRAVITATIONAL_CONSTANT
        self.MAX_SPEED = MAX_SPEED
        self.TERMINAL_VELOCITY = TERMINAL_VELOCITY
        self.CYOTE = 0.047
        self.right = False
        self.left = False
        self.up = False
        self.down = False
        self.cyoteTimer = 0.000
        self.item = Item(self)
        #self.item = Item(self, "block", Data(newType="wood"))
        

        self.sensingLinesCount = 8
        self.sensingLinesIncrement = 2*math.pi / self.sensingLinesCount
        self.sensingLines = []
        for i in range(self.sensingLinesCount):
            self.sensingLines.append(i*self.sensingLinesIncrement)
        self.sensingLinesData = []
        for i in range(self.sensingLinesCount):
            self.sensingLinesData.append(0)
        self.sensingLinesDanger = []
        for i in range(self.sensingLinesCount):
            self.sensingLinesDanger.append(0)
        self.SENSINGLINESDISTANCE = 140
        self.distanceIncrements = 32
        self.distanceIncrement = self.SENSINGLINESDISTANCE / self.distanceIncrements

        self.verticalCheckDistance = 140
        self.verticalChecksCount = 5
        self.verticalCheckSpacing = self.verticalCheckDistance / self.verticalChecksCount
        self.verticalIncrements = 10
        self.verticalSpread = 140
        self.verticalSpacing = self.verticalSpread / self.verticalIncrements

        self.verticalLinesData = []
        self.verticalLinesDanger = []
        for i in range(self.verticalChecksCount*2):
            self.verticalLinesData.append(0)
            self.verticalLinesDanger.append(0)



    def updateSensingLines(self):
        count = 0
        for i in self.sensingLines:
            for f in range(1, self.distanceIncrements+1):
                data = self.checkPoint((math.cos(i) * (f*self.distanceIncrement)) + self.rect.centerx, (math.sin(i) * (f*self.distanceIncrement)) + self.rect.centery)
                if data[0]:
                    self.sensingLinesData[count] = 1-((f*self.distanceIncrement) / self.SENSINGLINESDISTANCE)
                    self.sensingLinesDanger[count] = data[1]
                    break
                elif f == self.distanceIncrements:
                    self.sensingLinesData[count] = 0
                    self.sensingLinesDanger[count] = data[1]
            count += 1
        for d in range(1, self.verticalChecksCount+1):
            for q in range(self.verticalIncrements):
                data = self.checkPoint(self.rect.centerx + d*self.verticalCheckSpacing, self.rect.centery + q*self.verticalSpacing)
                if data[0]:
                    self.verticalLinesData[(d-1)*2] = q*self.verticalSpacing / self.verticalSpread
                    self.verticalLinesDanger[(d-1)*2] = data[1]
                elif q == self.verticalIncrements-1:
                    self.verticalLinesData[(d-1)*2] = 1
                    self.verticalLinesDanger[(d-1)*2] = data[1]

                data = self.checkPoint(self.rect.centerx + d*self.verticalCheckSpacing, self.rect.centery - q*self.verticalSpacing)
                if data[0]:
                    self.verticalLinesData[(d-1)*2 + 1] = 0 - q*self.verticalSpacing / self.verticalSpread
                    self.verticalLinesDanger[(d-1)*2 + 1] = data[1]
                elif q == self.verticalIncrements-1:
                    self.verticalLinesData[(d-1)*2 + 1] = -1
                    self.verticalLinesDanger[(d-1)*2 + 1] = data[1]

    def checkPoint(self, x, y):
        return self.main.checkPointCollision(x, y, self)

    def updatePosition(self):
        """Updates the position of the player based on their speeds"""
        self.cyoteTimer -= 1/60
        if self.cyoteTimer < 0.000:
            self.cyoteTimer = 0
        if abs(self.xVelocity) > self.MAX_SPEED:
            self.xVelocity = self.xVelocity/abs(self.xVelocity) * self.MAX_SPEED
        if self.yVelocity > self.TERMINAL_VELOCITY:
            self.yVelocity = self.TERMINAL_VELOCITY

        self.x = self.rect.midbottom[0]
        self.y = self.rect.bottom

        self.x += self.xVelocity
        self.y += self.yVelocity

        #if self.x < -500:
        #    self.x = 1999
        #elif self.x > 2000:
        #    self.x = -499

        self.goToPos()
        self.checkCollision()

    def checkCollisionAndEscape(self):
        i = 0
        isColliding, collisions = self.main.checkPlayerCollision(self.rect)
        while isColliding and i < 10:
            i += 1
            self.escapeCollision(collisions)
            isColliding, collisions = self.main.checkPlayerCollision(self.rect)
        return isColliding, collisions

    def checkCollision(self):
        """Checks collision and then modifies velocities based on result"""
        self.lastFrameOnGround = self.onGround
        self.onGround = self.main.checkGround(self)
        isColliding, collisions = self.checkCollisionAndEscape()
        #if i == 10:
            #pass
            #print("was unable to escape collision properly")
            #pygame.quit()
            #sys.exit() 
        #else:
            #self.y += 1
            #self.goToPos()
            #isColliding = self.main.checkPlayerCollision(self.rect)[0]
            #if isColliding:
                #self.onGround = True
                #if self.yVelocity > 0:
                    #self.yVelocity = 0
            #self.y -= 1
            #self.goToPos()
            
        if self.onGround and not self.lastFrameOnGround:
            if (self.right and self.xVelocity > 0) or (self.left and self.xVelocity < 0):
                self.xVelocity *= 0.8
            else:
                self.xVelocity *= 0.35
        
        if self.lastFrameOnGround and not self.onGround and not self.yVelocity < 0:
            self.cyoteTimer = self.CYOTE

        if self.onGround and not (self.right or self.left):
            if abs(self.xVelocity) < 0.2:
                self.xVelocity = 0
            else:
                self.xVelocity *= 0.8
        else:
            if (self.right and self.xVelocity < 0) or (self.left and self.xVelocity > 0):
                self.xVelocity *= 0.5
            else:
                self.xVelocity *= 0.99

        self.yVelocity += self.GRAVITY

    def jump(self):
        """Makes the player jump if on ground"""
        if (self.onGround or self.cyoteTimer > 0) and not self.yVelocity < 0:
            self.yVelocity = self.JUMP
    
    def move(self, direction):
        """Makes the player move in the given direction (1 or -1)"""
        if self.onGround:
            self.xVelocity += direction * self.SPEED
        else:
            self.xVelocity += direction * self.SPEED

    def use(self):
        used = False
        if self.item.itemType == "empty":
            pass
        if self.item.itemType == "block":
            if self.main.checkGround(self):
                self.y -= 9
            self.y -= 10
            self.goToPos()
            if self.main.checkPlayerCollision(self.rect)[0]:
                self.y += 10
                self.goToPos()
                print("cannot place")
                return "cannot place"
            self.y += 9
            self.goToPos()
            self.main.objects.append(self.item.use())
            self.yVelocity = 0
            self.y -= 10
            self.goToPos()
            used = True

        if used:
            self.item = Item(self)
            
        
    def goToPos(self, x = None, y = None):
        if x == None and y == None:
            self.rect.midbottom = (self.x, self.y)
        elif x == None:
            self.rect.midbottom = (self.x, y)
        elif y == None:
            self.rect.midbottom = (x, self.y)
        else:
            self.rect.midbottom = (x, y)

    def escapeCollision(self, collisions):
        """Shifts the player out of provided collisions"""
        #x = self.x
        #y = self.y
        #isColliding = self.main.checkPlayerCollision(self.rect)[0]
        #i = 0
        #while isColliding and i < 300:
        #    i += 1
        #    if not self.xVelocity == 0:
        #       newX = x + i * (0-self.xVelocity / abs(self.xVelocity))/20
        #   else:
        #        newX = x
        #   if not self.yVelocity == 0:
        #       newY = y + i * (0-self.yVelocity / abs(self.yVelocity))/20
        #   else:
        #       newY = y
        #    self.goToPos(newX, y)
        #   isColliding = self.main.checkPlayerCollision(self.rect)[0]
        #    if not isColliding:
        #       break
        #   self.goToPos(x, newY)
        #   isColliding = self.main.checkPlayerCollision(self.rect)[0]
        #   if not isColliding:
        #        break
        #    self.goToPos(newX, newY)
        #    isColliding = self.main.checkPlayerCollision(self.rect)[0]
            
        
        # second collision system, worse
        #x = self.x
        #y = self.y
        #isColliding = self.main.checkPlayerCollision(self.rect)[0]
        #i = 0
        #while isColliding and i < 100:
        #    i += 1
        #    degree = 0
        #    INCREMENTS = 90
        #    while isColliding and degree <= 360:
        #        degree += 360/INCREMENTS
        #        radians = math.radians(degree + 90)
        #        self.goToPos(x + i*math.cos(radians), y + i*math.sin(radians))
        #        isColliding = self.main.checkPlayerCollision(self.rect)[0]
                
        # original collision system, buggy
        extra = 0
        if abs(self.yVelocity) > 7:
            extra = 0.5*(self.rect.bottom - self.rect.centery)

        for collision in collisions:
            if self.rect.centery - extra < collision.top:
                self.rect.bottom = collision.top
                self.onGround = True
                if self.yVelocity > 0:
                    self.yVelocity = 0
            elif self.rect.centery + extra > collision.bottom and not self.onGround:
                self.rect.top = collision.bottom
                if self.yVelocity < 0:
                    self.yVelocity = 0
            elif self.rect.centerx < collision.centerx:
                self.rect.right = collision.left
                if self.xVelocity > 0:
                    self.xVelocity = 0
            elif self.rect.centerx > collision.centerx:
                self.rect.left = collision.right
                if self.xVelocity < 0:
                    self.xVelocity = 0

    def toString(self):
        return "x: " + str(self.x) + ", y: " + str(self.y) + ", xVel: " + str(self.xVelocity) + ", yVel: " + str(self.yVelocity)
