from main import Main
from random import random
import math


class stateBased():
    def __init__(self, stats, show = False, debugMode = False, repeatNum = None):
        self.game = Main(7, False, display=show, rayCastOnly=debugMode, stateBased=True)
        self.move = [1, 0]
        self.alive = True
        self.complete = False
        self.gameState = []
        self.reward = 0
        self.done = False
        self.won = False
        self.score = 0
        self.time = 0
        self.superScore = 0
        self.repeatNum = repeatNum

        self.myStats = stats
        if self.repeatNum:
            self.game.activeLevel = self.repeatNum
            self.game.repeatLevelForever = True

    def step(self):
        self.gameState, self.reward, self.done, self.won, self.score, self.time, self.velocities = self.game.step(self.move)

    def run(self):
        while True:#not self.complete:
            #print(self.time)
            self.game._checkEvents()
            self.step()
            self.decide()
            if (self.done) or self.time > 30:
                self.alive = False
                self.complete = True
                self.superScore += self.score
                if self.repeatNum:
                    self.game.activeLevel = self.repeatNum
            if self.game.activeLevel == 8:
                self.complete = True
                self.game.activeLevel = 7
                self.game.score = 0
            if self.won and self.done:
                self.superScore += self.score
                if self.repeatNum:
                    self.game.activeLevel = self.repeatNum
        return self.superScore, self.time, self.won
        
    
    def decide(self):
        right = self.gameState[0]
        rightDanger = self.gameState[1] == 1
        left = self.gameState[int(len(self.gameState)/2)]
        top = self.gameState[int(len(self.gameState)/4 * 3)]
        bottomRight = self.gameState[int(len(self.gameState)/4) - int(len(self.gameState)/8)]
        bottomRightDanger = self.gameState[int(len(self.gameState)/4) - int(len(self.gameState)/8) + 1] == 1
        bottomLeft = self.gameState[int(len(self.gameState)/4) + int(len(self.gameState)/8)]
        bottomLeftDanger = self.gameState[int(len(self.gameState)/4) + int(len(self.gameState)/8) + 1] == 1
        topRight = self.gameState[int(len(self.gameState)/4 * 3) + int(len(self.gameState)/8)]
        topRightDanger = self.gameState[int(len(self.gameState)/4 * 3) + int(len(self.gameState)/8) + 1] == 1
        bottom = self.gameState[int(len(self.gameState)/4)]
        bottomDanger = self.gameState[int(len(self.gameState)/4) + 1] == 1
        #print(self.velocities, rightDanger)
        if bottom > self.myStats[0] and (bottomRightDanger or bottomDanger) and bottomRight < self.myStats[1] and self.velocities[1] > 8:
            self.move = [-1, 0]
        elif bottom < self.myStats[2] and bottom > self.myStats[3] and bottomRight > self.myStats[4] and self.velocities[1] > 7:
            self.move = [-1, 0]
        elif not bottomDanger and bottomRightDanger and bottomRight > self.myStats[5] and bottom > self.myStats[6] and self.velocities[0] > 0:
            self.move = [-1, 0]
        elif bottomLeftDanger and self.velocities[0] < 0:
            self.move = [1, 0]
        elif (right < self.myStats[7] and rightDanger and bottom > self.myStats[8] and self.velocities[0] > 0):
            self.move = [-1, 0]
        elif (right < self.myStats[9] and (not (topRight < self.myStats[10] and topRight > self.myStats[11] and not topRightDanger)) and not top < self.myStats[12]):
            self.move = [1, 1]
        elif (bottomRight > self.myStats[13] or (bottomRightDanger)):
            self.move = [1, 1]
        else:
            self.move = [1, 0]


# 0.1, 0.4, 0.3, 0.1, 0.2, 0.3, 0.5, 0.12, 0.1, 0.35, 0.6, 0.1, 0.4, 0.4 these are the stats made by me that seem to work

# [0.03, 0.37, 0.04999999999999999, 0.0, 0.18000000000000002, 0.3, 0.5, 0.12, 0.1, 0.35, 0.6, 0.1, 0.36000000000000004, 0.4]
# [0.03, 0.28, 0.04999999999999999, 0.0, 0.18000000000000002, 0.21999999999999997, 0.44, 0.12, 0.03, 0.35, 0.51, 0.1, 0.36000000000000004, 0.4]
# [0.03, 0.12, 0.06, 0.0, 0.03, 0.22, 0.39, 0.12, 0.0, 0.32, 0.45, 0.1, 0.33, 0.4]
# [0.0, 0.12, 0.06, 0.0, 0.03, 0.22, 0.39, 0.12, 0.0, 0.32, 0.45, 0.08, 0.33, 0.4]
# [0.0, 0.12, 0.0, 0.0, 0.03, 0.22, 0.39, 0.11, 0.0, 0.32, 0.45, 0.08, 0.33, 0.4]
# [0.0, 0.12, -0.08, 0.0, 0.03, 0.22, 0.39, 0.11, 0.0, 0.32, 0.45, 0.08, 0.33, 0.4]


#ai = stateBased([0.1, 0.4, 0.3, 0.1, 0.2, 0.3, 0.5, 0.12, 0.1, 0.35, 0.6, 0.1, 0.4, 0.4], True, False, 7)
ai = stateBased([0.0, 0.12, -0.08, 0.0, 0.03, 0.22, 0.39, 0.11, 0.0, 0.32, 0.45, 0.08, 0.33, 0.4], True, True)

score, time, won = ai.run()
#print(str(score), str(time), str(won))

def randomize():
    n = 0
    original_state = [0.1, 0.4, 0.3, 0.1, 0.2, 0.3, 0.5, 0.12, 0.1, 0.35, 0.6, 0.1, 0.4, 0.4]
    best_state = original_state
    current_state = best_state
    record = 999
    recordScore = 0
    recordScoreTime = 0
    recordUnset = True
    while n < 50:
        if n == 0:
            ai = stateBased(current_state)
        else:
            current_state = messy(best_state)
            ai = stateBased(current_state)

        score, time, won = ai.run()
        #print(str(time))

        #if best_state != original_state:
        #    print("PANIC: " + str(best_state))

        if (time < record and won):
            record = time
            recordScoreTime = score / time
            recordScore = score
            best_state = current_state
            recordUnset = False
            print("NEW BEST " + str([record, recordScoreTime, recordScore]))
        elif recordUnset and (score > recordScore):
            recordScore = score
            recordScoreTime = score / time
            best_state = current_state
            print("NEW BEST")
        elif (score == recordScore and score / time > recordScoreTime and recordUnset):
            recordScoreTime = score / time
            best_state = current_state
            print("NEW BEST")

        n += 1

        print("GAME: " + str(n) + " set: " + str(current_state) + " | time: " + str(time) + ", score: " + str(score) + ", won: " + str(won))

    if best_state == original_state:
        print("no change")
    return best_state, record

def messy(state):
    new = state.copy()
    for i in range(len(new)):
        if (random() < 0.2):
            new[i] += round((random() - 1) / 10, 2)
    return new

#print(str(messy([0.1, 0.4, 0.3, 0.1, 0.2, 0.3, 0.5, 0.12, 0.1, 0.35, 0.6, 0.1, 0.4, 0.4])))

#print("best state: " + str(randomize()))



             