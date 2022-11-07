import pygame
from pygame.math import Vector2

from src.utils.common import loadSpriteSheet
import src.screens
from src.entities.boss import Boss
from src.entities.enemy import *

from src.audiosettings import AudioSettings

class EnemyManager:
    enemyTypes = {
        "GroundEnemies": GroundEnemy,
        "JumpingEnemies": JumpingEnemy,
        "FlyingEnemies": FlyingEnemy,
        "SlowEnemies": SlowEnemy
    }
    enemyImgs = {
        "GroundEnemies": (9, 12), 
        "JumpingEnemies": (6, 9),
        "FlyingEnemies": (3, 6),
        "SlowEnemies": (0, 3)
    }
    def __init__(self, extraData):
        self.enemySpawns = {}

        for enemyType in ["GroundEnemies", "JumpingEnemies", "FlyingEnemies", "SlowEnemies"]:
            if enemyType in extraData:
                self.enemySpawns[enemyType] = extraData[enemyType]
        
        if "Boss" in extraData and len(extraData["Boss"]) > 0:
            self.enemySpawns["Boss"] = extraData["Boss"][0]
        self.bossDamagePoints = []
        if "BossDamagePoints" in extraData:
            self.bossDamagePoints = extraData["BossDamagePoints"]
        
        self.imgs = loadSpriteSheet("res/imgs/enemies.png", (16,16), (3,4), (1,1), 12, (0,0,0))

        self.deathSound = pygame.mixer.Sound("res/sound/death.wav")
        self.rageSound = pygame.mixer.Sound("res/sound/rage.wav")

    def setup(self):
        self.reset = False
        
        self.boss = None
        self.enemies = []
        for enemyType, positions in self.enemySpawns.items():
            if enemyType != "Boss":
                for pos in positions:
                    self.enemies.append(self.enemyTypes[enemyType](pos, 12, 16, \
                        images=self.imgs[self.enemyImgs[enemyType][0]:self.enemyImgs[enemyType][1]]))
            else:
                self.boss = Boss(positions, 12, 16, images=self.imgs[0:3])
        
        self.bossDamageRects = [pygame.Rect(pos, (16, 16)) for pos in self.bossDamagePoints]
        self.bossDamageProgress = [16 for _ in self.bossDamageRects]

        self.newScreen = None

    def draw(self, win, scroll):
        if self.boss is not None:
            self.boss.draw(win, scroll)

        for enemy in self.enemies:
            #if screenRect.colliderect(enemy.rect):
            enemy.draw(win, scroll)
        
        for p, r in zip(self.bossDamageProgress, self.bossDamageRects):
            w = (p/16) * 6
            pygame.draw.rect(win, (0,200,50), (r.centerx-scroll.x-w*0.5, r.y-scroll.y, w, 5))
            pygame.draw.circle(win, (255,50,50), (r.x-scroll.x+r.w*0.5, r.y-scroll.y+5+r.w*0.5), r.w*0.5)

    def update(self, delta, tilemap, player, screenRect, playerSpawn=(0,0), colRects=None):
        if self.boss is not None:
            self.boss.update(delta, tilemap, player)
            if self.boss.spawnEnemy:
                self.boss.spawnEnemy = False
                self.enemies.append(self.enemyTypes[self.boss.enemySpawnType](self.boss.enemySpawnPos, 12, 16, \
                    images=self.imgs[self.enemyImgs[self.boss.enemySpawnType][0]:self.enemyImgs[self.boss.enemySpawnType][1]]))
                dir = self.boss.enemySpawnDir
                self.enemies[-1].decoratorObj.dir = dir
                self.enemies[-1].vel.x = self.enemies[-1].decoratorObj.getCurrentSpeed() * dir

            if not player.invincible:
                if self.boss.collide(player.rect):
                    self.reset = True
            
            if self.boss.phase > 0 and player.pos.y < 120:
                if player.pos.x > 140 and player.pos.x < 550:
                    player.displayText("Destroying these might help", 1)
                else:
                    player.displayText("Maybe I need to kick to get up there", 1)

            if player.acid:
                if player.waterParticles.collideRect(self.boss.rect):
                    if not self.boss.invincible:
                        origPhase = self.boss.phase
                        if not self.boss.damage(1):
                            self.boss = None
                            self.bossDamagePoints = []
                        if self.boss is not None and self.boss.phase != origPhase:
                            player.pos = Vector2(playerSpawn)
                            player.updateRectPos()
                            player.textQueue = []
                            player.currentText = None

                            if self.boss.phase == 1:
                                player.displayText("The shrink ray is wearing off!", 2)
                    else:
                        player.displayText("I could go up to break its invincibility")
                for i in range(len(self.bossDamageProgress))[::-1]:
                    if player.waterParticles.collideRect(self.bossDamageRects[i]):
                        self.bossDamageProgress[i] -= 0.25
                        if self.bossDamageProgress[i] < 3:
                            if AudioSettings().sfx:
                                self.rageSound.play()

                            self.bossDamageRects.pop(i)
                            self.bossDamageProgress.pop(i)

                            player.pos = Vector2(playerSpawn)
                            player.updateRectPos()
                            player.textQueue = []
                            player.currentText = None

                            player.displayText("Now I can damage it", 4)

                            self.boss.invincible = False
            
            if self.boss is None:
                self.enemies = []
                self.newScreen = src.screens.textscreen.TextScreen("res/levels/wintext.json")

        for enemy in self.enemies:
            enemy.onScreen = enemy.rect.colliderect(screenRect)
            enemy.update(delta, player, tilemap, colRects)

        for i in range(len(self.enemies))[::-1]:
            if self.enemies[i].onScreen:#screenRect.colliderect(self.enemies[i].rect):
                if player.waterParticles.collideRect(self.enemies[i].rect):
                    if player.acid:
                        if self.enemies[i].damageTimer <= 0:
                            self.enemies[i].kick(player.dir * 75)
                        if not self.enemies[i].damage(1):
                            if AudioSettings().sfx:
                                self.deathSound.play()
                            self.enemies.pop(i)
                    else:
                        self.enemies[i].stun(1)

        if not player.invincible:
            for enemy in self.enemies:
                if enemy.stunTimer <= 0 and enemy.collide(player.rect):#rect(player.rect):
                    self.reset = True

    def getStunnedRects(self):
        return [enemy.rect for enemy in self.enemies if enemy.stunTimer > 0]