import pygame
import numpy as np

# Configurações de tela
WIN_WIDTH, WIN_HEIGHT = (1600, 900)
X_POSITION, Y_POSITION = 1.5, 1.5  # Posição inicial ajustada para área livre
ROTATION_R = 0.0

# Configurações de movimento
PRECISION = 0.1
MOVE_SPEED = 0.08  # Aumentado para movimento mais perceptível
SENSITIVITY = 0.04  # Rotação mais suave

# Configurações de raycasting
FOV = 80
COLUMN_WIDTH = 3  # Largura de cada coluna em pixels (variável configurável)
NUM_RAYS = WIN_WIDTH // COLUMN_WIDTH  # Número de raios baseado na largura da coluna
MAX_DEPTH = 20  # Aumentado para ver mais longe
WALL_HEIGHT = 800  # Altura das paredes

# Configurações de renderização e textura
TEXTURE_SIZE = 64  # Tamanho padrão das texturas (variável configurável)
TEXTURE_SCALE_FACTOR = 1.0  # Fator de escala para texturas

# Configurações de shading
MIN_SHADE = 0.2  # Sombra mínima (variável configurável)
SIDE_SHADE_FACTOR = 0.7  # Fator de sombra para lados Y das paredes
FOG_DISTANCE = 15  # Distância do fog

# Cores base das paredes (variáveis configuráveis)
BRICK_COLOR = (150, 100, 70)   # Tijolo
STONE_COLOR = (100, 100, 120)  # Pedra
WOOD_COLOR = (160, 100, 60)    # Madeira
DEFAULT_WALL_COLOR = (100, 100, 100)  # Cor padrão

# Cores do ambiente
FLOOR_COLOR = (40, 40, 40)
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
ENABLE_TEXTURES = True  # Habilitado para usar texturas
TEXTURE_QUALITY = 1.0  # Qualidade das texturas (1.0 = máxima)
RENDER_DISTANCE = 15

# Configurações de cache
MAX_TEXTURE_CACHE_SIZE = 50  # Tamanho máximo do cache de texturas
CACHE_CLEANUP_INTERVAL = 100  # Intervalo para limpeza do cache