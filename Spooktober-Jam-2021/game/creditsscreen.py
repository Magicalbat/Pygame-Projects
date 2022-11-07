import pygame

import webbrowser

from engine.gamescreen import GameScreen
from engine.text import Text
from engine.menu import Menu

class CreditsScreen(GameScreen):
    def setup(self):
        self.backMenu = Menu(["Back", "Song - SpiderDave", "Code, Art - Magicalbat(myself)", "Made with Pygame"], 2, (0, 40), (5, 5), \
            {0:self.screenManager.changeScreenWithTransition, 1:webbrowser.open, 2:webbrowser.open, 3:webbrowser.open}, \
                {0:self.prevScreen, 1:"https://opengameart.org/users/spiderdave", 2:"https://magicalbat.itch.io", 3:"https://www.pygame.org/news"}, (255, 229, 127))

    def __init__(self, prevScreen=None):
        self.prevScreen = prevScreen
        super().__init__()
    
    def draw(self, win):
        self.backMenu.draw(win)
    
    def update(self, delta, inp):
        self.backMenu.update(inp, delta)