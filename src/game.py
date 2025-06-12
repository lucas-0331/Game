import pygame
from pygame.locals import QUIT
import math
import numpy as np
from src import config
from src.player.player import Player
from src.maps.maps import Maps
from src.renderer.texture_manager import TextureManager

class Game:
    def __init__(self):
        self.maps = Maps()
        self.current_level = 1
        self.player = Player(self.current_level)
        self.map = self.maps.get_map(self.current_level)
        self.texture_manager = TextureManager()
        
        # Otimizações principais
        self.setup_optimizations()
        
    def setup_optimizations(self):
        """Configurar todas as otimizações de performance"""
        # Ajustar número de raios para melhor balance performance/qualidade
        config.NUM_RAYS = config.WIN_WIDTH // 3  # Aumentado de //4 para //3
        
        # Pre-calcular ângulos dos raios
        self.ray_angles = np.array([
            math.radians(i * config.FOV / config.NUM_RAYS - config.FOV/2) 
            for i in range(config.NUM_RAYS)
        ])
        self.distance_correction = np.cos(self.ray_angles)
        
        # Buffer para distâncias (z-buffer)
        self.wall_buffer = np.full(config.NUM_RAYS, float('inf'))
        
        # Configurar surface para double buffering
        self.screen_buffer = pygame.Surface((config.WIN_WIDTH, config.WIN_HEIGHT))
        
        # Debug: mostrar posição do jogador
        self.debug_font = pygame.font.Font(None, 24)
        
    def run(self):
        while config.RUNNING:
            config.CLOCK.tick(config.FPS)
            self.handle_events()
            self.update()
            self.draw()
            
            # Mostrar FPS e posição para debug
            fps_text = f"FPS: {int(config.CLOCK.get_fps())} | Pos: ({self.player.x:.2f}, {self.player.y:.2f}) | Rot: {math.degrees(self.player.rot):.1f}°"
            pygame.display.set_caption(fps_text)
            pygame.display.flip()
        pygame.quit()

    def handle_events(self):
        """Manipular apenas eventos essenciais"""
        for e in pygame.event.get():
            if e.type == QUIT:
                config.RUNNING = False

    def update(self):
        self.player.update()

    def draw(self):
        # Limpar buffer
        self.screen_buffer.fill((0, 0, 0))
        
        # Desenhar fundo simples
        self.draw_simple_background()
        
        # Raycasting corrigido
        self.corrected_raycasting()
        
        # Debug info
        self.draw_debug_info()
        
        # Blit buffer para tela principal
        config.DISPLAY.blit(self.screen_buffer, (0, 0))

    def draw_simple_background(self):
        """Fundo simples sem gradiente custoso"""
        # Céu
        pygame.draw.rect(self.screen_buffer, config.CEILING_COLOR, 
                        (0, 0, config.WIN_WIDTH, config.WIN_HEIGHT // 2))
        # Chão
        pygame.draw.rect(self.screen_buffer, config.FLOOR_COLOR,
                        (0, config.WIN_HEIGHT // 2, config.WIN_WIDTH, config.WIN_HEIGHT // 2))

    def corrected_raycasting(self):
        """Raycasting corrigido para garantir movimento visível"""
        # Resetar buffer
        self.wall_buffer.fill(float('inf'))
        
        # Largura de cada coluna
        column_width = max(1, config.WIN_WIDTH // config.NUM_RAYS)
        
        # Posição e rotação do jogador
        px, py, prot = self.player.x, self.player.y, self.player.rot
        
        for i in range(config.NUM_RAYS):
            # Ângulo do raio atual
            ray_angle = prot + self.ray_angles[i]
            
            # Direção do raio
            dx = math.cos(ray_angle)
            dy = math.sin(ray_angle)
            
            # DDA melhorado
            distance, wall_type, hit_side = self.improved_dda(px, py, dx, dy)
            
            if distance > 0 and distance < config.MAX_DEPTH:
                # Correção fisheye
                corrected_distance = distance * self.distance_correction[i]
                
                # Altura da parede
                wall_height = min(config.WALL_HEIGHT / max(corrected_distance, 0.1), 
                                config.WIN_HEIGHT * 2)
                
                # Posições na tela
                wall_top = max(0, int((config.WIN_HEIGHT - wall_height) // 2))
                wall_bottom = min(config.WIN_HEIGHT, int(wall_top + wall_height))
                
                # Shading baseado na distância e lado da parede
                base_shade = max(0.2, 1.0 - (distance / config.FOG_DISTANCE))
                if hit_side == 1:  # Lado Y da parede (mais escuro)
                    base_shade *= 0.7
                
                # Desenhar coluna
                self.draw_wall_column(i * column_width, wall_top, wall_bottom, 
                                    wall_type, base_shade, column_width)
                
                self.wall_buffer[i] = corrected_distance

    def improved_dda(self, px, py, dx, dy):
        """DDA algorithm melhorado"""
        # Posição atual no mapa
        map_x, map_y = int(px), int(py)
        
        # Calcular delta distances
        if abs(dx) < 1e-10:
            delta_dist_x = 1e30
        else:
            delta_dist_x = abs(1.0 / dx)
            
        if abs(dy) < 1e-10:
            delta_dist_y = 1e30
        else:
            delta_dist_y = abs(1.0 / dy)
        
        # Calcular step e distância inicial
        if dx < 0:
            step_x = -1
            side_dist_x = (px - map_x) * delta_dist_x
        else:
            step_x = 1
            side_dist_x = (map_x + 1.0 - px) * delta_dist_x
            
        if dy < 0:
            step_y = -1
            side_dist_y = (py - map_y) * delta_dist_y
        else:
            step_y = 1
            side_dist_y = (map_y + 1.0 - py) * delta_dist_y
        
        # DDA loop
        hit = False
        side = 0
        wall_type = 1
        
        for _ in range(int(config.MAX_DEPTH * 2)):  # Limite para evitar loop infinito
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1
            
            # Verificar se atingiu uma parede
            if (map_y < 0 or map_y >= len(self.map) or 
                map_x < 0 or map_x >= len(self.map[0])):
                hit = True
                wall_type = 1  # Parede de borda
                break
            elif self.map[map_y][map_x] != 0:
                hit = True
                wall_type = self.map[map_y][map_x]
                break
        
        if not hit:
            return config.MAX_DEPTH, 1, 0
        
        # Calcular distância perpendicular
        if side == 0:
            perp_wall_dist = (map_x - px + (1 - step_x) / 2) / dx
        else:
            perp_wall_dist = (map_y - py + (1 - step_y) / 2) / dy
        
        return abs(perp_wall_dist), wall_type, side

    def draw_wall_column(self, x, wall_top, wall_bottom, wall_type, shade, width):
        """Desenhar coluna da parede"""
        # Cores base por tipo de parede
        base_colors = {
            1: (150, 100, 70),   # Tijolo
            2: (100, 100, 120),  # Pedra
            3: (160, 100, 60),   # Madeira
        }
        
        base_color = base_colors.get(wall_type, (100, 100, 100))
        
        # Aplicar shading
        color = (
            max(0, min(255, int(base_color[0] * shade))),
            max(0, min(255, int(base_color[1] * shade))),
            max(0, min(255, int(base_color[2] * shade)))
        )
        
        # Desenhar retângulo
        height = max(1, wall_bottom - wall_top)
        if height > 0 and x >= 0 and x < config.WIN_WIDTH:
            pygame.draw.rect(self.screen_buffer, color, 
                           (x, wall_top, width, height))

    def draw_debug_info(self):
        """Desenhar informações de debug na tela"""
        debug_texts = [
            f"Pos: ({self.player.x:.2f}, {self.player.y:.2f})",
            f"Rot: {math.degrees(self.player.rot):.1f}°",
            f"Map: {self.get_map_cell(self.player.x, self.player.y)}",
            f"Rays: {config.NUM_RAYS}",
        ]
        
        for i, text in enumerate(debug_texts):
            surface = self.debug_font.render(text, True, (255, 255, 255))
            self.screen_buffer.blit(surface, (10, 10 + i * 25))

    def get_map_cell(self, x, y):
        """Obter célula do mapa na posição"""
        map_x, map_y = int(x), int(y)
        if (0 <= map_y < len(self.map) and 0 <= map_x < len(self.map[0])):
            return self.map[map_y][map_x]
        return "OOB"  # Out of bounds