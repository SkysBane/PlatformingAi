import math
from pathlib import Path

import numpy as np
import pygame

from ground import Ground
from levels import build_levels
from NN import NeuralNetwork
from player import Player
from timing import FixedStepClock, RenderClock, SIMULATION_HZ, STEP_SECONDS

SCREEN_SIZE = (1280, 720)
RECORDS_PATH = Path(__file__).with_name("records.local.txt")


class Flag:
    def __init__(self) -> None:
        self.rect = pygame.Rect(0, 0, 10, 20)

    def draw(self, screen, camera_x):
        x = self.rect.x - camera_x
        y = self.rect.y
        pygame.draw.rect(screen, "#1cfc03", (x, y, 10, 7))
        pygame.draw.rect(screen, "#1cfc03", (x, y, 3, 20))


class Main:
    def __init__(self, startLevel = 0, repeatLevelForever = False, playerXOveride = None, playerYOveride = None, playerXvelOveride = None, playerYvelOveride = None, display = True, rayCastOnly = False, bonusStats = False, timedDeath=True, timeDeathAmount = 30, stateBased = False, controlledByNN = False, populationSize=1):
        self.screen = None
        if display:
            pygame.display.init()
            pygame.font.init()
            self.screen = pygame.display.set_mode(SCREEN_SIZE)
            pygame.display.set_caption("Prototype Platformer")
            self.font = pygame.font.Font(None, 25)
        self.render_clock = RenderClock()
        self.elapsed_steps = 0
        self.displayRecordCooldown = 0
        self.recordMargin = 0
        self.display = display
        self.rayCastOnly = rayCastOnly
        self.bonusStats = bonusStats
        self.timedDeath = timedDeath
        self.timeDeathAmount = timeDeathAmount
        self.stateBased = stateBased
        self.controlledByNN = controlledByNN

        self.reset = False
        self.done = False
        self.gameState = [1, 0] * 8 + [0, 11, 30]

        self.currentReward = 0
        self.won = False
        self.score = 0

        self.leftRight = 0
        self.up = -1
        self.otherright = False
        self.otherleft = False
        self.otherup = False

        self.spawnPoint = (100, 640)

        if playerXOveride is not None and playerYOveride is not None:
            if playerXvelOveride is not None and playerYvelOveride is not None:
                self.players = [Player(playerXOveride, playerYOveride, 10, 0.3, 1, 4, 10, self, playerXvelOveride, playerYvelOveride)]
            else:
                self.players = [Player(playerXOveride, playerYOveride, 10, 0.3, 1, 4, 10, self)]
        else:
            self.players = [Player(self.spawnPoint[0], self.spawnPoint[1], 10, 0.3, 1, 4, 10, self)]
        self.objects = []
        self.ground = Ground(600, SCREEN_SIZE[1] - 80, 80)
        self.programRunning = False
        self.flagRender = Flag()

        self.cameraX = 0


        self.repeatLevelForever = repeatLevelForever
        self.activeLevel = startLevel
        self.levels = build_levels()
        self.flagRender.rect.midbottom = self.levels[self.activeLevel].flagPos

        if self.controlledByNN and populationSize:
            self.resetAndRestartNNBrains(
                NeuralNetwork(21, 3, 1, 21) for _ in range(populationSize)
            )

    def quitPygame(self):
        pygame.quit()

    def getPlayerStats(self):
        return self.players[0].x, self.players[0].y, self.players[0].xVelocity, self.players[0].yVelocity

    @property
    def elapsed_seconds(self):
        return self.elapsed_steps / SIMULATION_HZ

    def step(self, inputs=(0, 0)):
        """Advance one simulation step and return the observation and episode status."""
        if len(inputs) == 3:
            right, left, jump = inputs
            inputs = (right - left, jump)
        self.currentReward = 0
        self.done = False
        self.won = False
        self.elapsed_steps += 1
        elapsed = self.elapsed_seconds
        self.gameState = self.update(inputs)

        if self.done and not self.won:
            self.currentReward = -10
        elif self.players[0].xVelocity > 0 and self.currentReward == 0:
            self.currentReward = 0.0001

        result = (self.gameState, self.currentReward, self.done, self.won, self.score, elapsed)
        if self.stateBased:
            player = self.players[0]
            return (*result, (player.xVelocity, player.yVelocity))
        return result

    def run(self, fps=60):
        if self.controlledByNN:
            return self.runNN(fps=fps)

        self.programRunning = True
        self.resetTime()
        for steps in self._display_frames(fps):
            for _ in range(steps):
                self.step((self.leftRight, self.up))
            self._render()

    def _display_frames(self, fps):
        """Yield the number of physics updates due before each rendered frame."""
        if self.screen is None:
            raise RuntimeError("Interactive play needs a display")
        self.render_clock = RenderClock()
        schedule = FixedStepClock()
        while self.programRunning:
            elapsed = self.render_clock.tick(fps)
            self._checkEvents()
            if not self.programRunning:
                break
            yield schedule.advance(elapsed)

    def _render(self):
        if self.controlledByNN:
            leader = max(self.players, key=lambda player: player.rect.centerx)
            level = self.levels[self.activeLevel]
            if level.scrolling:
                width = SCREEN_SIZE[0]
                self.cameraX = max(0, min(level.farEnd - width, leader.rect.centerx - width // 2))

        self.drawBackground()
        self.drawAll()
        pygame.display.flip()

    def checkWin(self):
        if not self.players[0].rect.colliderect(self.flagRender.rect):
            return
        if self.display:
            self.checkRecord()
        self.resetLevel()
        self.resetTime()
        self.done = True
        self.won = True
        self.score += 1
        self.currentReward = 10
        if not self.repeatLevelForever:
            self.activeLevel = (self.activeLevel + 1) % len(self.levels)
            self.flagRender.rect.midbottom = self.levels[self.activeLevel].flagPos

    def checkLoss(self):
        timed_out = self.timedDeath and self.elapsed_seconds >= self.timeDeathAmount
        hit_spike = any(
            self.players[0].rect.colliderect(spike.rect)
            for spike in self.levels[self.activeLevel].spikes
        )
        if timed_out or hit_spike:
            self.resetLevel()
            self.resetTime()
            self.done = True

    def resetLevel(self):
        player = self.players[0]
        player.rect.midbottom = self.spawnPoint
        player.x, player.y = self.spawnPoint
        player.xVelocity = 0
        player.yVelocity = 0
        player.onGround = False
        player.lastFrameOnGround = False
        player.cyoteTimer = 0

    def checkRecord(self):
        elapsed_ms = self.elapsed_steps * 1000 // SIMULATION_HZ
        try:
            records = RECORDS_PATH.read_text(encoding="utf-8").splitlines()
        except FileNotFoundError:
            records = []
        records.extend([""] * (self.activeLevel + 1 - len(records)))
        previous = records[self.activeLevel]
        if previous:
            self.displayRecordCooldown = 150
            self.recordMargin = (elapsed_ms - int(previous)) / 1000
        if not previous or elapsed_ms < int(previous):
            records[self.activeLevel] = str(elapsed_ms)
            RECORDS_PATH.write_text("\n".join(records) + "\n", encoding="utf-8")

    def resetTime(self):
        self.elapsed_steps = 0

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
        return STEP_SECONDS * 1000

    def _checkEvents(self):
        if self.screen is None:
            return
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.programRunning = False
            elif event.type == pygame.KEYDOWN:
                self._keyDownEvents(event)
            elif event.type == pygame.KEYUP:
                self._keyUpEvents(event)

    def _keyDownEvents(self, event):
        if event.key == pygame.K_q:
            self.programRunning = False
        if event.key == pygame.K_r:
            self.reset = True
        if event.key == pygame.K_RIGHT:
            self.leftRight = 1
        if event.key == pygame.K_LEFT:
            self.leftRight = -1
        if event.key == pygame.K_UP:
            self.up = 1
        if event.key == pygame.K_d:
            self.otherright = True
        if event.key == pygame.K_a:
            self.otherleft = True
        if event.key == pygame.K_w:
            self.otherup = True


    def _keyUpEvents(self, event):
        if event.key == pygame.K_RIGHT and self.leftRight == 1:
            self.leftRight = 0
        if event.key == pygame.K_LEFT and self.leftRight == -1:
            self.leftRight = 0
        if event.key == pygame.K_UP:
            self.up = -1
        if event.key == pygame.K_d:
            self.otherright = False
        if event.key == pygame.K_a:
            self.otherleft = False
        if event.key == pygame.K_w:
            self.otherup = False

    def drawBackground(self):
        self.screen.fill("#ffffff")

    def drawAll(self):
        if self.rayCastOnly:
            rad_increment = 2*math.pi / len(self.players[0].sensingLinesData)
            for i in range(len(self.players[0].sensingLinesData)):
                radians = rad_increment * i
                if self.players[0].sensingLinesDanger[i] == 0:
                    color = "#008000"
                else:
                    color = "#f00000"
                pygame.draw.line(self.screen, color, (self.players[0].rect.centerx - self.cameraX, self.players[0].rect.centery), (self.players[0].rect.centerx - self.cameraX + math.cos(radians)*(1-self.players[0].sensingLinesData[i])*140, self.players[0].rect.centery + math.sin(radians)*(1-self.players[0].sensingLinesData[i])*140), 2)

        pygame.draw.rect(self.screen, "#000000", self.ground.rect)
        self.flagRender.draw(self.screen, self.cameraX)

        level = self.levels[self.activeLevel]
        for objects in (self.players, self.objects, level.objects, level.spikes):
            for obj in objects:
                self.drawThing(obj.surface, obj.rect)

        self.text = self.font.render("time: " + f"{self.elapsed_seconds:.3f}", False, "#000000")
        self.screen.blit(self.text, (60, 200))
        self.text = self.font.render(f"fps: {self.render_clock.fps:.1f}", False, "#000000")
        self.screen.blit(self.text, (60, 170))
        self.text = self.font.render("score: " + str(self.score), False, "#000000")
        self.screen.blit(self.text, (800, 140))
        #self.text = self.font.render("reward: " + str(self.currentReward), False, "#000000")
        #self.screen.blit(self.text, (800, 170))
        if self.bonusStats:
            self.text = self.font.render("score/time: " + str(self.score / max(self.elapsed_seconds, STEP_SECONDS)), False, "#000000")
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
            self.text = self.font.render("frame: " + str(self.elapsed_steps), False, "#000000")
            self.screen.blit(self.text, (800, 270))

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
        self.displayRecordCooldown -= 1
        self.checkPlayerEvents(self.players, inputs)
        if self.reset:
            self.resetLevel()
            self.resetTime()
            self.reset = False
        self.flagRender.rect.midbottom = self.levels[self.activeLevel].flagPos
        self.checkWin()
        if not self.done:
            self.checkLoss()

        if self.players[0].rect.x > self.levels[self.activeLevel].farEnd - SCREEN_SIZE[0]/2 and self.levels[self.activeLevel].scrolling:
            self.cameraX += (self.levels[self.activeLevel].farEnd - SCREEN_SIZE[0] - self.cameraX) / 10
            if abs(self.cameraX - (self.levels[self.activeLevel].farEnd - SCREEN_SIZE[0])) < 0.001:
                self.cameraX = self.levels[self.activeLevel].farEnd - SCREEN_SIZE[0]
        elif self.players[0].rect.x > SCREEN_SIZE[0]/2 and self.levels[self.activeLevel].scrolling:
            self.cameraX += (self.players[0].rect.x - SCREEN_SIZE[0]/2 - self.cameraX) / 10
            if abs(self.cameraX - (self.players[0].rect.x - SCREEN_SIZE[0]/2)) < 0.001:
                self.cameraX = self.players[0].rect.x - SCREEN_SIZE[0]/2
        else:
            self.cameraX += (0 - self.cameraX) / 10
            if self.cameraX < 0.001:
                self.cameraX = 0
        newInputs = []
        for i in range(self.players[0].sensingLinesCount):
            newInputs.append(abs(self.players[0].sensingLinesData[i]-1))
            newInputs.append(self.players[0].sensingLinesDanger[i])
        if not self.stateBased:
            newInputs.append(self.players[0].xVelocity)
            newInputs.append(self.players[0].yVelocity)
            newInputs.append(self.timeDeathAmount - self.elapsed_seconds)
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

    def checkPlayerEvents(self, players, inputs):
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
            i.updatePosition()
            if i == self.players[0]:
                i.updateSensingLines()

    def getNNInputs(self, player):
        inputs = []

        for distance, danger in zip(
            player.sensingLinesData,
            player.sensingLinesDanger
        ):
            inputs.append(1-distance)
            inputs.append(danger)

        inputs.append(player.xVelocity / player.MAX_SPEED)
        inputs.append(player.yVelocity / player.TERMINAL_VELOCITY)

        goalX, goalY = self.levels[self.activeLevel].flagPos

        dx = goalX - player.rect.centerx
        dy = goalY - player.rect.centery

        inputs.append(np.clip(dx / 600, -1, 1))
        inputs.append(np.clip(dy / 300, -1, 1))

        inputs.append(float(player.onGround))

        return np.asarray(inputs, dtype=float)

    def nnFrame(self, maxFrames = 1800):
        self.elapsed_steps += 1
        level = self.levels[self.activeLevel]

        self.flagRender.rect.midbottom = level.flagPos

        for player in self.players:

            if not player.alive:
                continue

            player.updateSensingLines()

            inputs = self.getNNInputs(player)
            outputs = player.brain.forward(inputs)

            left, right, jump = outputs > 0.3

            player.left = bool(left)
            player.right = bool(right)

            if left:
                player.move(-1)

            if right:
                player.move(1)

            if jump:
                player.jump()

            player.updatePosition()
            player.framesAlive += 1

            player.bestX = max(player.bestX, player.rect.centerx)

            player.fitness = player.bestX - player.startX

            if player.rect.colliderect(self.flagRender.rect):
                player.alive = False
                player.finished = True

                player.fitness = level.flagPos[0] - player.startX + 10000 + maxFrames - player.framesAlive

            elif any(player.rect.colliderect(spike.rect) for spike in level.spikes):
                player.alive = False
            elif player.lastX == player.rect.centerx and player.lastY == player.rect.centery and player.onGround:
                player.alive = False


            elif player.framesAlive >= maxFrames:
                player.alive = False

            player.lastX = player.rect.centerx
            player.lastY = player.rect.centery

    def runNN(self, maxFrames=1800, fps=60, fast = False):
        self.programRunning = True
        if self.display and not fast:
            for steps in self._display_frames(fps):
                for _ in range(steps):
                    if self.elapsed_steps >= maxFrames or not any(p.alive for p in self.players):
                        break
                    self.nnFrame(maxFrames)
                self._render()
                if self.elapsed_steps >= maxFrames or not any(p.alive for p in self.players):
                    break
            if not self.programRunning:
                return False
        else:
            while self.elapsed_steps < maxFrames and any(p.alive for p in self.players):
                if self.display:
                    self._checkEvents()
                    if not self.programRunning:
                        return False
                
                self.nnFrame(maxFrames)
                if self.display and self.render_clock.tick(fps, wait=False) is not None:
                    self._render()

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
