import pygame

from src.audiosettings import AudioSettings

class GameScreen:
    def __init__(self):    pass
    def setup(self, screenManager):
        self.screenManager = screenManager 
    def draw(self, win):    pass
    def update(self, delta):    pass
    def keydown(self, event):    pass
    def keyup(self, event):    pass

class ScreenManager:
    def __init__(self, startScreen):
        self.curScreen = startScreen
        self.curScreen.setup(self)
    
    def changeScreen(self, newScreen):
        del self.curScreen
        self.curScreen = newScreen
        self.curScreen.setup(self)

    def reloadCurrentScreen(self):
        self.curScreen.setup(self)
        
    def draw(self, win):
        self.curScreen.draw(win)
    def update(self, delta):
        self.curScreen.update(delta)
        
    def keydown(self, event):
        if event.key == pygame.K_m:
            AudioSettings().sfx = not AudioSettings().sfx
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.pause()
            else:
                pygame.mixer.music.unpause()

        self.curScreen.keydown(event)
    def keyup(self, event):
        self.curScreen.keyup(event)