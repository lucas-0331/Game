import pygame
import numpy as np

# Configurações de tela
WIN_WIDTH, WIN_HEIGHT = (1600, 900)
X_POSITION, Y_POSITION = 2.0, 2.0  # Posição inicial ajustada para área livre
ROTATION_R = 0.0

# Configurações de movimento
PRECISION = 0.1
MOVE_SPEED = 0.08  # Aumentado para movimento mais perceptível
SENSITIVITY = 0.04  # Rotação mais suave

# Configurações de raycasting
FOV = 80
NUM_RAYS = WIN_WIDTH // 3  # Melhor balance qualidade/performance
MAX_DEPTH = 20  # Aumentado para ver mais longe
WALL_HEIGHT = 8000  # Altura das paredes

# Cores
FLOOR_COLOR = (40, 40, 40)
CEILING_COLOR = (15, 15, 30)
FOG_DISTANCE = 15

# Controles
W_KEY = S_KEY = A_KEY = D_KEY = False

# Configurações do pygame
pygame.init()
DISPLAY = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
CLOCK = pygame.time.Clock()
FPS = 60
RUNNING = True

# Configurações de otimização
ENABLE_TEXTURES = False  # Desabilitado para focar na performance
TEXTURE_QUALITY = 0.5
RENDER_DISTANCE = 15