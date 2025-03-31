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
        self.createRocks(3)
        self.saucer = None
        self.secondsCount = 1
        self.score = 0
        self.ship = None
        self.lives = 0
        self.current_reward = 0
        self.reward_context = {
            'reward_close_to_rock': 10,
            'reward_too_close_no_fire': -50,
            'reward_hit_alien_slow': 500,
            'reward_hit_alien_fast': 1000,
            'reward_hit_large_rock': 100,
            'reward_hit_medium_rock': 300,
            'reward_hit_small_rock': 500,
            'reward_survive_frame': 1,
            'reward_do_nothing': 0,
            'reward_life_lost': -5000,
            'reward_level_cleared': 500
        }
        self.rocks_hit = 0
        self.levels_completed = 0
        self.numLevels = 3

    def add_reward(self, key):
        reward_value = self.reward_context.get(key, 0)
        self.current_reward += reward_value

    def initialiseGame(self):
        self.gameState = 'playing'
        [self.stage.removeSprite(sprite)
         for sprite in self.rockList]  # clear old rocks
        if self.saucer is not None:
            self.killSaucer()
        self.startLives = 5
        self.createNewShip()
        self.createLivesList()
        self.score = 0
        self.rockList: List[Rock] = []
        # Set level 1 
        self.level = 1
        self.numRocks = 3
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
            [self.stage.spriteList.remove(debris)
             for debris in self.ship.shipDebrisList]
        self.ship = Ship(self.stage)
        self.stage.addSprite(self.ship.thrustJet)
        self.stage.addSprite(self.ship)

    def createLivesList(self):
        self.lives += 1
        self.livesList = []
        for i in range(1, self.startLives):
            self.addLife(i)
        self.lives = self.startLives

    def addLife(self, lifeNumber):
        self.lives += 1
        ship = Ship(self.stage)
        self.stage.addSprite(ship)
        ship.position.x = self.stage.width - \
            (lifeNumber * ship.boundingRect.width) - 10
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
                # nearest integer
                self.fps = round((frameCount / (timePassed / 1000.0)))
                # reset counter
                timePassed = 0
                frameCount = 0

            self.secondsCount += 1
            if self.gameState == 'playing':
                print("Calling add_reward for staying alive.")
                self.add_reward('reward_survive_frame')


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

            # Process keys
            if self.gameState == 'playing':
                self.playing()
            elif self.gameState == 'exploding':
                self.exploding()
            elif self.gameState == 'win':
                self.stage.displayWinScreen()
                done = True
            else:
                self.stage.displayText()

            pygame.display.flip()

    def step(self, action):
        done = False

        self.stage.moveSprites()
        self.doSaucerLogic()
        self.stage.displayScore(self.score)
        self.checkScore()

        # Process keys and game states
        self.secondsCount += 1
        if self.gameState == 'playing':
            self.agent_playing(action)
            self.add_reward('reward_survive_frame')
        elif self.gameState == 'exploding':
            self.exploding()
            if self.lives == 0:
                done = True
        elif self.gameState == 'win':
            self.stage.displayWinScreen()
            done = True
        else:
            self.stage.displayText()


        min_distance = float('inf')

        # Find the nearest rock
        if self.rockList:
            min_distance = min([
                math.sqrt((rock.getPos().x - self.ship.getPos().x) ** 2 + (rock.getPos().y - self.ship.getPos().y) ** 2)
                for rock in self.rockList
            ])

        # Encourage moving closer to rocks for attacks
        if min_distance < 300:
            self.add_reward('reward_close_to_rock')
            # print(f"🟢 Approaching rock, Reward added. Distance: {min_distance:.2f}")

        # Penalize agent for reckless movement without shooting
        if min_distance < 50 and action != 'fire':
            self.add_reward('reward_too_close_no_fire')
            # print(f"🔴 Too close without firing! Penalty applied. Distance: {min_distance:.2f}")


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

        reward = self.current_reward
        self.current_reward = 0  # reset reward after each step
        
        return self.current_state, reward, done

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
                self.saucer = Saucer(
                    self.stage, Saucer.smallSaucerType, self.ship)
            else:
                self.saucer = Saucer(
                    self.stage, Saucer.largeSaucerType, self.ship)
            self.stage.addSprite(self.saucer)

    def exploding(self):
        self.explodingCount += 1
        if self.explodingCount > self.explodingTtl:
            self.gameState = 'playing'
            [self.stage.spriteList.remove(debris)
             for debris in self.ship.shipDebrisList]
            self.ship.shipDebrisList = []

            if self.lives == 0:
                self.ship.visible = False
            else:
                self.createNewShip()

    def levelUp(self):
        self.levels_completed += 1
        print(f"🚀 Level {self.levels_completed} completed! Moving to the next level.")
        if self.level < self.numLevels:
            self.level += 1
            self.numRocks += 1
            self.createRocks(self.numRocks)
        else:
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
                    # Start a new game
                    if event.key == K_RETURN:
                        self.initialiseGame()

                if event.key == K_p:
                    if self.paused:  # (is True)
                        self.paused = False
                    else:
                        self.paused = True

                if event.key == K_j:
                    if self.showingFPS:  # (is True)
                        self.showingFPS = False
                    else:
                        self.showingFPS = True

                if event.key == K_f:
                    pygame.display.toggle_fullscreen()

                # if event.key == K_k:
                    # self.killShip()
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
        pressed = False
        if key[K_LEFT] or key[K_z]:
            self.ship.rotateLeft()
            pressed = True
        elif key[K_RIGHT] or key[K_x]:
            self.ship.rotateRight()
            pressed = True

        if key[K_UP] or key[K_n]:
            self.ship.increaseThrust()
            self.ship.thrustJet.accelerating = True
            pressed = True
        else:
            self.ship.thrustJet.accelerating = False
            pressed = True
        if not pressed and self.gameState == 'playing':
            self.add_reward('reward_do_nothing')
    # Check for ship hitting the rocks etc.

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
                self.rocks_hit += 1
                # print(f"💥 Rock destroyed! Total rocks hit: {self.rocks_hit}")

                if rock.rockType == Rock.largeRockType:
                    playSound("explode1")
                    newRockType = Rock.mediumRockType
                    self.score += 50
                    if self.gameState == 'playing':
                        self.add_reward('reward_hit_large_rock')
                elif rock.rockType == Rock.mediumRockType:
                    playSound("explode2")
                    newRockType = Rock.smallRockType
                    self.score += 100
                    if self.gameState == 'playing':
                        self.add_reward('reward_hit_medium_rock')
                else:
                    playSound("explode3")
                    self.score += 200

                if rock.rockType != Rock.smallRockType:
                    # new rocks
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
            self.add_reward('reward_life_lost')
            # comment in to pause on collision
            #self.paused = True

    def killShip(self):
        stopSound("thrust")
        playSound("explode2")
        self.explodingCount = 0
        self.lives -= 1
        if (self.livesList):
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
        if self.saucer and self.saucer.saucerType == Saucer.smallSaucerType:
            self.add_reward('reward_hit_alien_fast')
        else:
            self.add_reward('reward_hit_alien_slow')

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


# Script to run the game
if not pygame.font:
    print('Warning, fonts disabled')
if not pygame.mixer:
    print('Warning, sound disabled')

# initSoundManager()
# game = Asteroids()  # create object game from class Asteroids
# game.playGame()

####