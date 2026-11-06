from main import Main
from random import random
from player import Player

def indexOfMax(array):
    max = array[0]
    index = 0
    for i in range(len(array)):
        if (array[i] > max):
            index = i
            max = array[i]
    return index


actionsList = []
actionOptions = [[1, -1], [1, 1], [0, -1], [0, 1], [-1, -1], [-1, 1]]


def runForever(actions):
    while True:
        game = Main(1, True)
        for action in actions:
            game.step(action)
            game.tick(60)

def go():
    game = Main(1, True)
    findNextPos(game, 0)
    runForever(actionsList)

def findNextPos(game, depth):
    #if depth > 30:
        #exit()
    #print(depth)
    count = 0
    while count < 6:
        action = actionOptions[count]
        
        myX, myY, myXvel, myYvel = game.getPlayerStats()
        numbers, reward, complete, didWin = game.step(action)
        game.tick(0)
        print(action, abs(myX - game.players[0].x), abs(myY - game.players[0].y), myXvel, myYvel)

        if (didWin):
            actionsList.append(action)
            return "yay"
        elif complete or (abs(myX - game.players[0].x) < 0.3 and abs(myY - game.players[0].y) < 0.3 and depth > 10):
            count += 1
            game.players[0] = Player(myX, myY, 10, 0.3, 1, 4, 10, game, myXvel, myYvel)
            continue
        
        actionsList.append(action)
        nextOutcome = findNextPos(game, depth + 1)
        if nextOutcome is "yay":
            return "yay"
        else:
            actionsList.pop()
            count += 1
            game.players[0] = Player(myX, myY, 10, 0.3, 1, 4, 10, game, myXvel, myYvel)
    return "very bad"
    

# actions:
#   [(-1, 0, 1), (-1, 1)]
#   -1 left, 0 nothing, 1 right | -1 nothing, 1 jump
#


actionsList = []
go()
