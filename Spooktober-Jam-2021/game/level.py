import pygame

import random

from engine.gamescreen import GameScreen
from engine.tilemap import Tilemap
from engine.text import Text
from engine.menu import Menu
from engine.particles import Particles
from engine.common import *

from game.player import Player
from game.pumpkin import Pumpkin
from game.ghost import Ghost
from game.audiosettings import AudioSettings

class Level(GameScreen):
    def setup(self):
        super().setup()

        self.tilemap = Tilemap(12)
        extraMapData = self.tilemap.loadFromJson(f"data/maps/level{self.levelNum}.json", True)
        #level{self.levelNum}.json

        playerSpawn = [20,100]
        if 'playerSpawn' in extraMapData:
            playerSpawn = extraMapData['playerSpawn'][0]

        self.player = Player(playerSpawn[0], playerSpawn[1], 12, 12)
        self.ghost = Ghost(0, 0, 12, 12, self.player.gravity)

        self.levelExitImg = pygame.image.load("data/images/tiles/candles.png").convert()
        self.levelExitImg.set_colorkey((0,0,0))
        self.levelExitParticles = Particles([2,4], [-4, 4, -1, 1], [-15, 15, -35, -40], 100, True, 4, colors=((250, 192, 0), (255, 117, 0), (255,255,0), (255,128,0)))
        if 'levelExit' in extraMapData:
            self.levelExit = pygame.Rect((extraMapData['levelExit'][0][0], extraMapData['levelExit'][0][1], 12, 12))
        else:
            self.levelExit = pygame.Rect((0,0,0,0))
        
        self.spikeImg = pygame.image.load("data/images/tiles/spikes.png").convert()
        self.spikeImg.set_colorkey((0,0,0))
        self.spikes = []
        if 'spikes' in extraMapData:
            for pos in extraMapData['spikes']:
                self.spikes.append(pygame.Rect((pos[0], pos[1] + 8, 12, 4)))

        self.jackOLanternImg = pygame.image.load("data/images/characters/jack_o_lantern.png").convert()
        self.jackOLanternImg.set_colorkey((0,0,0))
        self.pumpkinImgs = loadSpriteSheet("data/images/characters/Pumpkin.png", (14,14), (4,2), (1,1), 8, (0,0,0))
        self.pumpkinImgs = [self.pumpkinImgs[0], self.pumpkinImgs[4], self.pumpkinImgs[5]]
        self.pumpkins = []

        self.pumpkinSpawnSound = pygame.mixer.Sound("data/sounds/pumpkin.wav")

        self.maxPumpkins = 1
        if 'maxPumpkins' in extraMapData:
            self.maxPumpkins = extraMapData['maxPumpkins']
        
        self.wind = []
        self.windSpeed = self.player.gravity
        self.windParticles = Particles((5, 6), (0, 12, -2, 2), (-.1, .1, -10, -25), 1000, True, 6, colors=((255,255,255),(225,225,225),(200,200,200)))
        if 'wind' in extraMapData:
            for pos in extraMapData['wind']:
                self.wind.append(pygame.Rect((pos[0], pos[1], 12, 12)))

        self.text = Text()
        self.text.loadFontImg("data/images/text.png", scale=(2,2), color=(255, 229, 127))

        self.levelText = None
        self.levelTextPos = [0,0]

        if 'text' in extraMapData:
            if isinstance(extraMapData['text'][1],str):
                self.levelTextPos = extraMapData['text'][0]
                self.levelText = self.text.createTextSurf(extraMapData['text'][1]).copy()
                self.text.loadFontImg("data/images/text.png", scale=(2,2))

        self.fps = 0

        self.scroll = [0,0]
        self.cameraBounds = ((0,0),(0,0))
        if 'cameraBounds' in extraMapData:
            if len(extraMapData['cameraBounds']) == 1:
                self.cameraBound = ((0,0), extraMapData['cameraBounds'][0])
            else:
                self.cameraBounds = (sorted((extraMapData['cameraBounds'][0], extraMapData['cameraBounds'][1])))
        
        self.pauseMenu = Menu(["Resume", "Restart", "Back"], 2, (0, 20), (5, 25), {0:self.togglePause, 1:self.screenManager.reloadCurrentScreenWithTransition, 2:self.screenManager.changeScreenWithTransition}, {2:self.prevScreen})
        self.paused = False
        
        self.alphaSurf = pygame.Surface((320,180))
        self.alphaSurf.fill((0,0,0))
        self.alphaSurf.set_alpha(128)

        self.lightningTimer = 0
        self.lightningSound = pygame.mixer.Sound("data/sounds/thunder.wav")
        self.lightningSound.set_volume(0.25)
    
    def __init__(self, levelNum=1, prevScreen=None):
        self.levelNum = levelNum
        self.prevScreen = prevScreen
        super().__init__()
    
    def togglePause(self):
        self.paused = not self.paused

    def draw(self, win):
        #if abs(((self.player.pos.x - win.get_width() / 2) - self.scroll[0]) - self.scroll[0]) > 25:
        self.scroll[0] += ((self.player.pos.x - win.get_width() / 2) - self.scroll[0]) / 20
        self.scroll[0] = clamp(self.scroll[0], self.cameraBounds[0][0], self.cameraBounds[1][0])
        
        self.scroll[1] += ((self.player.pos.y - win.get_height() / 2) - self.scroll[1]) / 20
        self.scroll[1] = clamp(self.scroll[1], self.cameraBounds[0][1], self.cameraBounds[1][1])

        if self.lightningTimer > 0:
            self.scroll[0] += random.randint(0,8) - 4
            self.scroll[1] += random.randint(0,8) - 4

        self.tilemap.draw(win, self.scroll)

        for s in self.spikes:
            #pygame.draw.rect(win, (255,0,0), (s.x - self.scroll[0], s.y - self.scroll[1], s.w, s.h))
            win.blit(self.spikeImg, (s.x - self.scroll[0], s.y - self.scroll[1] - 4))
        
        if self.levelExit != pygame.Rect((0,0,0,0)):
            win.blit(self.levelExitImg, (self.levelExit.x - self.scroll[0], self.levelExit.y - self.scroll[1]))

            self.levelExitParticles.draw(win, self.scroll)

        for w in self.wind:
            self.windParticles.emit((w.x, w.y + 12), .2)
            #pygame.draw.rect(win, (0,128,128), (w.x - self.scroll[0], w.y - self.scroll[1], w.w, w.h))
        self.windParticles.draw(win, self.scroll)

        if self.levelText is not None:
            win.blit(self.levelText, (self.levelTextPos[0] - self.scroll[0], self.levelTextPos[1] - self.scroll[1]))
        
        if self.ghost.active:
            win.blit(self.alphaSurf, (0,0))
        
        self.player.draw(win, self.scroll)
        
        self.ghost.draw(win, self.scroll)

        for p in self.pumpkins:
            p.draw(win, self.scroll)
        
        if self.lightningTimer > 0.15:
            win.fill((225,225,225))

        win.blit(self.pumpkinImgs[0], (4,4))
        win.blit(self.text.createTextSurf(f': {self.maxPumpkins - len(self.pumpkins)}'), (20,4))

        if self.paused:
            win.blit(self.alphaSurf, (0,0))
            self.pauseMenu.draw(win)

    def update(self, delta, inp):
        if delta:
            self.fps = int(1 / delta)
            delta = min(delta, 0.1)
        
        if self.lightningTimer > 0:
            self.lightningTimer -= delta
        
        if inp.keyJustPressed(pygame.K_ESCAPE):
            self.togglePause()

        if not self.paused:
            entityRects = [p.rect for p in self.pumpkins]

            self.windParticles.update(delta)

            self.player.update(delta, inp, entityRects, self.tilemap.chunks)

            if self.player.rect.collidelist(self.wind) != -1:
                dist = abs(self.player.pos.y) % 12
                if dist < 1:
                    self.player.velocity.y -= self.windSpeed * delta * 1.4
                self.player.velocity.y -= self.windSpeed * delta * ((max(dist, 2) / 12) * 5)

            entityRects.append(self.player.rect)

            for p in self.pumpkins:
                if p.rect.collidelist(self.wind) != -1:
                    dist = abs(p.pos.y) % 12
                    p.velocity.y -= self.windSpeed * delta * ((max(dist, 2) / 12) * 5)

                p.update(delta, entityRects, self.tilemap.chunks)

                if p.stopping:
                    p.stopping = False
                    self.pumpkins.sort(key=lambda p:(p.rect.x, p.rect.y))

            if inp.keyJustPressed(pygame.K_x):
                if len(self.pumpkins) + 1 <= self.maxPumpkins:
                    self.pumpkins.append(Pumpkin(self.player.rect.x, self.player.rect.y, self.player.rect.w, self.player.rect.h, self.player.velocity, self.player.gravity, self.pumpkinImgs[random.randint(0,2)], self.jackOLanternImg))
                
                    self.player.reset()

                    hitlist = getCollidingRects(self.player.rect, [p.rect for p in self.pumpkins])
                
                    for rect in hitlist:
                        self.pumpkins.remove(rect)
                    
                    if AudioSettings().sfx:
                        self.pumpkinSpawnSound.play()
            
            if self.player.rect.collidelist(self.spikes) != -1:
                self.player.reset()
            
            if self.levelExit != pygame.Rect((0,0,0,0)):
                self.levelExitParticles.update(delta)
                
                self.levelExitParticles.emit((self.levelExit.x+1, self.levelExit.y+5), 0.025)
                self.levelExitParticles.emit((self.levelExit.x+5, self.levelExit.y+4), 0.025)
                self.levelExitParticles.emit((self.levelExit.x+7, self.levelExit.y+6), 0.025)
                self.levelExitParticles.emit((self.levelExit.x+10, self.levelExit.y+3), 0.025)

            if self.player.rect.colliderect(self.levelExit) and not self.ghost.active:
                self.ghost.activate(self.player.pos, (self.player.pos.x < 320 / 2) * 2 - 1)
                self.player.applyGravity = False
                self.player.applyVelocity = False
                self.player.handleCollision = False

                for p in self.pumpkins:
                    p.changeToJackOLantern()
                
                self.lightningTimer = .25
                if AudioSettings().sfx:
                    self.lightningSound.play()
            
            if self.ghost.active:
                self.player.pos = pygame.math.Vector2(self.ghost.pos.x, self.ghost.pos.y + 10)
                self.player.updateRect()
            
            if self.ghost.finished:
                #from game.startscreen import StartScreen
                self.screenManager.changeScreenWithTransition(Level(self.levelNum + 1, self.prevScreen))
            
            self.ghost.update(delta)

            if inp.keyJustPressed(pygame.K_r):
                self.screenManager.reloadCurrentScreenWithTransition()
        else:
            self.pauseMenu.update(inp, delta)