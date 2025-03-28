#!/usr/bin/env python3
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Copyright (C) 2008  Nick Redshaw
#    Copyright (C) 2018  Francisco Sanchez Arroyo
#

# TODO
# safe area on new life
# sounds thump

# Notes:
# random.randrange returns an int
# random.uniform returns a float
# p for pause
# j for toggle showing FPS
# o for frame advance whilst paused

from typing import List
import pygame
import sys
import os
import random
from pygame.locals import *
from util.vectorsprites import *
from ship import *
from stage import *
from badies import *
from shooter import *
from soundManager import *

class Asteroids():

    explodingTtl = 180

    def __init__(self):
        self.stage = Stage('Atari Asteroids', (1024, 768))
        self.paused = False
        self.showingFPS = False
        self.frameAdvance = False
        self.gameState = "attract_mode"
        self.rockList = []
        # 
        self.createRocks(1)
        self.saucer = None
        self.secondsCount = 1
        self.score = 0
        self.ship = None
        self.lives = 0
        self.level = 1


    def initialiseGame(self):
        self.gameState = 'playing'
        [self.stage.removeSprite(sprite) for sprite in self.rockList]  # clear old rocks
        if self.saucer is not None:
            self.killSaucer()
        self.startLives = 5
        self.createNewShip()
        self.createLivesList()
        self.score = 0
        self.rockList: List[Rock] = []
        # Set level 1 
        self.level = 1
        self.numRocks = 1
        self.nextLife = 10000

        self.createRocks(self.numRocks)
        self.secondsCount = 1

        rockState = {}
        for index, rock in enumerate(self.rockList):
            rockState[index] = {
                'position': rock.getPos(), # Vector(x,y)
                'heading': rock.getHeading() # Vector(x,y)
            }

        self.current_state = {
            'alien': None, # None or Vector(x,y)
            'ship': {
                'position': self.ship.getPos(), # Vector(x,y)
                'heading': self.ship.getHeading(), # Vector(x,y)
            }, # the whole Ship object
            'rocks': rockState
        }

        # returns observation, reward, and done
        return self.current_state, 0, False

    def createNewShip(self):
        if self.ship:
            [self.stage.spriteList.remove(debris) for debris in self.ship.shipDebrisList]
        self.ship = Ship(self.stage)
        self.stage.addSprite(self.ship.thrustJet)
        self.stage.addSprite(self.ship)

    def createLivesList(self):
        self.lives += 1
        self.livesList = []
        for i in range(1, self.startLives):
            self.addLife(i)

    def addLife(self, lifeNumber):
        self.lives += 1
        ship = Ship(self.stage)
        self.stage.addSprite(ship)
        ship.position.x = self.stage.width - (lifeNumber * ship.boundingRect.width) - 10
        ship.position.y = 0 + ship.boundingRect.height
        self.livesList.append(ship)

    def createRocks(self, numRocks):
        for _ in range(0, numRocks):
            position = Vector2d(random.randrange(-10, 10),
                                random.randrange(-10, 10))
            newRock = Rock(self.stage, position, Rock.largeRockType)
            self.stage.addSprite(newRock)
            self.rockList.append(newRock)

    def playGame(self):
        clock = pygame.time.Clock()

        frameCount = 0.0
        timePassed = 0.0
        self.fps = 0.0
        # Main loop
        while True:

            # calculate fps
            timePassed += clock.tick(60)
            frameCount += 1
            if frameCount % 10 == 0:  # every 10 frames
                self.fps = round((frameCount / (timePassed / 1000.0)))
                timePassed = 0
                frameCount = 0

            self.secondsCount += 1

            self.input(pygame.event.get())

            # pause
            if self.paused and not self.frameAdvance:
                self.stage.displayPaused()
                continue

            self.stage.screen.fill((10, 10, 10))
            self.stage.moveSprites()
            self.stage.drawSprites()
            self.doSaucerLogic()
            self.stage.displayScore(self.score)
            if self.showingFPS:
                self.stage.displayFps()  # for debug
            self.checkScore()

            # Process keys and game states
            if self.gameState == 'playing':
                self.playing()
            elif self.gameState == 'exploding':
                self.exploding()
            elif self.gameState == 'win':
                self.stage.displayWinScreen()
            else:
                self.stage.displayText()

            pygame.display.flip()

    def step(self, action):
        # self.input(action)

        # self.stage.screen.fill((10, 10, 10))
        self.stage.moveSprites()
        # self.stage.drawSprites()
        self.doSaucerLogic()
        self.stage.displayScore(self.score)
        # if self.showingFPS:
        #     self.displayFps()  # for debug
        self.checkScore()

        # Process keys and game states
        if self.gameState == 'playing':
            self.agent_playing(action)
        elif self.gameState == 'exploding':
            self.exploding()
        elif self.gameState == 'win':
            self.stage.displayWinScreen()
        else:
            self.stage.displayText()

        rockState = {}
        for index, rock in enumerate(self.rockList):
            rockState[index] = {
                'position': rock.getPos(), # Vector(x,y)
                'heading': rock.getHeading() # Vector(x,y)
            }

        alienState = None
        if self.saucer:
            alienState = self.saucer.getPos()

        self.current_state = {
            'alien': alienState, # None or Vector(x,y)
            'ship': {
                'position': self.ship.getPos(), # Vector(x,y)
                'heading': self.ship.getHeading(), # Vector(x,y)
            }, # the whole Ship object
            'rocks': rockState
        }

        done = False
        if self.lives == 0 and self.gameState == 'exploding':
            done = True

        return self.current_state, 0, done

    def agent_playing(self, action):
        if self.lives == 0:
            self.gameState = 'attract_mode'
        else:
            self.processAgentKeys(action)
            self.checkCollisions()
            # Level up when all rocks clear.
            if len(self.rockList) == 0:
                self.levelUp()

    def playing(self):
        if self.lives == 0:
            self.gameState = 'attract_mode'
        else:
            self.processKeys()
            self.checkCollisions()
            # Level up when all rocks clear.
            if len(self.rockList) == 0:
                self.levelUp()

    def doSaucerLogic(self):
        if self.saucer is not None:
            if self.saucer.laps >= 2:
                self.killSaucer()

        # Create a saucer
        if self.secondsCount % 2000 == 0 and self.saucer is None:
            randVal = random.randrange(0, 10)
            if randVal <= 3:
                self.saucer = Saucer(self.stage, Saucer.smallSaucerType, self.ship)
            else:
                self.saucer = Saucer(self.stage, Saucer.largeSaucerType, self.ship)
            self.stage.addSprite(self.saucer)

    def exploding(self):
        self.explodingCount += 1
        if self.explodingCount > self.explodingTtl:
            self.gameState = 'playing'
            [self.stage.spriteList.remove(debris) for debris in self.ship.shipDebrisList]
            self.ship.shipDebrisList = []

            if self.lives == 0:
                self.ship.visible = False
            else:
                self.createNewShip()

    def levelUp(self):
        if self.level == 1:
            self.level = 2
            self.numRocks = 2
            self.createRocks(self.numRocks)
        elif self.level == 2:
            self.level = 3
            self.numRocks = 3
            self.createRocks(self.numRocks)
        elif self.level == 3:
            # Win after level 3
            self.gameState = 'win'

    def input(self, events):
        self.frameAdvance = False
        for event in events:
            if event.type == QUIT:
                sys.exit(0)
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    sys.exit(0)
                if self.gameState == 'playing':
                    if event.key == K_SPACE:
                        self.ship.fireBullet()
                    elif event.key == K_b:
                        self.ship.fireBullet()
                    elif event.key == K_h:
                        self.ship.enterHyperSpace()
                elif self.gameState == 'attract_mode':
                    if event.key == K_RETURN:
                        self.initialiseGame()

                if event.key == K_p:
                    self.paused = not self.paused

                if event.key == K_j:
                    self.showingFPS = not self.showingFPS

                if event.key == K_f:
                    pygame.display.toggle_fullscreen()
            elif event.type == KEYUP:
                if event.key == K_o:
                    self.frameAdvance = True

    def processAgentKeys(self, action):
        key = pygame.key.get_pressed()

        if action == 'left':
            self.ship.rotateLeft()
        elif action == 'right':
            self.ship.rotateRight()

        if action == 'up':
            self.ship.increaseThrust()
            self.ship.thrustJet.accelerating = True
        else:
            self.ship.thrustJet.accelerating = False

        if action == 'fire':
            self.ship.fireBullet()
        if action == 'hyperspace':
            self.ship.enterHyperSpace()

    def processKeys(self):
        key = pygame.key.get_pressed()

        if key[K_LEFT] or key[K_z]:
            self.ship.rotateLeft()
        elif key[K_RIGHT] or key[K_x]:
            self.ship.rotateRight()

        if key[K_UP] or key[K_n]:
            self.ship.increaseThrust()
            self.ship.thrustJet.accelerating = True
        else:
            self.ship.thrustJet.accelerating = False

    def checkCollisions(self):

        # Ship bullet hit rock?
        newRocks = []
        shipHit, saucerHit = False, False

        # Rocks
        for rock in self.rockList:
            rockHit = False

            if not self.ship.inHyperSpace and rock.collidesWith(self.ship):
                p = rock.checkPolygonCollision(self.ship)
                if p is not None:
                    shipHit = True
                    rockHit = True

            if self.saucer is not None:
                if rock.collidesWith(self.saucer):
                    saucerHit = True
                    rockHit = True

                if self.saucer.bulletCollision(rock):
                    rockHit = True

                if self.ship.bulletCollision(self.saucer):
                    saucerHit = True
                    self.score += self.saucer.scoreValue

            if self.ship.bulletCollision(rock):
                rockHit = True

            if rockHit:
                self.rockList.remove(rock)
                self.stage.spriteList.remove(rock)

                if rock.rockType == Rock.largeRockType:
                    playSound("explode1")
                    newRockType = Rock.mediumRockType
                    self.score += 50
                elif rock.rockType == Rock.mediumRockType:
                    playSound("explode2")
                    newRockType = Rock.smallRockType
                    self.score += 100
                else:
                    playSound("explode3")
                    self.score += 200

                if rock.rockType != Rock.smallRockType:
                    for _ in range(0, 2):
                        position = Vector2d(rock.position.x, rock.position.y)
                        newRock = Rock(self.stage, position, newRockType)
                        self.stage.addSprite(newRock)
                        self.rockList.append(newRock)

                self.createDebris(rock)

        # Saucer bullets
        if self.saucer is not None:
            if not self.ship.inHyperSpace:
                if self.saucer.bulletCollision(self.ship):
                    shipHit = True

                if self.saucer.collidesWith(self.ship):
                    shipHit = True
                    saucerHit = True

            if saucerHit:
                self.createDebris(self.saucer)
                self.killSaucer()

        if shipHit:
            self.killShip()

    def killShip(self):
        stopSound("thrust")
        playSound("explode2")
        self.explodingCount = 0
        self.lives -= 1
        if self.livesList:
            ship = self.livesList.pop()
            self.stage.removeSprite(ship)

        self.stage.removeSprite(self.ship)
        self.stage.removeSprite(self.ship.thrustJet)
        self.gameState = 'exploding'
        self.ship.explode()

    def killSaucer(self):
        stopSound("lsaucer")
        stopSound("ssaucer")
        playSound("explode2")
        self.stage.removeSprite(self.saucer)
        self.saucer = None

    def createDebris(self, sprite):
        for _ in range(0, 25):
            position = Vector2d(sprite.position.x, sprite.position.y)
            debris = Debris(position, self.stage)
            self.stage.addSprite(debris)



    def checkScore(self):
        if self.score > 0 and self.score > self.nextLife:
            playSound("extralife")
            self.nextLife += 10000
            self.addLife(self.lives)

    # def step(self, action):
    #     """Performs one step in the environment"""
    #     observation = self.current_state()
    #     reward = 0
    #     done = False
    #     if self.lives == 0 and self.gameState == 'exploding':
    #         done = True

    #     return observation, reward, done




# Script to run the game
if not pygame.font:
    print('Warning, fonts disabled')
if not pygame.mixer:
    print('Warning, sound disabled')

# initSoundManager()
# game = Asteroids()  # create object game from class Asteroids
# game.playGame()

####
