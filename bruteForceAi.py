from main import Main
from random import random

def indexOfMax(array):
    max = array[0]
    index = 0
    for i in range(len(array)):
        if (array[i] > max):
            index = i
            max = array[i]
    return index

def runForever(actions):
    while True:
        game = Main(8, True)
        for action in actions:
            game.step(action)
            game.tick()




actionsList = []
INTERVAL = 50
ATTEMPTS = 20
done = False
current = 1

while not done:
    scores = []  
    actionsTaken = []
    for attempt in range(ATTEMPTS):
        game = Main(8, True)
        score = 0
        myActions = []
        for actions in range(INTERVAL*current):

            try:
                a = actionsList[actions]
            except:
                print("empty on first")
                for i in range(INTERVAL):
                    actionsList.append([1, -1])
                a = actionsList[actions]

            if (random() < 0.25 and attempt > 0 and actions > INTERVAL*(current-1)):
                if (random() < 0.5):
                    if (random() < 0.5):
                        a = [1, a[1]]
                    else:
                        a = [-1, a[1]]
                else:
                    if (random() < 0.5):
                        a = [a[0], 1]
                    else:
                        a = [a[0], -1]


            
            numbers, reward, complete, didWin = game.step(a)
            if (complete and not didWin):
                score = -1
                break
            if (didWin):
                actionsList = myActions
                done = True
                runForever()
            score += reward
            myActions.append(a)
        scores.append(score)
        actionsTaken.append(myActions)
    actionsList = actionsTaken[indexOfMax(scores)]
    


    current += 1
