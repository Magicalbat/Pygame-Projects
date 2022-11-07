import pygame
from pygame.math import Vector2

from src.screens.screenmanager import ScreenManager
from src.screens.level import Level 
from src.screens.textscreen import TextScreen

"""

Song Credit - 
https://opengameart.org/content/tower-defense-theme
https://opengameart.org/users/dst

Sound Credit - 
https://opengameart.org/content/rage-mode

"""

def main():
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()

    width = 320
    height = 180
    win = pygame.display.set_mode((width, height), pygame.SCALED | pygame.RESIZABLE, 8)
    pygame.display.set_caption('Metroidvania Month 15')

    clock = pygame.time.Clock()
    fps = 60

    pygame.mixer.music.load("res/sound/DST-TowerDefenseTheme.mp3")
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)

    screenManager = ScreenManager(TextScreen("res/levels/starttext.json"))
    
    running = True
    while running:
        clock.tick(fps)
        delta = min(clock.get_time() / 1000, 0.1)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                screenManager.keydown(event)
            if event.type == pygame.KEYUP:
                screenManager.keyup(event)

        screenManager.update(delta)

        win.fill((0,0,0))

        screenManager.draw(win)

        pygame.display.update()

    pygame.quit()

if __name__ == '__main__':
    main()