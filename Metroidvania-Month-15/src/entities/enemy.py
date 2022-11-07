import pygame
from pygame.math import Vector2

import math
from enum import Enum

from src.entities.entity import Entity
from src.utils.common import lerp
from src.utils.animation import Animation

def enemy(cls):
    class EnemyWrapper(Entity):
        def __init__(self, *args, **kwargs):
            super().__init__(*args)
    
            self.applyGravity, self.applyCollision = True, True
            
            self.stunTimer = 0
            self.startStunTime = 0
            self.damageTimer = 0
            self.maxHealth = 5
            self.health = self.maxHealth

            self.kicked = False

            self.onScreen = False

            self.decoratorObj = cls(self, **kwargs)

            self.indicationSurf = pygame.Surface((self.width+2, self.height+2)).convert()
            self.indicationSurf.fill((0,245,255))
            self.indicationSurf.set_alpha(128)

            if hasattr(self.decoratorObj, "collide"):
                self.collide = self.childCollide
            else:
                self.collide = self.internalCollide 

        def internalCollide(self, rect):
            return self.rect.colliderect(rect)

        def childCollide(self, rect):
            return self.decoratorObj.collide(self.rect, rect)
    
        def stun(self, time):
            self.startStunTime = time
            self.stunTimer = time
            self.indicationSurf.fill((0,245,255))
        
        def kick(self, vel):
            self.stunTimer = 0
            self.kicked = True
            self.vel.x = vel

        # Return whether or not it is alive
        def damage(self, amt):
            if self.damageTimer <= 0:
                self.health -= amt
                self.damageTimer = 0.5
                
                self.indicationSurf.set_alpha(128)
            return self.health > 0
        
        def draw(self, win, scroll):
            if self.health != self.maxHealth:
                r = pygame.Rect(self.pos.x - scroll.x, self.pos.y - self.height/2 - scroll.y, self.width, self.height/4)
                pygame.draw.rect(win, (255,0,0), r)
                pygame.draw.rect(win, (0,255,0), (r.x, r.y, r.w * (self.health/self.maxHealth), r.h))
            self.decoratorObj.draw(win, self, scroll)

            if self.stunTimer > 0:
                self.indicationSurf.set_alpha(64 + 128 * (self.stunTimer / self.startStunTime))
                win.blit(self.indicationSurf, self.pos-scroll+(-1, -1))
            elif self.damageTimer > 0.25:
                self.indicationSurf.fill((255,0,0))
                win.blit(self.indicationSurf, self.pos-scroll+(-1, -1))
            elif self.damageTimer > 0:
                self.indicationSurf.fill((255,255,255))
                win.blit(self.indicationSurf, self.pos-scroll+(-1, -1))
        
        def update(self, delta, player, tilemap=None, colRects=None):
            if self.stunTimer <= 0:
                if self.kicked:
                    self.vel.x *= 0.9
                    if abs(self.vel.x) < 10: self.kicked = False
                else:
                    self.decoratorObj.update(delta, self, player, tilemap)
                super().update(delta, tilemap, colRects)
            else:
                self.stunTimer -= delta
                
            if self.damageTimer > 0:    self.damageTimer -= delta
    return EnemyWrapper

from src.entities.projectile import Projectile

