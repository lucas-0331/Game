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
        
        self.setup_optimizations()
        
    def setup_optimizations(self):
        """Configurar todas as otimizações de performance"""
        config.NUM_RAYS = config.WIN_WIDTH // config.COLUMN_WIDTH
        
        self.ray_angles = np.array([
            math.radians(i * config.FOV / config.NUM_RAYS - config.FOV/2) 
            for i in range(config.NUM_RAYS)
        ])
        self.distance_correction = np.cos(self.ray_angles)
        
        self.wall_buffer = np.full(config.NUM_RAYS, float('inf'))
        
        self.screen_buffer = pygame.Surface((config.WIN_WIDTH, config.WIN_HEIGHT))
        
        self.texture_column_cache = {}
        self.max_column_cache = 200
        
        self.temp_surface = pygame.Surface((config.COLUMN_WIDTH, config.WIN_HEIGHT))
        
        self.shade_lut = np.linspace(0, 1, 256)
        
        self.debug_font = pygame.font.Font(None, 24)
        
    def run(self):
        while config.RUNNING:
            config.CLOCK.tick(config.FPS)
            self.handle_events()
            self.update()
            self.draw()
            
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
        self.screen_buffer.fill((0, 0, 0))
        
        self.draw_simple_background()
        
        self.optimized_textured_raycasting()
        
        self.draw_debug_info()
        
        config.DISPLAY.blit(self.screen_buffer, (0, 0))

    def draw_simple_background(self):
        """Fundo simples sem gradiente custoso"""
        pygame.draw.rect(self.screen_buffer, config.CEILING_COLOR, 
                        (0, 0, config.WIN_WIDTH, config.WIN_HEIGHT // 2))
        pygame.draw.rect(self.screen_buffer, config.FLOOR_COLOR,
                        (0, config.WIN_HEIGHT // 2, config.WIN_WIDTH, config.WIN_HEIGHT // 2))

    def optimized_textured_raycasting(self):
        """Raycasting com texturização otimizada para performance"""
        self.wall_buffer.fill(float('inf'))
        
        px, py, prot = self.player.x, self.player.y, self.player.rot
        
        for i in range(config.NUM_RAYS):
            ray_angle = prot + self.ray_angles[i]
            
            dx = math.cos(ray_angle)
            dy = math.sin(ray_angle)
            
            distance, wall_type, hit_side, wall_x = self.improved_dda_with_texture(px, py, dx, dy)
            
            if distance > 0 and distance < config.MAX_DEPTH:
                corrected_distance = distance * self.distance_correction[i]
                
                wall_height = min(config.WALL_HEIGHT / max(corrected_distance, 0.1), 
                                config.WIN_HEIGHT * 2)
                
                wall_top = max(0, int((config.WIN_HEIGHT - wall_height) // 2))
                wall_bottom = min(config.WIN_HEIGHT, int(wall_top + wall_height))
                
                base_shade = max(config.MIN_SHADE, 1.0 - (distance / config.FOG_DISTANCE))
                if hit_side == 1:
                    base_shade *= config.SIDE_SHADE_FACTOR
                
                self.draw_optimized_textured_column(i * config.COLUMN_WIDTH, wall_top, wall_bottom, 
                                                  wall_type, base_shade, wall_x, hit_side)
                
                self.wall_buffer[i] = corrected_distance

    def improved_dda_with_texture(self, px, py, dx, dy):
        """DDA algorithm melhorado com informações de textura"""
        map_x, map_y = int(px), int(py)
        
        if abs(dx) < 1e-10:
            delta_dist_x = 1e30
        else:
            delta_dist_x = abs(1.0 / dx)
            
        if abs(dy) < 1e-10:
            delta_dist_y = 1e30
        else:
            delta_dist_y = abs(1.0 / dy)
        
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
        
        hit = False
        side = 0
        wall_type = 1
        
        for _ in range(int(config.MAX_DEPTH * 2)):
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1
            
            if (map_y < 0 or map_y >= len(self.map) or 
                map_x < 0 or map_x >= len(self.map[0])):
                hit = True
                wall_type = 1
                break
            elif self.map[map_y][map_x] != 0:
                hit = True
                wall_type = self.map[map_y][map_x]
                break
        
        if not hit:
            return config.MAX_DEPTH, 1, 0, 0.0
        
        if side == 0:
            perp_wall_dist = (map_x - px + (1 - step_x) / 2) / dx
            wall_x = py + perp_wall_dist * dy
        else:
            perp_wall_dist = (map_y - py + (1 - step_y) / 2) / dy
            wall_x = px + perp_wall_dist * dx
        
        wall_x = wall_x - math.floor(wall_x)
        
        return abs(perp_wall_dist), wall_type, side, wall_x

    def draw_optimized_textured_column(self, screen_x, wall_top, wall_bottom, wall_type, shade, wall_x, hit_side):
        """MÉTODO OTIMIZADO: Desenhar coluna da parede com textura de forma eficiente"""
        wall_height = wall_bottom - wall_top
        
        if wall_height <= 0 or screen_x < 0 or screen_x >= config.WIN_WIDTH:
            return
        
        texture = self.texture_manager.get_wall_texture(wall_type)
        
        if config.ENABLE_TEXTURES and texture:
            self.draw_fast_textured_column(screen_x, wall_top, wall_bottom, texture, wall_x, shade)
        else:
            self.draw_solid_color_column(screen_x, wall_top, wall_bottom, wall_type, shade)

    def draw_fast_textured_column(self, screen_x, wall_top, wall_bottom, texture, wall_x, shade):
        """OTIMIZAÇÃO PRINCIPAL: Renderização rápida de coluna com textura"""
        tex_width, tex_height = texture.get_size()
        wall_height = wall_bottom - wall_top
        
        if wall_height <= 0:
            return
        
        cache_key = (id(texture), int(wall_x * tex_width), wall_height, int(shade * 100))
        
        if cache_key in self.texture_column_cache:
            cached_column = self.texture_column_cache[cache_key]
            self.blit_column_fast(screen_x, wall_top, cached_column)
            return
        
        tex_x = int(wall_x * tex_width) % tex_width
        
        tex_column_rect = pygame.Rect(tex_x, 0, 1, tex_height)
        try:
            tex_column = texture.subsurface(tex_column_rect)
            
            scaled_column = pygame.transform.scale(tex_column, (config.COLUMN_WIDTH, wall_height))
            
            if shade < 1.0:
                scaled_column = self.apply_shade_fast(scaled_column, shade)
            
            if len(self.texture_column_cache) < self.max_column_cache:
                self.texture_column_cache[cache_key] = scaled_column.copy()
            
            self.blit_column_fast(screen_x, wall_top, scaled_column)
            
        except (ValueError, pygame.error):
            self.draw_solid_color_column(screen_x, wall_top, wall_bottom, 1, shade)

    def apply_shade_fast(self, surface, shade):
        """OTIMIZAÇÃO: Aplicar shading rapidamente usando operações de surface"""
        shade_surface = pygame.Surface(surface.get_size())
        shade_value = int(255 * shade)
        shade_surface.fill((shade_value, shade_value, shade_value))
        
        shaded_surface = surface.copy()
        shaded_surface.blit(shade_surface, (0, 0), special_flags=pygame.BLEND_MULT)
        
        return shaded_surface

    def blit_column_fast(self, screen_x, wall_top, column_surface):
        """OTIMIZAÇÃO: Blit rápido de coluna na tela"""
        if screen_x >= 0 and screen_x + config.COLUMN_WIDTH <= config.WIN_WIDTH:
            self.screen_buffer.blit(column_surface, (screen_x, wall_top))
        else:
            dest_rect = pygame.Rect(screen_x, wall_top, config.COLUMN_WIDTH, column_surface.get_height())
            screen_rect = pygame.Rect(0, 0, config.WIN_WIDTH, config.WIN_HEIGHT)
            
            if dest_rect.colliderect(screen_rect):
                clipped_rect = dest_rect.clip(screen_rect)
                source_rect = pygame.Rect(
                    clipped_rect.x - screen_x,
                    clipped_rect.y - wall_top,
                    clipped_rect.width,
                    clipped_rect.height
                )
                self.screen_buffer.blit(column_surface, clipped_rect, source_rect)

    def draw_solid_color_column(self, screen_x, wall_top, wall_bottom, wall_type, shade):
        """Desenhar coluna com cor sólida (fallback otimizado)"""
        base_colors = {
            1: config.BRICK_COLOR,
            2: config.STONE_COLOR,
            3: config.WOOD_COLOR,
        }
        
        base_color = base_colors.get(wall_type, config.DEFAULT_WALL_COLOR)
        
        color = (
            max(0, min(255, int(base_color[0] * shade))),
            max(0, min(255, int(base_color[1] * shade))),
            max(0, min(255, int(base_color[2] * shade)))
        )
        
        height = max(1, wall_bottom - wall_top)
        if height > 0 and screen_x >= 0 and screen_x < config.WIN_WIDTH:
            rect = pygame.Rect(screen_x, wall_top, config.COLUMN_WIDTH, height)
            self.screen_buffer.fill(color, rect)

    def draw_debug_info(self):
        """Desenhar informações de debug na tela"""
        debug_texts = [
            f"Pos: ({self.player.x:.2f}, {self.player.y:.2f})",
            f"Rot: {math.degrees(self.player.rot):.1f}°",
            f"Map: {self.get_map_cell(self.player.x, self.player.y)}",
            f"Rays: {config.NUM_RAYS}",
            f"Textures: {'ON' if config.ENABLE_TEXTURES else 'OFF'}",
            f"Column Width: {config.COLUMN_WIDTH}px",
            f"Cached Columns: {len(self.texture_column_cache)}"
        ]
        
        for i, text in enumerate(debug_texts):
            surface = self.debug_font.render(text, True, (255, 255, 255))
            self.screen_buffer.blit(surface, (10, 10 + i * 25))

    def get_map_cell(self, x, y):
        """Obter célula do mapa na posição"""
        map_x, map_y = int(x), int(y)
        if (0 <= map_y < len(self.map) and 0 <= map_x < len(self.map[0])):
            return self.map[map_y][map_x]
        return "OOB"
        
    def clear_texture_cache(self):
        """Limpar cache de texturas quando necessário"""
        if len(self.texture_column_cache) > self.max_column_cache * 0.9:
            cache_items = list(self.texture_column_cache.items())
            for i in range(len(cache_items) // 2):
                del self.texture_column_cache[cache_items[i][0]]
