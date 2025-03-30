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

    def displaySword(self):
        newSword = Sword(self, self.position, self.heading, self.ttl, self.velocity, self.stage)
        if (self.currentWeapon == "Sword"):
            self.stage.addSprite(newSword)
        else:
            self.stage.removeSprite(newSword)
        
    
    def swingSword(self, heading, ttl, velocity):
        self.position = Vector2d(self.position.x, self.position.y)
        self.stage.addSprite(newSword)

    def swordCollision(self, target):
        collisionDetected = False
        sword = Sword(self, self.position, self.ship, self.heading, self.ttl, self.stage)
        if sword.ttl > 0 and target.collidesWith(sword):
            collisionDetected = True
            sword.ttl = 0
        return collisionDetected 

# Bullet class


class Bullet(Point):

    def __init__(self, position, heading, shooter, ttl, velocity, stage):
        Point.__init__(self, position, heading, stage)
        self.shooter = shooter
        self.ttl = ttl
        self.velocity = velocity

    def move(self):
        Point.move(self)
        if (self.ttl <= 0):
            self.shooter.bullets.remove(self)

# Laser class
class Laser(Point):

    def __init__(self, position, heading, shooter, ttl, angle, stage):
        Point.__init__(self, position, heading, stage)
        self.shooter = shooter
        self.ttl = ttl
        self.pointlist = [(0, 0), (-1, -350), (1, -350)]
        self.angle = angle
        self.turnAngle = 6
    
    def move(self):
        Point.move(self)
        if (self.ttl <= 0):
            self.shooter.lasers.remove(self)
    
    def rotateLeft(self):
        self.angle += self.turnAngle

    def rotateRight(self):
        self.angle -= self.turnAngle


#Sword class
class Sword(Point):
    
    def __init__(self, position, heading, ttl, velocity, stage):
        Point.__init__(self, position, heading, stage)
        self.position = position
        self.ttl = ttl
        self.velocity = velocity
        self.pointlist = [(3, 10), (60, 100), (10, 25), (40, -5)]

    def move(self):
        Point.move(self)

    

        
        
