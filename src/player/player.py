import math
import pygame
from src import config
from src.maps.maps import Maps

class Player:
    def __init__(self, lvl):
        self.x = config.X_POSITION
        self.y = config.Y_POSITION
        self.rot = config.ROTATION_R
        self.speed = config.MOVE_SPEED
        self.sensitivity = config.SENSITIVITY
        self.maps = Maps()
        self.map = self.maps.get_map(lvl)
        
        # Collision detection otimizada
        self.collision_radius = 0.15
        
        # Debug: armazenar posição anterior para detectar movimento
        self.prev_x = self.x
        self.prev_y = self.y

    def update(self):
        # Armazenar posição anterior
        self.prev_x = self.x
        self.prev_y = self.y
        
        # Obter estado atual das teclas
        keys = pygame.key.get_pressed()
        
        new_x, new_y = self.x, self.y
        moved = False
        
        # Movimento baseado no estado das teclas
        if keys[pygame.K_w]:
            new_x += self.speed * math.cos(self.rot)
            new_y += self.speed * math.sin(self.rot)
            moved = True
        if keys[pygame.K_s]:
            new_x -= self.speed * math.cos(self.rot)
            new_y -= self.speed * math.sin(self.rot)
            moved = True
        
        # Movimento lateral (strafe)
        if keys[pygame.K_q]:  # Adicionar strafe esquerda
            new_x += self.speed * math.cos(self.rot - math.pi/2)
            new_y += self.speed * math.sin(self.rot - math.pi/2)
            moved = True
        if keys[pygame.K_e]:  # Adicionar strafe direita
            new_x += self.speed * math.cos(self.rot + math.pi/2)
            new_y += self.speed * math.sin(self.rot + math.pi/2)
            moved = True
        
        # Rotação baseada no estado das teclas
        if keys[pygame.K_a]:
            self.rot -= self.sensitivity
        if keys[pygame.K_d]:
            self.rot += self.sensitivity
        
        # Normalizar rotação
        while self.rot > 2 * math.pi:
            self.rot -= 2 * math.pi
        while self.rot < 0:
            self.rot += 2 * math.pi
        
        # Collision detection melhorada
        if self.can_move_to(new_x, self.y):
            self.x = new_x
        if self.can_move_to(self.x, new_y):
            self.y = new_y
        
        # Debug: imprimir movimento se houver
        if moved and (abs(self.x - self.prev_x) > 0.001 or abs(self.y - self.prev_y) > 0.001):
            print(f"Player moved: ({self.prev_x:.3f}, {self.prev_y:.3f}) -> ({self.x:.3f}, {self.y:.3f})")
            
        # Atualizar config global
        config.X_POSITION = self.x
        config.Y_POSITION = self.y
        config.ROTATION_R = self.rot

    def can_move_to(self, x, y):
        """Verificação de colisão melhorada"""
        # Verificar múltiplos pontos ao redor do jogador
        points = [
            (x + self.collision_radius, y + self.collision_radius),
            (x - self.collision_radius, y + self.collision_radius),
            (x + self.collision_radius, y - self.collision_radius),
            (x - self.collision_radius, y - self.collision_radius),
            (x, y)  # Centro
        ]
        
        for px, py in points:
            map_x, map_y = int(px), int(py)
            # Verificar limites do mapa
            if (map_y < 0 or map_y >= len(self.map) or 
                map_x < 0 or map_x >= len(self.map[0])):
                return False
            # Verificar se a célula é uma parede
            if self.map[map_y][map_x] != 0:
                return False
        return True
    
    def get_current_map_cell(self):
        """Retorna a célula atual do mapa"""
        map_x, map_y = int(self.x), int(self.y)
        if (0 <= map_y < len(self.map) and 0 <= map_x < len(self.map[0])):
            return self.map[map_y][map_x]
        return -1  # Fora dos limites