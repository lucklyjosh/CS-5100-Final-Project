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

import pygame
import sys
import os
from pygame.locals import *


class Stage:

    # Set up the PyGame surface
    def __init__(self, caption, dimensions=None):
        pygame.init()
        self.font = pygame.font.Font(None, 36)

        # If no screen size is provided pick the first available mode
        if dimensions == None:
            dimensions = pygame.display.list_modes()[0]

        # pygame.display.set_mode(dimensions, FULLSCREEN)
        # pygame.mouse.set_visible(False)

        # # pygame.display.set_mode(dimensions)

        # pygame.display.set_caption(caption)
        # self.screen = pygame.display.get_surface()
        self.screen = pygame.display.set_mode(dimensions)
        pygame.display.set_caption(caption)
        pygame.mouse.set_visible(False)

        self.spriteList = []
        self.width = dimensions[0]
        self.height = dimensions[1]
        self.showBoundingBoxes = False

    # Add sprite to list then draw it as a easy way to get the bounding rect
    def addSprite(self, sprite):
        self.spriteList.append(sprite)
        sprite.boundingRect = pygame.draw.aalines(
            self.screen, sprite.color, True, sprite.draw())

    def removeSprite(self, sprite):
        self.spriteList.remove(sprite)

    def drawSprites(self):
        for sprite in self.spriteList:
            sprite.boundingRect = pygame.draw.aalines(
                self.screen, sprite.color, True, sprite.draw())
            if self.showBoundingBoxes == True:
                pygame.draw.rect(self.screen, (255, 255, 255),
                                 sprite.boundingRect, 1)

    def moveSprites(self):
        for sprite in self.spriteList:
            sprite.move()

            if sprite.position.x < 0:
                sprite.position.x = self.width

            if sprite.position.x > self.width:
                sprite.position.x = 0

            if sprite.position.y < 0:
                sprite.position.y = self.height

            if sprite.position.y > self.height:
                sprite.position.y = 0
    
    def displayText(self):
        font1 = pygame.font.Font('../res/Hyperspace.otf', 50)
        font2 = pygame.font.Font('../res/Hyperspace.otf', 20)
        font3 = pygame.font.Font('../res/Hyperspace.otf', 30)

        titleText = font1.render('Asteroids', True, (180, 180, 180))
        titleTextRect = titleText.get_rect(centerx=self.width/2)
        titleTextRect.y = self.height/2 - titleTextRect.height*2
        self.screen.blit(titleText, titleTextRect)

        keysText = font2.render('(C) 1979 Atari INC.', True, (255, 255, 255))
        keysTextRect = keysText.get_rect(centerx=self.width/2)
        keysTextRect.y = self.height - keysTextRect.height - 20
        self.screen.blit(keysText, keysTextRect)

        instructionText = font3.render('Press start to Play', True, (200, 200, 200))
        instructionTextRect = instructionText.get_rect(centerx=self.width/2)
        instructionTextRect.y = self.height/2 - instructionTextRect.height
        self.screen.blit(instructionText, instructionTextRect)

    def displayWinScreen(self):
        # Display victory
        font = pygame.font.Font('../res/Hyperspace.otf', 50)
        winText = font.render("You WIN!!!", True, (255, 255, 0))
        winRect = winText.get_rect(center=(self.width / 2, self.height / 2))
        self.screen.fill((0, 0, 0))
        self.screen.blit(winText, winRect)
        pygame.display.flip()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        waiting = False
        pygame.quit()
        sys.exit()

    def displayPaused(self):
        if self.paused:
            font1 = pygame.font.Font('../res/Hyperspace.otf', 30)
            pausedText = font1.render("Paused", True, (255, 255, 255))
            textRect = pausedText.get_rect(centerx=self.width/2, centery=self.height/2)
            self.screen.blit(pausedText, textRect)
            pygame.display.update()

    def displayScore(self, score):
        font1 = pygame.font.Font('../res/Hyperspace.otf', 30)
        scoreStr = str("%02d" % score)
        scoreText = font1.render(scoreStr, True, (200, 200, 200))
        scoreTextRect = scoreText.get_rect(centerx=100, centery=45)
        self.screen.blit(scoreText, scoreTextRect)

    def displayFps(self):
        font2 = pygame.font.Font('../res/Hyperspace.otf', 15)
        fpsStr = str(self.fps)+(' FPS')
        scoreText = font2.render(fpsStr, True, (255, 255, 255))
        scoreTextRect = scoreText.get_rect(centerx=(self.width/2), centery=15)
        self.screen.blit(scoreText, scoreTextRect)
