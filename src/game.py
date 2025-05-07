import pygame
from pygame.locals import QUIT, KEYDOWN, KEYUP
import math
from src import config
from src.player.player import Player
from src.maps.maps import Maps

class Game:
    def __init__(self):
        self.maps = Maps()
        self.current_level = 3
        self.player = Player(self.current_level)
        self.map = self.maps.get_map(self.current_level) 

    def run(self):
        while config.RUNNING:
            config.CLOCK.tick(config.FPS)
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.set_caption("Lab")
            pygame.display.update()
        pygame.quit()

    def handle_events(self):
        for e in pygame.event.get():
            if e.type == QUIT:
                config.RUNNING = False

            if e.type == KEYDOWN:
                if e.key == pygame.K_w:
                    config.W_KEY = True
                if e.key == pygame.K_s:
                    config.S_KEY = True
                if e.key == pygame.K_a:
                    config.A_KEY = True
                if e.key == pygame.K_d:
                    config.D_KEY = True

            if e.type == KEYUP:
                if e.key == pygame.K_w:
                    config.W_KEY = False
                if e.key == pygame.K_s:
                    config.S_KEY = False
                if e.key == pygame.K_a:
                    config.A_KEY = False
                if e.key == pygame.K_d:
                    config.D_KEY = False

    def update(self):
        self.player.update()

    def draw(self):
        config.DISPLAY.fill((0, 0, 0))
        self.raycasting()

    def raycasting(self):
        for i in range(config.FOV + 1):
            rot_d = self.player.rot + math.radians(i - config.FOV/2)
            x, y = self.player.x, self.player.y
            sin, cos = (config.PRECISION * math.sin(rot_d), config.PRECISION * math.cos(rot_d))
            j = 0
            while True:
                x, y = (x + cos, y + sin)
                j += 1
                if self.map[int(y)][int(x)] != 0:
                    #tile = self.map[int(y)][int(x)]
                    d = j
                    j = j * math.cos(math.radians(i - config.FOV/2))
                    height = (10/j * 2500)
                    break
            if d/2 > 255:
                d = 510

            pygame.draw.line(config.DISPLAY,
                             (int(255 - d/2), int(255 - d/2), int(255 - d/2)),
                             (i * (config.WIN_WIDTH / config.FOV), (config.WIN_HEIGHT / 2) + height),
                             (i * (config.WIN_WIDTH / config.FOV), (config.WIN_HEIGHT / 2) - height),
                             width=int(config.WIN_WIDTH / config.FOV))
