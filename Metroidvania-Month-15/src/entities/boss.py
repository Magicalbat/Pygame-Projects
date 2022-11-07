import pygame
from pygame.math import Vector2

import random

from src.entities.entity import Entity
from src.entities.projectile import Projectile
from src.utils.animation import Animation

class Boss(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)

        self.spawnX = self.pos.x

        self.applyGravity, self.applyCollision = True, True

        self.speed = 16 * 3.5
        self.dir = -1

        self.vel.x = self.speed * self.dir

        self.imgs = kwargs["images"]
        self.anim = Animation([1, 3], 4, realTime=True)

        self.phase = 0
        self.healths = [5, 10, 20]
        self.health = self.healths[self.phase]
        self.damageTimer = 0

        self.invincible = False

        self.shootRate = 0.5
        self.shootTimer = self.shootRate
        self.projectiles = []

        self.enemySpawnTimer = 5
        self.spawnEnemy = False
        self.enemySpawnType = "GroundEnemies"
        self.enemySpawnPos = (0, 0)
        self.enemySpawnDir = 1

        self.damageSurf = pygame.Surface((self.width + 2, self.height + 2)).convert()
        self.damageSurf.fill((255,0,0))
        self.damageSurf.set_alpha(128)
    
    def collide(self, other : pygame.Rect):
        for proj in self.projectiles:
            if other.collidepoint(proj.pos):    return True
        return self.rect.colliderect(other)
    
    # Return whether or not it is alive
    def damage(self, amt):
        if not self.invincible:
            if self.damageTimer <= 0:
                self.health -= amt
                self.damageTimer = 0.5
            if self.health <= 0:
                self.phase += 1
                if self.phase >= len(self.healths): return False
                self.health = self.healths[self.phase]
                self.invincible = True

                self.shootRate += 1

                self.speed *= 0.67

                self.pos.x = self.spawnX
                self.pos.y -= self.height
                self.width *= 2
                self.height *= 2
                self.updateRect()

                self.damageSurf = pygame.Surface((self.damageSurf.get_width() * 2, self.damageSurf.get_height() * 2))
                self.damageSurf.fill((255,0,0))
                self.damageSurf.set_alpha(128)
        return True
    
    def draw(self, win, scroll):
        if self.phase == 0:
            if self.health != self.healths[self.phase]:
                r = pygame.Rect(self.pos.x - scroll.x, self.pos.y - self.height/2 - scroll.y, self.width, self.height/4)
            else:
                r = pygame.Rect(0, 0, 0, 0)
        else:
            r = pygame.Rect(40, 2, 240, 5)
        pygame.draw.rect(win, (255,0,0), r)
        pygame.draw.rect(win, (0,255,0), (r.x, r.y, r.w * (self.health/self.healths[self.phase]), r.h))
        drawIndex = int(self.anim.value)
        if self.collisionDir & 0b0010 == 0: drawIndex = 0

        scale = 2**self.phase
        win.blit(pygame.transform.scale(pygame.transform.flip(self.imgs[drawIndex], self.dir == -1, False), (16*scale, 16*scale)), self.pos-scroll+(-2*scale, 0))

        if self.damageTimer > 0.25:
            self.damageSurf.fill((255,0,0))
            win.blit(self.damageSurf, self.pos-scroll+(-scale, -scale))
        elif self.damageTimer > 0:
            self.damageSurf.fill((255,255,255))
            win.blit(self.damageSurf, self.pos-scroll+(-scale, -scale))

        for proj in self.projectiles:
            proj.draw(win, scroll)
        #super().draw(win, scroll)
    
    def update(self, delta, tilemap, player, colRects=None):
        self.anim.update(delta)
        self.damageTimer -= delta
        if self.phase == 0:
            if self.collisionDir & 0b0100 > 0 or self.collisionDir & 0b0001 > 0:
                self.dir *= -1
                self.vel.x = self.speed * self.dir
        else:
            if abs(self.pos.x - self.spawnX) > 100 + 75 * (self.phase-1):
                self.dir *= -1
                self.vel.x = self.speed * self.dir
                self.pos.x += self.vel.x * delta * 2
                self.updateRectPos()

            for i in range(len(self.projectiles))[::-1]:
                self.projectiles[i].update(delta)
                if tilemap.collidePoint(self.projectiles[i].pos):
                    self.projectiles.pop(i)

        self.vel.x = self.speed * self.dir

        if self.phase == 1 and self.center.distance_squared_to(player.center) < 62500: # Radius: 250
            if self.shootTimer <= 0:
                self.shootTimer = self.shootRate
                self.projectiles.append(Projectile(self.center, player.center, speed=16*5))
            else:
                self.shootTimer -= delta

        if self.phase == 2 and self.center.distance_squared_to(player.center) < 62500: # Radius: 250
            if self.enemySpawnTimer <= 0:
                self.enemySpawnTimer = 5
                self.spawnEnemy = True
                if random.random() > 0.75:  self.enemySpawnType = "GroundEnemies"
                else:   self.enemySpawnType = "SlowEnemies"
                self.enemySpawnPos = self.center
                self.enemySpawnDir = ((self.pos.x + self.width*0.5) < (player.pos.x + player.width*0.5)) * 2 - 1
            else:
                self.enemySpawnTimer -= delta
            
        super().update(delta, tilemap, colRects)