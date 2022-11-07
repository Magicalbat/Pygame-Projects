import pygame
from pygame.math import Vector2

import json

from src.screens.screenmanager import ScreenManager, GameScreen
from src.screens.level import Level
from src.utils.text import Text

class TextScreen(GameScreen):
    def __init__(self, filepath="res/levels/texttest.json"):
        with open(filepath, 'r') as f:
            self.data = json.loads(f.read())
        
        self.text = Text()
        self.text.loadFontImg("res/imgs/text.png", scale=(1,1))

        self.nextDisplay = self.text.createTextSurf("Press any key to continue")

        #self.text.loadFontImg("res/imgs/text.png", scale=(2,2))
        
    def setup(self, screenManager):
        super().setup(screenManager)

        self.index = 0
        self.nextDisplayInterval = 2
        self.nextDisplayTimer = self.nextDisplayInterval

        self.updateTextDisplay()
        #self.currentTextDisplay = self.text.createTextSurf(self.data["Text"][self.index])
    
    def updateTextDisplay(self):
        self.currentTextDisplay = self.text.createTextSurf(self.data["Text"][self.index])
    
    def draw(self, win : pygame.Surface):
        win.fill((0, 0, 0))
        
        center = win.get_rect().center
        win.blit(self.currentTextDisplay, (center[0]-self.currentTextDisplay.get_width() * 0.5, center[1]-self.currentTextDisplay.get_height() * 0.5))

        progress = (1 - (self.nextDisplayTimer / self.nextDisplayInterval))
        self.nextDisplay.set_alpha(255 * (progress * progress * progress))

        if "Next" in self.data:
            win.blit(self.nextDisplay, (center[0]-self.nextDisplay.get_width()*0.5, win.get_height() - self.nextDisplay.get_height() * 2))
        elif self.index < len(self.data["Text"])-1:
            win.blit(self.nextDisplay, (center[0]-self.nextDisplay.get_width()*0.5, win.get_height() - self.nextDisplay.get_height() * 2))

    def update(self, delta):
        if self.nextDisplayTimer > 0:
            self.nextDisplayTimer -= delta
    
    screenTypes = {
        "Level" : Level
    }

    def keydown(self, event):
        self.index += 1

        if self.index >= len(self.data["Text"]):
            if "Next" in self.data:
                self.screenManager.changeScreen(self.screenTypes[self.data["Next"]["Type"]](self.data["Next"]["File"]))
            else:
                self.index -= 1
        else:
            self.nextDisplayTimer = self.nextDisplayInterval
            self.updateTextDisplay()