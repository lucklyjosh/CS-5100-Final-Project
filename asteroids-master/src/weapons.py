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
        self.stage = stage
        self.weapons = ["Shooter", "Sword"]
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

    def displaySword(self, ship):
        newSword = Sword(position, ship, heading, ttl, velocity, stage)
        self.stage.addSprite(newSword)
    
    def swingSword(self, heading, ttl, velocity):
        self.position = Vector2d(self.position.x, self.position.y)

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

class Sword(Point):
    
    def __init__(self, position, ship, heading, ttl, velocity, stage):
        Point.__init__(self, position, heading, stage)
        self.position = position
        self.ship = ship
        self.ttl = ttl
        self.velocity = velocity

    def move(self):
        Point.move(self)

    

        
        
