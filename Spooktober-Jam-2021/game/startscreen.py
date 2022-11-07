import sys

import pygame

from engine.gamescreen import GameScreen
from engine.menu import Menu
from engine.text import Text
from engine.common import *

from game.controlsscreen import ControlsScreen
from game.creditsscreen import CreditsScreen
from game.level import Level

class StartScreen(GameScreen):
    def quit(self):
        pygame.quit()
        sys.exit()

    def setup(self):
        self.text = Text()
        self.text.loadFontImg("data/images/text.png", scale=(3,3), color=(70,214,26))

        self.textSurf = self.text.createTextSurf("Pumpkin Jump")
        
        pumpkinSheet = loadSpriteSheet("data/images/characters/Pumpkin.png", (14,14), (4,2), (1,1), 8, (0,0,0))
        self.pumpkinImg = pumpkinSheet[0].copy()
        self.pumpkinImg.blit(pumpkinSheet[6], (0,0))
        self.pumpkinImg = pygame.transform.flip(pygame.transform.scale(self.pumpkinImg, (12*4, 12*4)), True, False)

        self.menu = Menu(["Start", "Controls", "Credits", "Exit"], 3, (0, 35), (15, 25), \
            {0:self.screenManager.changeScreenWithTransition, 1:self.screenManager.changeScreenWithTransition, 2:self.screenManager.changeScreenWithTransition, 3:self.quit},\
                 {0:Level(prevScreen=self), 1:ControlsScreen(prevScreen=self), 2:CreditsScreen(prevScreen=self)}, (255, 229, 127))

    def draw(self, win):
        self.menu.draw(win)
        
        win.blit(self.textSurf, (150, 50))
        win.blit(self.pumpkinImg, (200, 80))

    def update(self, delta, inp):
        self.menu.update(inp, delta)