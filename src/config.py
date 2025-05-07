import pygame

WIN_WIDTH, WIN_HEIGHT = (1600, 900)

X_POSITION, Y_POSITION = 1, 1
ROTATION_R = 0
PRECISION = 0.02

MOVE_SPEED = 0.01
SENSITIVITY = 0.01

W_KEY, S_KEY, A_KEY, D_KEY = False, False, False, False

pygame.init()
DISPLAY = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
CLOCK = pygame.time.Clock()
FPS = 200 
RUNNING = True
FOV = 80 