@enemy
class FlyingEnemy:
    # No states, dumb enemy

    def __init__(self, enemy, **kwargs):
        enemy.applyGravity = False

        self.angle = 0
        self.shootRate = 1
        self.shootTimer = self.shootRate

        self.speed = 16 * 3

        self.projectiles = []

        self.imgs = kwargs["images"]
        self.anim = Animation([0,3], 4, realTime=True)
    
    def collide(self, r1, r2):
        for proj in self.projectiles:
            if r2.collidepoint(proj.pos):  return True
        return r1.colliderect(r2)
    
    def draw(self, win, enemy, scroll):
        if enemy.onScreen:
            drawIndex = int(self.anim.value)
            win.blit(self.imgs[drawIndex], enemy.pos-scroll+(-2,0))
            #pygame.draw.rect(win, (0,255,0), (enemy.pos.x - scroll.x, enemy.pos.y - scroll.y, enemy.width, enemy.height), 1)
        for proj in self.projectiles:
            proj.draw(win, scroll)
    
    def update(self, delta, enemy, player, tilemap):
        self.anim.update(delta)

        self.angle += 3 * delta
        self.angle = math.fmod(self.angle, math.tau)

        enemy.vel.x = math.sin(self.angle) * self.speed
        enemy.vel.y = math.cos(self.angle) * self.speed

        if enemy.onScreen and enemy.pos.distance_squared_to(player.pos) < 40000:
            if self.shootTimer <= 0:
                self.shootTimer = self.shootRate
                self.projectiles.append(Projectile(enemy.center, player.center))
            else:
                self.shootTimer -= delta

        for i in range(len(self.projectiles))[::-1]:
            self.projectiles[i].update(delta)
            if tilemap.collidePoint(self.projectiles[i].pos):
                self.projectiles.pop(i)

@enemy
class JumpingEnemy:
    class States(Enum):
        IDLE = 0
        ATTACK = 1

    def __init__(self, enemy, **kwargs):
        self.currentState = self.States.IDLE

        idleJumpHeight = 16 * 1.2
        attackJumpHeight = 16 * 3.2

        self.idleJumpVel = -math.sqrt(2 * enemy.gravity * idleJumpHeight)
        self.attackJumpVel = -math.sqrt(2 * enemy.gravity * attackJumpHeight)

        self.idleSpeed = 16 * 2
        self.attackSpeed = 16 * 5

        self.dir = -1

        self.imgs = kwargs["images"]

    def draw(self, win, enemy, scroll):
        if enemy.onScreen:
            #col = (0,255,0)
            #if self.currentState == self.States.ATTACK:    col = (255,0,0)
            drawIndex = 1
            if self.currentState == self.States.ATTACK: drawIndex = 0
            if enemy.vel.y < -50:  drawIndex = 2
            win.blit(self.imgs[drawIndex], enemy.pos-scroll+(-2, 0))
            #pygame.draw.rect(win, (0,255,0), pygame.Rect(enemy.pos - scroll, (enemy.width, enemy.height)), 1)

    def update(self, delta, enemy, player, tilemap):
        if enemy.collisionDir & 0b0010 > 0:
            if self.currentState == self.States.IDLE:
                self.dir *= -1
                enemy.vel.x = self.idleSpeed  * self.dir
                enemy.vel.y = self.idleJumpVel
            elif self.currentState == self.States.ATTACK:
                enemy.vel.x = self.attackSpeed  * self.dir
                enemy.vel.y = self.attackJumpVel

        if self.currentState == self.States.ATTACK:
            self.dir = ((enemy.pos.x + enemy.width*0.5) < (player.pos.x + player.width*0.5)) * 2 - 1
            if abs(player.pos.x - enemy.pos.x) < 10:
                if player.vel.length() < 0.1:    enemy.vel.x *= 0.9
                else:    enemy.vel.x *= 0.96

        # To attack
        if self.currentState != self.States.ATTACK and (enemy.damageTimer > 0 or enemy.center.distance_squared_to(player.center) < 2500): # radius - 50
            self.changeState(self.States.ATTACK, enemy)

        # Out of attack
        if self.currentState == self.States.ATTACK and enemy.center.distance_squared_to(player.center) > 10000: # radius - 100
            self.changeState(self.States.IDLE, enemy)

    def changeState(self, newState, enemy):
        self.currentState = newState

