import pygame

import math, copy

from engine.entity import Entity
from engine.animation import Animation
from engine.common import *

from game.audiosettings import AudioSettings

class Player(Entity):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, (255,165,0))

        self.startPos = copy.deepcopy(self.pos)

        self.imgs = loadSpriteSheet("data/images/characters/pumpkin.png", (14,14), (4,2), (1,1), 8, (0,0,0))
        self.imgGroundCycleAnim = Animation([0,4], 8, realTime=True)
        self.groundEyeFrames = [0,1,1,0]
        self.imgJumpCycleAnim = Animation([0,2], 4, realTime=True)
        self.flipped = False

        self.maxSpeed = 12 * 5.5
        self.accel = 12
        self.friction = 14

        self.jumpPressTimer = 0
        self.groundTimer = 0

        maxJumpHeight = 3.35 * 12
        minJumpHeight = 0.5 * 12
        jumpDur = 0.5

        self.gravity = 2 * maxJumpHeight / jumpDur ** 2
        self.maxJumpVel = -math.sqrt(2 * self.gravity * maxJumpHeight)
        self.minJumpVel = -math.sqrt(2 * self.gravity * minJumpHeight)

        self.jumpSound = pygame.mixer.Sound("data/sounds/jump.wav")
        self.jumpSound.set_volume(0.35)

        self.applyGravity = True
        self.handleCollision = True
        self.applyVelocity = True
    
    def draw(self, win, scroll=(0,0)):
        if self.collisionTypes['bottom'] or self.velocity.y == 0:
            win.blit(pygame.transform.flip(self.imgs[0 + int(self.imgGroundCycleAnim.value)], self.flipped, False), (self.rect.x - scroll[0] - 1, self.rect.y - scroll[1] - 2))
            win.blit(pygame.transform.flip(self.imgs[6 + self.groundEyeFrames[int(self.imgGroundCycleAnim.value)]], self.flipped, False), (self.rect.x - scroll[0] - 1, self.rect.y - scroll[1] - 2))
        else:
            win.blit(pygame.transform.flip(self.imgs[4 + int(self.imgJumpCycleAnim.value)], self.flipped, False), (self.rect.x - scroll[0] - 1, self.rect.y - scroll[1] - 2))
            win.blit(pygame.transform.flip(self.imgs[6], self.flipped, False), (self.rect.x - scroll[0] - 1, self.rect.y - scroll[1] - 2))
        #pygame.draw.rect(win, (255,0,0), self.rect, width=1)
        #super().drawRect(win, scroll)
    
    def update(self, delta, inp, collisionRects=None, chunks=None):

        accelerating = False

        rightPressed = inp.keyDown(pygame.K_RIGHT)
        leftPressed = inp.keyDown(pygame.K_LEFT)

        if rightPressed:
            self.velocity.x += self.accel
            self.velocity.x = min(self.velocity.x, self.maxSpeed)
            accelerating = True

            if not leftPressed:
                self.flipped = False
        if leftPressed:
            self.velocity.x -= self.accel
            self.velocity.x = max(self.velocity.x, -self.maxSpeed)
            accelerating = True

            if not rightPressed:
                self.flipped = True
        
        moveDir = 0
        if self.velocity.x:
            moveDir = self.velocity.x / abs(self.velocity.x)

        if not accelerating:
            self.velocity.x -= self.friction * moveDir
            if moveDir == 1:
                self.velocity.x = max(self.velocity.x, 0)
            else:
                self.velocity.x = min(self.velocity.x, 0)

        super().update(delta, collisionRects, chunks)

        if self.collisionTypes['bottom']:
            self.imgGroundCycleAnim.update(delta)

            if self.velocity.x == 0:
                self.imgGroundCycleAnim.speed = 6
            else:
                self.imgGroundCycleAnim.speed = 12 * (abs(self.velocity.x) / self.maxSpeed)
        elif self.velocity.y != 0:
            self.imgJumpCycleAnim.update(delta)

            if self.velocity.x == 0:
                self.imgJumpCycleAnim.speed = 2
            else:
                self.imgJumpCycleAnim.speed = 6 * (abs(self.velocity.x) / self.maxSpeed)

        self.jumpPressTimer -= delta
        self.groundTimer -= delta

        if self.collisionTypes['bottom']:
            self.groundTimer = 0.1
        
        if inp.keyJustPressed(pygame.K_UP) or inp.keyJustPressed(pygame.K_c):
            self.jumpPressTimer = 0.05

        if self.groundTimer > 0 and self.jumpPressTimer > 0:
            self.velocity.y = self.maxJumpVel
            self.groundTimer = 0
            self.jumpPressTimer = 0

            if AudioSettings().sfx:
                self.jumpSound.play()
        
        if (inp.keyJustReleased(pygame.K_UP) or inp.keyJustReleased(pygame.K_c)) and self.velocity.y < self.minJumpVel:
            self.velocity.y = self.minJumpVel
        
        self.velocity.y = min(self.velocity.y, self.gravity * 0.75)
    
    def reset(self):
        self.pos = copy.deepcopy(self.startPos)
        self.rect.x = round(self.pos.x)
        self.rect.y = round(self.pos.y)
        self.velocity.x = 0
        self.velocity.y = 0