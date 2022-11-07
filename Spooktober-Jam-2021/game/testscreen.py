import pygame

import random

from engine.gamescreen import GameScreen
from engine.tilemap import Tilemap
from engine.text import Text
from engine.common import *

from game.player import Player
from game.pumpkin import Pumpkin

class TestScreen(GameScreen):
    def setup(self):
        super().setup()

        self.tilemap = Tilemap(12)
        extraMapData = self.tilemap.loadFromJson("data/maps/really_bad_map.json", True)

        playerSpawn = [20,100]
        if 'playerSpawn' in extraMapData:
            playerSpawn = extraMapData['playerSpawn']

        self.player = Player(playerSpawn[0], playerSpawn[1], 12, 12)

        self.pumpkinImgs = loadSpriteSheet("data/images/pumpkins/pumpkin.png", (14,14), (4,2), (1,1), 8, (0,0,0))
        self.pumpkinImgs = [self.pumpkinImgs[0], self.pumpkinImgs[4], self.pumpkinImgs[5]]
        self.pumpkins = []

        self.text = Text()
        self.text.loadFontImg("data/images/text.png", scale=(2,2))

        self.fps = 0

        self.scroll = [0,0]
        self.cameraBounds = ((0,0),(0,0))

    def draw(self, win):
        #self.scroll[0] += ((self.player.pos.x - win.get_width() / 2) - self.scroll[0]) / 20
        #self.scroll[0] = clamp(self.scroll[0], self.cameraBounds[0][0], self.cameraBounds[0][1])
        
        #self.scroll[1] += ((self.player.pos.y - win.get_height() / 2) - self.scroll[1]) / 20
        #self.scroll[1] = clamp(self.scroll[1], self.cameraBounds[1][0], self.cameraBounds[1][1])

        self.tilemap.draw(win, self.scroll)

        self.player.draw(win, self.scroll)
        
        for p in self.pumpkins:
            p.draw(win, self.scroll)

        win.blit(self.text.createTextSurf(f'{self.fps}'), (0,0))

    def update(self, delta, inp, fps=0):
        if delta:
            self.fps = int(1 / delta)
        delta = min(delta, 0.1)

        entityRects = [p.rect for p in self.pumpkins]

        self.player.update(delta, inp, entityRects, self.tilemap.chunks)

        entityRects.append(self.player.rect)

        for p in self.pumpkins:
            p.update(delta, entityRects, self.tilemap.chunks)

            if p.stopping:
                p.stopping = False
                self.pumpkins.sort(key=lambda p:(p.rect.x, p.rect.y))

        if inp.keyJustPressed(pygame.K_x):
            self.pumpkins.append(Pumpkin(self.player.rect.x, self.player.rect.y, self.player.rect.w, self.player.rect.h, self.player.velocity, self.player.gravity, self.pumpkinImgs[random.randint(0,2)]))
            
            self.player.reset()

            hitlist = getCollidingRects(self.player.rect, [p.rect for p in self.pumpkins])
            
            for rect in hitlist:
                self.pumpkins.remove(rect)

        if inp.keyJustPressed(pygame.K_r):
            self.screenManager.reloadCurrentScreenWithTransition()