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

import random
from util.vectorsprites import *
from util import *
from soundManager import *
import pygame

class Weapon(VectorSprite):

    def __init__(self, position, heading, pointlist, stage, weapons, currentWeapon):
        VectorSprite.__init__(self, position, heading, pointlist)
        self.bullets = []
        self.lasers = []
        self.stage = stage
        self.weapons = ["Shooter", "Laser", "Sword"]
        self.currentWeapon = weapons[0]

    def fireBullet(self, heading, ttl, velocity):
        if (len(self.bullets) < self.maxBullets):
            position = Vector2d(self.position.x, self.position.y)
            newBullet = Bullet(position, heading, self,
                            ttl, velocity, self.stage)
            self.bullets.append(newBullet)
            self.stage.addSprite(newBullet)
            return True

    def bulletCollision(self, target):
        collisionDetected = False
        for bullet in self.bullets:
            if bullet.ttl > 0 and target.collidesWith(bullet):
                collisionDetected = True
                bullet.ttl = 0
        return collisionDetected
    
    def fireLaser(self, heading, ttl):
        if (len(self.lasers) < self.maxLasers):
            position = Vector2d(self.position.x, self.position.y)
            newLaser = Laser(position, heading, self, ttl, self.angle, self.stage)
            self.lasers.append(newLaser)
            self.stage.addSprite(newLaser)
            return True
    
    def laserCollision(self, target):
        collisionDetected = False
        for laser in self.lasers:
            if laser.ttl > 0 and target.collidesWith(laser):
                collisionDetected = True
                laser.ttl = 0
        return collisionDetected

    def swordCollision(self, sword, target):
        if sword.useSword == False:
            return False
        else:
            return target.collidesWith(sword)

# Bullet class


class Bullet(Point):

    def __init__(self, position, heading, weapon, ttl, velocity, stage):
        Point.__init__(self, position, heading, stage)
        self.weapon = weapon
        self.ttl = ttl
        self.velocity = velocity

    def move(self):
        Point.move(self)
        if (self.ttl <= 0):
            self.weapon.bullets.remove(self)

# Laser class
class Laser(Point):

    def __init__(self, position, heading, weapon, ttl, angle, stage):
        Point.__init__(self, position, heading, stage)
        self.weapon = weapon
        self.ttl = ttl
        self.angle = angle
        self.turnAngle = 6
        self.pointlist = [(0, 0), (-1, -400), (1, -400)]
    
    def move(self):
        Point.move(self)
        if (self.ttl <= 0):
            self.weapon.lasers.remove(self)
            stopSound("laser")
    
    def rotateLeft(self):
        self.angle += self.turnAngle

    def rotateRight(self):
        self.angle -= self.turnAngle


#Sword class
class Sword(VectorSprite):
    
    def __init__(self, stage, ship):
        position = Vector2d(stage.width/2, stage.height/2)
        heading = Vector2d(0, 0)
        self.pointlist = [(0, -10), (-3, -30), (-7, -30), (-3, -40), 
                          (0, -80), (3, -40), (7, -30), (3, -30)]
        self.ship = ship
        self.useSword = False
        VectorSprite.__init__(self, position, heading, self.pointlist)

    
    def draw(self):
        if self.useSword and self.ship.inHyperSpace == False:
            self.color = (255, 255, 255)
        else:
            self.color = (10, 10, 10)

        VectorSprite.draw(self)
        return self.transformedPointlist

