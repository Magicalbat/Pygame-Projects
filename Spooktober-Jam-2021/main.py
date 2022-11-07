import pygame

"""

Sound Credits:

Song - A Wonderful Nightmare, Credit: SpiderDave

"""

def main():
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()

    pygame.event.set_allowed([pygame.QUIT])

    width = 320
    height = 180
    win = pygame.display.set_mode((width, height), pygame.SCALED | pygame.RESIZABLE, 8)
    pygame.display.set_caption('Spooktober Jam 2021')

    clock = pygame.time.Clock()
    fps = 60

    pygame.mixer.music.load("data/sounds/A_Wonderful_Nightmare.ogg")
    pygame.mixer.music.set_volume(0.1)
    pygame.mixer.music.play(-1)

    from engine.screenmanager import ScreenManager
    from game.startscreen import StartScreen
    from game.level import Level

    screenManger = ScreenManager(StartScreen())

    running = True
    while running:
        clock.tick(fps)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        win.fill((145,59,173))
        screenManger.draw(win)
        pygame.display.update()

        screenManger.update(clock.get_time() / 1000)
        
    pygame.quit()

if __name__ == '__main__':
    main()