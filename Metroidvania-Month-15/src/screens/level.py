import pygame
from pygame.math import Vector2

import math, copy, random

from src.screens.screenmanager import ScreenManager, GameScreen
    
from src.entities.player import Player
from src.entities.enemy import GroundEnemy
from src.entities.enemymanager import EnemyManager

from src.utils.tilemap import Tilemap
from src.utils.camera import Camera
from src.utils.text import Text
from src.utils.specialtiles import SpecialTileManager
from src.utils.common import *

class Level(GameScreen):
    def __init__(self, filepath="res/levels/level0.json", **kwargs):
        self.stars = []
        for _ in range(random.randrange(400, 800)):
            self.stars.append((Vector2(random.randrange(-320, 640), random.randrange(-180, 360)), random.randrange(1,3), random.random()*3))
        
        tileImgs = loadSpriteSheet("res/imgs/labtiles.png", (16,16), (5,5), (1,1), 25, (0,0,0))
        self.tilemap = Tilemap(16, tileImgs)
        extraData = self.tilemap.loadLevel(filepath)

        self.returnIndex = -1
        if "returnIndex" in kwargs:
            self.returnIndex = kwargs["returnIndex"]
        
        self.transitionTimer = 1

        text = Text()
        text.loadFontImg("res/imgs/text.png", scale=(2,2))
        
        self.pauseSurf = pygame.Surface((320, 180)).convert()
        self.pauseSurf.set_colorkey((255,0,255))
        self.pauseSurf.fill((0,0,0))
        self.pauseSurf.set_alpha(64)
        pauseText = text.createTextSurf("Paused")
        self.pauseSurf.blit(pauseText, (160 - pauseText.get_width() * 0.5, 90 - pauseText.get_height() * 0.5))

        self.enemyManager = EnemyManager(extraData)

        self.processExtraData(extraData)

        if "player" in kwargs:
            self.player = kwargs["player"] 
            self.player.pos = self.playerSpawn
            self.player.updateRectPos()

    def setup(self, screenManager):
        super().setup(screenManager)

        self.paused = False

        if hasattr(self, "player"):
            self.player.vel = Vector2(0, 0)
            self.player.pos = copy.deepcopy(self.playerSpawn)
            self.player.updateRectPos()
            self.player.textQueue = []
            self.player.currentText = None
            #self.player = Player(self.playerSpawn, 12, 16, images=self.player.imgs, text=self.player.text)
        else:
            self.player = Player(self.playerSpawn, 12, 16)
            self.player.displayText("Left and right to move")
            self.player.displayText("C to jump")
            self.player.displayText("Hold X to spray water", 8)
            self.player.displayText("Green acid will kill you", 8)
            self.player.displayText("Your water can freeze enemies", 7)
            self.player.displayText("Have fun!")

        self.enemyManager.setup()
        self.specialTileManager.setup()

        self.awaitingSpawn = False
        self.awaitingSpawnTimer = 0
        #self.enemies = [GroundEnemy(pos, 12, 16) for pos in self.enemyPositions]

        self.screenRect = pygame.Rect(0,0,0,0)

    def draw(self, win : pygame.Surface):
        if self.transitionTimer > 0:
            self.camera.smoothing = 1
        else:
            self.camera.smoothing = 10
        self.camera.update(self.player, win.get_size())
        if self.camera.changedTarget:
            self.awaitingSpawn = True
            self.awaitingSpawnTimer = 0.1

        if self.awaitingSpawn and self.awaitingSpawnTimer <= 0 and self.player.collisionDir & 0b0010 > 0:
            self.playerSpawn = copy.deepcopy(self.player.pos)
            self.awaitingSpawn = False

        self.screenRect = pygame.Rect(self.camera.scroll-Vector2(25,25), (win.get_width()+25, win.get_width()+25))

        scaledTicks = pygame.time.get_ticks() / 350
        for star in self.stars:
            pygame.draw.circle(win, (255,255,0), star[0]-self.camera.scroll/20, star[1]+math.sin(scaledTicks+star[2]))
        
        self.tilemap.draw(win, self.camera.scroll)
        #self.tilemap.drawCollision(win, self.camera.scroll)
        self.specialTileManager.draw(win, self.camera.scroll)

        for pickup in self.pickups:
            r = pickup[0]
            pygame.draw.rect(win, (0,255,255), (r.topleft-self.camera.scroll, (r.w, r.h)))

        self.enemyManager.draw(win, self.camera.scroll)
        self.player.draw(win, self.camera.scroll)

        if self.paused:
            win.blit(self.pauseSurf, (0,0))

        #for lc in self.levelChanges:
        #    r = lc[0]
        #    pygame.draw.rect(win, (0,255,0), (r.topleft-self.camera.scroll, (r.w,r.h)))

        #pygame.draw.rect(win, (255,0,0), (self.playerSpawn-self.camera.scroll, (16,16)))

    def update(self, delta):
        if not self.paused:
            self.player.update(delta, self.tilemap, self.enemyManager, self.enemyManager.getStunnedRects()+self.specialTileManager.getColRects())

            self.enemyManager.update(delta, self.tilemap, self.player, self.screenRect, self.playerSpawn, []+self.specialTileManager.getColRects())
            if self.enemyManager.newScreen is not None:
                self.screenManager.changeScreen(self.enemyManager.newScreen)

            self.specialTileManager.update(delta, self.player)

            if self.enemyManager.reset or self.specialTileManager.reset:
                self.screenManager.reloadCurrentScreen()

            if self.awaitingSpawnTimer > 0:
                self.awaitingSpawnTimer -= delta
        
            for lc in self.levelChanges:
                if lc[0].colliderect(self.player.rect):
                    self.screenManager.changeScreen(Level(lc[1], player=self.player, returnIndex=lc[2]))

            for i in range(len(self.pickups))[::-1]:
                if self.pickups[i][0].colliderect(self.player.rect):
                    self.player.addPickup(self.pickups[i][1])
                    self.pickups.pop(i)
        
        if self.transitionTimer > 0:
            self.transitionTimer -= delta

    def keydown(self, event):
        self.player.keydown(event)

        if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
            self.paused = not self.paused

    def keyup(self, event):
        self.player.keyup(event)

    def processExtraData(self, extraData):
        self.playerSpawn = Vector2(0,0)
        if "PlayerSpawn" in extraData:
            self.playerSpawn = Vector2(extraData["PlayerSpawn"][0][0], extraData["PlayerSpawn"][0][1] - 16)
        cameraTriggerRects = []
        cameraTriggerVectors = []
        if "CameraTriggers" in extraData:
            for i in range(int(len(extraData["CameraTriggers"])/2)):
                p1 = Vector2(extraData["CameraTriggers"][i*2])
                p2 = Vector2(extraData["CameraTriggers"][i*2+1])
                #r = pygame.Rect(p1, p2-p1)
                cameraTriggerRects.append(pygame.Rect(p1, p2-p1))
                cameraTriggerVectors.append((p1, p2))
        self.camera = Camera(cameraTriggerRects, cameraTriggerVectors)

        self.levelChanges = []
        if "ToLevel" in extraData:
            for item in extraData["ToLevel"]:
                self.levelChanges.append((
                    pygame.Rect(item["Pos"], (16, 16)),
                    item["LevelPath"], item["Index"]
                ))

        if self.returnIndex >= 0:
            if "FromLevel" in extraData:
                pos = extraData["FromLevel"][self.returnIndex]
                self.playerSpawn = Vector2(pos[0], pos[1] - 16)

        self.pickups = []
        if "Pickup" in extraData:
            for item in extraData["Pickup"]:
                self.pickups.append((
                    pygame.Rect(item["Pos"], (16, 16)),
                    item["Type"]
                ))

        self.specialTileManager = SpecialTileManager(extraData)