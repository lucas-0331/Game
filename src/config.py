import pygame
import numpy as np

# Configurações de tela
WIN_WIDTH, WIN_HEIGHT = (1600, 900)
GRAPHICS_QUALITY = 'medium'
FULLSCREEN = False
X_POSITION, Y_POSITION = 1.5, 1.5 
ROTATION_R = 0.0

# Configurações de movimento
PRECISION = 0.1
MOVE_SPEED = 0.08
SENSITIVITY = 0.04

# Configurações de raycasting
FOV = 80
COLUMN_WIDTH = 3 
NUM_RAYS = WIN_WIDTH // COLUMN_WIDTH
MAX_DEPTH = 15
WALL_HEIGHT = 800
MAX_WALL_HEIGHT = WIN_HEIGHT * 1.5

# Configurações de renderização e textura
TEXTURE_SIZE = 64
TEXTURE_SCALE_FACTOR = 1.0

# Configurações de shading
MIN_SHADE = 0.2
SIDE_SHADE_FACTOR = 0.7
FOG_DISTANCE = 15

# Cores base das paredes
BRICK_COLOR = (150, 100, 70)   # Tijolo
STONE_COLOR = (100, 100, 120)  # Pedra
WOOD_COLOR = (160, 100, 60)    # Madeira
DEFAULT_WALL_COLOR = (100, 100, 100)  # Cor padrão

# Cores do ambiente
FLOOR_COLOR = (50, 50, 50)
CEILING_COLOR = (15, 15, 30)

# Controles
W_KEY = S_KEY = A_KEY = D_KEY = False

# Configurações do pygame
pygame.init()
DISPLAY = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
CLOCK = pygame.time.Clock()
FPS = 60
RUNNING = True

# Configurações de otimização
ENABLE_TEXTURES = True
TEXTURE_QUALITY = 1.0
RENDER_DISTANCE = 20

# Configurações de cache
MAX_TEXTURE_CACHE_SIZE = 50
CACHE_CLEANUP_INTERVAL = 100
