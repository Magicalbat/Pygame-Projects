import pygame
from pygame.math import Vector2

import math

from src.entities.entity import Entity
from src.utils.particles import Particles
from src.utils.animation import Animation
from src.utils.text import Text
from src.utils.common import loadSpriteSheet

from src.audiosettings import AudioSettings

class Player(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)

        if "text" in kwargs:
            self.text = kwargs["text"]
        else:
            self.text = Text()
            self.text.loadFontImg("res/imgs/text.png")
        self.textQueue = []
        self.textTimer = 0
        self.currentText = None

        if "images" in kwargs:
            self.imgs = kwargs["images"]
        else:
            self.imgs = loadSpriteSheet("res/imgs/player.png", (16,16), (4,3), (1,1), 12, (0,0,0))
        self.idleAnim = Animation((0,4), 6, realTime=True)
        self.runAnim = Animation((4,8), 10, realTime=True)

        self.jumpSound = pygame.mixer.Sound("res/sound/jump.wav")
        self.kickSound = pygame.mixer.Sound("res/sound/kick.wav")
        self.kickSound.set_volume(2)

        self.jumpPressTimer = 0

        self.speed = 16*5
        self.accel = 8
        self.airFriction = 0.93
        self.groundFriction = 0.85

        self.applyGravity, self.applyCollision = True, True

        maxJumpHeight = 3.35 * 16
        minJumpHeight = 0.5 * 16

        self.maxJumpVel = -math.sqrt(2 * self.gravity * maxJumpHeight)
        self.minJumpVel = -math.sqrt(2 * self.gravity * minJumpHeight)

        self.waterParticles = Particles((2,4), (-.1,.1,-.1,.1), circle=True, speed=4, accel=Vector2(0, self.gravity), collision=True, colors=[
            (0,0,255), (0,0,225), (0,0,200),
            (0,245,255), (0,128,255), (0,225,225),
        ])

        self.hasAcid = False 
        self.hasKick = False

        self.dir = 1
        self.holdingDown = False

        self.acid = False
        self.kickTimer = 0
        self.horizontalKicking = False
        self.kickDir = 1
        self.kickedEnemyTimer = 0
        
        self.invincible = False

        self.kickPower = Vector2(350, 250)
    
    def displayText(self, text, time=3):
        if (text, time) not in self.textQueue:
            self.textQueue.append((text, time))

    def addPickup(self, pickup):
        if pickup == "Acid":
            self.hasAcid = True
            self.displayText("Press A to toggle between water and acid")
            self.displayText("Acid can deal damage to enemies", 8)
        elif pickup == "Kick":
            self.hasKick = True
            self.displayText("Press Z to kick")
            self.displayText("Hold DOWN and Z to kick off of the ground", 6)
            self.displayText("You can kick enemies away", 6)
            self.displayText("You can also kick off the wall and frozen enemies", 6)

    def toggleAcid(self):
        if self.hasAcid:
            if self.acid:
                self.acid = False
                self.waterParticles.clear()
                self.waterParticles.colors = [
                    (0,0,255), (0,0,225), (0,0,200),
                    (0,245,255), (0,128,255), (0,225,225),
                ]
            else:
                self.acid = True
                self.waterParticles.clear()
                self.waterParticles.colors = [
                    (0,255,0), (0,225,0), (0,220,100)
                ]

    def draw(self, win, scroll):
        drawIndex = int(self.idleAnim.value)
        if abs(self.vel.x) > 25:    drawIndex = int(self.runAnim.value)
        if self.vel.y < 0:    drawIndex = 8
        elif self.vel.y > 0:    drawIndex = 9
        if (self.kickTimer > 0 and not self.holdingDown) or self.horizontalKicking or self.kickedEnemyTimer > 0:
            drawIndex = 10
            if self.kickTimer > 0 and not self.holdingDown:  self.kickDir = self.dir
            win.blit(pygame.transform.flip(self.imgs[drawIndex], self.kickDir == -1, False), self.pos-scroll-(2, 0))
        else:
            win.blit(pygame.transform.flip(self.imgs[drawIndex], self.dir == -1, False), self.pos-scroll-(2, 0))

        self.waterParticles.draw(win, scroll)

        if self.currentText != None:
            x = self.pos.x + self.width * 0.5 - scroll.x - self.currentText.get_width() * 0.5
            x = min(max(x, 0), win.get_width()-self.currentText.get_width())
            win.blit(self.currentText, (x, self.pos.y - scroll.y - 2 * self.currentText.get_height()))

        if self.hasAcid:
            col = (0,255,0) if self.acid else (0,0,255)
            pygame.draw.rect(win, col, (2,2,10,10))

        # Draw kick hitbox
        #if self.kickTimer > 0:
        #    keys = pygame.key.get_pressed()
        #    if keys[pygame.K_DOWN]:
        #        r = pygame.Rect(self.pos.x, self.pos.y + self.height, self.width, self.height/2)
        #    else:
        #        r = pygame.Rect(self.pos.x + self.width*self.dir, self.pos.y, self.width, self.height)
        #    pygame.draw.rect(win, (255,255,0), (r.x-scroll.x, r.y-scroll.y, r.w, r.h), 1)

    def update(self, delta, tilemap=None, enemyManager=None, colRects=None):
        self.waterParticles.update(delta, tilemap)

        self.idleAnim.update(delta)
        self.runAnim.update(delta)

        if self.textTimer <= 0:
            if len(self.textQueue) > 0:
                item = self.textQueue.pop(0)
                self.currentText = self.text.createTextSurf(item[0])
                self.textTimer = item[1]
            elif self.currentText is not None:
                self.currentText = None
        else:
            self.textTimer -= delta
        
        if self.jumpPressTimer > 0:
            if self.collisionDir & 0b0010 > 0:
                if AudioSettings().sfx:
                    self.jumpSound.play()
                self.vel.y = self.maxJumpVel
            self.jumpPressTimer -= delta
        
        keys = pygame.key.get_pressed()

        if self.collisionDir & 0b0010 > 0:
            self.vel.x *= self.groundFriction
        else:
            self.vel.x *= self.airFriction

        if keys[pygame.K_LEFT]:
            self.vel.x -= self.accel 
            if not self.horizontalKicking:
                self.vel.x = max(self.vel.x, -self.speed)
            self.dir = -1
        if keys[pygame.K_RIGHT]:
            self.vel.x += self.accel 
            if not self.horizontalKicking:
                self.vel.x = min(self.vel.x, self.speed)
            self.dir = 1
        if self.horizontalKicking:
            if self.collisionDir & 0b0010 > 0 or abs(self.vel.x) < 100:
                self.horizontalKicking = False
                
        if self.kickTimer > 0:
            self.kickTimer -= delta
            self.holdingDown = keys[pygame.K_DOWN]# and (self.collisionDir & 0b0010 > 0 or (not keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]))
            if self.holdingDown:
                r = pygame.Rect(self.pos.x, self.pos.y + self.height, self.width, self.height/2)
                if r.collidelist(tilemap.getRectColRects(r)) != -1 or r.collidelist(colRects) != -1:
                    self.vel.y = -self.kickPower.y
                    self.kickTimer = 0
                    if AudioSettings().sfx:
                        self.kickSound.play()
            else:
                r = pygame.Rect(self.pos.x + self.width*self.dir, self.pos.y, self.width, self.height)
                if r.collidelist(tilemap.getRectColRects(r)) != -1 or r.collidelist(colRects) != -1:
                    self.vel.x = self.kickPower.x * -self.dir
                    self.kickTimer = 0
                    self.horizontalKicking = True
                    self.kickDir = self.dir
                    if AudioSettings().sfx:
                        self.kickSound.play()
                for enemy in enemyManager.enemies:
                    if r.colliderect(enemy.rect):
                        enemy.kick(self.kickPower.x * self.dir)
                        self.kickTimer = 0
                        self.kickedEnemyTimer = 0.2
                        self.kickDir = self.dir
                        if AudioSettings().sfx:
                            self.kickSound.play()
        if self.kickedEnemyTimer > 0:    self.kickedEnemyTimer -= delta

        if keys[pygame.K_x]:
            if self.dir < 0:
                self.waterParticles.emit(self.rect.midleft, 1, (self.vel.x, -200+self.vel.x, -10, -90))
            else:
                self.waterParticles.emit(self.rect.midright, 1, (self.vel.x, 200+self.vel.x, -10, -90))

        super().update(delta, tilemap, colRects)

    def keydown(self, event):
        if event.key == pygame.K_c:
            self.jumpPressTimer = 0.1

        if self.hasKick and event.key == pygame.K_z:# and self.collisionDir & 0b0010 <= 0:
            self.kickTimer = 0.2
        
        if event.key == pygame.K_a:
            self.toggleAcid()

    def keyup(self, event):
        if event.key == pygame.K_c:
            if self.vel.y < self.minJumpVel:
                self.vel.y = self.minJumpVel