@enemy
class GroundEnemy:
    class States(Enum): 
        PATROL = 0
        ATTACK = 1
        SEARCH = 2
        
    def __init__(self, enemy, **kwargs):
        self.currentState = self.States.PATROL

        enemy.height, enemy.rect.h = 10, 10

        self.walkSpeed = 16 * 3
        self.runSpeed  = 16 * 4.5
        self.dir = 1
        self.searchTimer = 0

        self.imgs = kwargs["images"]
        self.anim = Animation([0,2], 4, realTime=True)

    def getCurrentSpeed(self):
        if self.currentState == self.States.PATROL:
            return self.walkSpeed
        return self.runSpeed
    
    def draw(self, win, enemy, scroll):
        if enemy.onScreen:
            #col = (0,255,0)
            #if self.currentState == self.States.ATTACK: col = (255,0,0)
            #if self.currentState == self.States.SEARCH: col = (0,0,255)
            drawIndex = int(self.anim.value)
            if self.currentState != self.States.PATROL:   drawIndex += 1
            win.blit(pygame.transform.flip(self.imgs[drawIndex], self.dir < 0, False), enemy.pos-scroll+(-2, -7))
            #pygame.draw.rect(win, (0, 255, 0), pygame.Rect(enemy.pos - scroll, (enemy.width, enemy.height)), 1)

    def update(self, delta, enemy, player, tilemap):
        if self.currentState == self.States.PATROL: self.anim.speed = 4
        else:   self.anim.speed = 8
        self.anim.update(delta)

        if self.currentState == self.States.PATROL:
            if enemy.collisionDir & 0b0100 > 0 or enemy.collisionDir & 0b0001 > 0:
                self.dir *= -1
            enemy.vel.x = self.walkSpeed * self.dir
        elif self.currentState == self.States.ATTACK:
            self.dir = lerp(self.dir, ((enemy.pos.x + enemy.width*0.5) < (player.pos.x + player.width*0.5)) * 2 - 1, 0.05)
            enemy.vel.x = self.runSpeed * self.dir

            if enemy.center.distance_squared_to(player.center) > 15625: # radius - 125
                self.changeState(self.States.SEARCH, enemy)
        elif self.currentState == self.States.SEARCH:
            enemy.vel.x = self.runSpeed * self.dir

            self.searchTimer -= delta
            if self.searchTimer < 0:
                self.changeState(self.States.PATROL, enemy)

        if self.currentState != self.States.ATTACK and (enemy.damageTimer > 0 or enemy.center.distance_squared_to(player.center) < 2500): # radius - 50
            self.changeState(self.States.ATTACK, enemy)

    def changeState(self, newState, enemy):
        enemy.vel.x = 0
        if newState != self.States.ATTACK:
            self.dir = (self.dir > 0) * 2 - 1
            self.searchTimer = 2

        self.currentState = newState

@enemy
class SlowEnemy:
    def __init__(self, enemy, **kwargs):
        self.speed = 16 * 3.5

        self.dir = 1

        enemy.vel.x = self.speed * self.dir

        self.imgs = kwargs["images"]
        self.anim = Animation([1,3], 4, realTime=True)
    
    def getCurrentSpeed(self):
        return self.speed

    def draw(self, win, enemy, scroll):
        drawIndex = int(self.anim.value)
        if enemy.collisionDir & 0b0010 == 0: drawIndex = 0
        win.blit(pygame.transform.flip(self.imgs[drawIndex], self.dir == -1, False), enemy.pos-scroll+(-2, 0))
        #pygame.draw.rect(win, (0,255,0), (enemy.pos - scroll, (enemy.width, enemy.height)), 1)

    def update(self, delta, enemy, player, tilemap):
        self.anim.update(delta)
        enemy.vel.x = self.speed * self.dir
        if enemy.collisionDir & 0b0100 > 0 or enemy.collisionDir & 0b0001 > 0:
            self.dir *= -1
            enemy.vel.x = self.speed * self.dir
            enemy.pos.x += enemy.vel.x * 2 * delta
            enemy.updateRectPos()