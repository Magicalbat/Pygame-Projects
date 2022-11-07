import pygame

from engine.gamescreen import GameScreen
from engine.text import Text
from engine.menu import Menu

class ControlsScreen(GameScreen):
    def setup(self):
        self.text = Text()
        self.text.loadFontImg("data/images/text.png", scale=(2,2), color=(255, 229, 127))

        self.textSurf = self.text.createTextSurf("Left, Right -> move\nc / Up -> jump\nx -> discard pumpkin\nr -> restart\nESC -> pause\nF11/CTRL+f -> toggle fullscreen\nm -> mute music\ns -> mute sfx").copy()
        
        self.backMenu = Menu(["Back"], 2, (0, 20), (5, 5), {0:self.screenManager.changeScreenWithTransition}, {0:self.prevScreen}, (255, 229, 127))

    def __init__(self, prevScreen=None):
        self.prevScreen = prevScreen
        super().__init__()
    
    def draw(self, win):
        self.backMenu.draw(win)
        
        win.blit(self.textSurf, (10, 25))
    
    def update(self, delta, inp):
        self.backMenu.update(inp, delta)