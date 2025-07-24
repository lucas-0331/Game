import pygame
import numpy as np
import math
from src import config
import random

class Renderer:
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.player = game.player
        self.texture_manager = game.texture_manager
        
        self.ray_angles = np.array([])
        self.distance_correction = np.array([])
        self.wall_buffer = np.array([])
        self.texture_column_cache = {}
        self.max_column_cache = 200

        self.floor_texture_high_res = self.create_procedural_wood_texture(size=(256, 256))
        
        self.floor_texture_med_res = pygame.transform.scale(self.floor_texture_high_res, (128, 128))
        self.floor_texture_low_res = pygame.transform.scale(self.floor_texture_high_res, (64, 64))

        self.tex_arrays = {
            'high': pygame.surfarray.array3d(self.floor_texture_high_res),
            'medium': pygame.surfarray.array3d(self.floor_texture_med_res),
            'low': pygame.surfarray.array3d(self.floor_texture_low_res)
        }
        self.tex_sizes = {
            'high': 256, 'medium': 128, 'low': 64
        }

        self.setup_optimizations()

    def create_procedural_wood_texture(self, size=(256, 256)):
        """Gera uma textura procedural de tábuas de madeira em alta resolução."""
        wood_color = (139, 90, 43); line_color = (87, 56, 26)
        plank_width = size[0] // 4 
        texture = pygame.Surface(size)
        texture.fill(wood_color)
        for x in range(0, size[0], plank_width):
            pygame.draw.line(texture, line_color, (x, 0), (x, size[1]), 2)
        for _ in range(int(size[0] * 40)): 
            x = random.randint(0, size[0] - 1); y = random.randint(0, size[1] - 1)
            r, g, b, _ = texture.get_at((x, y))
            grain_color = (max(0,r-random.randint(5,25)), max(0,g-random.randint(5,25)), max(0,b-random.randint(5,25)))
            texture.set_at((x, y), grain_color)
        return texture

    def setup_optimizations(self):
        self.texture_column_cache.clear()
        num_rays = config.WIN_WIDTH // config.COLUMN_WIDTH
        if num_rays == 0: num_rays = 1
        self.ray_angles = np.array([math.radians(i*config.FOV/num_rays - config.FOV/2) for i in range(num_rays)])
        self.distance_correction = np.cos(self.ray_angles)
        self.wall_buffer = np.full(num_rays, float('inf'))
        
    def render_game_world(self):
        pygame.draw.rect(self.screen, config.CEILING_COLOR, (0, 0, config.WIN_WIDTH, config.WIN_HEIGHT // 2))
        pygame.draw.rect(self.screen, config.FLOOR_COLOR, (0, config.WIN_HEIGHT // 2, config.WIN_WIDTH, config.WIN_HEIGHT // 2))
        self.draw_walls()

    def draw_walls(self):
        self.wall_buffer.fill(float('inf'))
        px, py, prot = self.player.x, self.player.y, self.player.rot
        for i, angle in enumerate(self.ray_angles):
            ray_angle = prot + angle
            dx, dy = math.cos(ray_angle), math.sin(ray_angle)
            distance, wall_type, hit_side, wall_x = self.improved_dda_with_texture(px, py, dx, dy, self.game.map)
            if 0 < distance < config.MAX_DEPTH:
                corrected_distance = distance * self.distance_correction[i]
                wall_height = config.WIN_HEIGHT / max(corrected_distance, 0.0001)
                
                if config.GRAPHICS_QUALITY == 'high':
                    if corrected_distance < 4:
                        tex_quality = 'high'
                    elif corrected_distance < 8:
                        tex_quality = 'medium'
                    else:
                        tex_quality = 'low'
                else: 
                    tex_quality = 'medium'

                wall_top = (config.WIN_HEIGHT / 2) - (wall_height / 2)
                base_shade = max(config.MIN_SHADE, 1.0 - (corrected_distance / config.FOG_DISTANCE))
                if hit_side == 1: base_shade *= config.SIDE_SHADE_FACTOR
                self.draw_fast_textured_column(i * config.COLUMN_WIDTH, wall_top, wall_height, wall_type, base_shade, wall_x, tex_quality)

    def draw_fast_textured_column(self, screen_x, wall_top, wall_height, wall_type, shade, wall_x, tex_quality):
        base_texture = self.texture_manager.get_wall_texture(wall_type)
        if not base_texture: return

        if tex_quality == 'high':
            texture = base_texture 
        else: 
            tex_size = self.tex_sizes[tex_quality]
            texture = pygame.transform.scale(base_texture, (tex_size, tex_size))

        tex_height = texture.get_height()
        tex_x = int(wall_x * texture.get_width()) % texture.get_width()
        tex_column = texture.subsurface(tex_x, 0, 1, tex_height)

        draw_start = max(wall_top, 0)
        draw_end = min(wall_top + wall_height, config.WIN_HEIGHT)
        if draw_start >= draw_end: return
        
        onscreen_height = draw_end - draw_start
        tex_y_start = (draw_start - wall_top) * (tex_height / wall_height)
        tex_y_height = onscreen_height * (tex_height / wall_height)
        
        try:
            texture_slice = tex_column.subsurface((0, tex_y_start, 1, tex_y_height))
            
            if config.GRAPHICS_QUALITY == 'high' and onscreen_height > 0:
                scaled_slice = pygame.transform.smoothscale(texture_slice, (config.COLUMN_WIDTH, int(onscreen_height)))
            elif onscreen_height > 0:
                scaled_slice = pygame.transform.scale(texture_slice, (config.COLUMN_WIDTH, int(onscreen_height)))
            else:
                return

            if shade < 1.0:
                scaled_slice = self.apply_shade_fast(scaled_slice, shade)
                
            self.screen.blit(scaled_slice, (screen_x, draw_start))
        except (ValueError, pygame.error):
            pass
            
    def improved_dda_with_texture(self, px, py, dx, dy, current_map):
        map_x, map_y = int(px), int(py)
        delta_dist_x = abs(1.0 / dx) if dx != 0 else 1e30
        delta_dist_y = abs(1.0 / dy) if dy != 0 else 1e30
        if dx < 0: step_x, side_dist_x = -1, (px - map_x) * delta_dist_x
        else: step_x, side_dist_x = 1, (map_x + 1.0 - px) * delta_dist_x
        if dy < 0: step_y, side_dist_y = -1, (py - map_y) * delta_dist_y
        else: step_y, side_dist_y = 1, (map_y + 1.0 - py) * delta_dist_y
        for _ in range(int(config.MAX_DEPTH * 2)):
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x; map_x += step_x; side = 0
            else:
                side_dist_y += delta_dist_y; map_y += step_y; side = 1
            if not (0 <= map_y < len(current_map) and 0 <= map_x < len(current_map[0])) or current_map[map_y][map_x] != 0: break
        if side == 0: perp_wall_dist = (map_x - px + (1 - step_x) / 2) / dx; wall_x = py + perp_wall_dist * dy
        else: perp_wall_dist = (map_y - py + (1 - step_y) / 2) / dy; wall_x = px + perp_wall_dist * dx
        wall_x -= math.floor(wall_x)
        wall_type = current_map[map_y][map_x] if 0 <= map_y < len(current_map) and 0 <= map_x < len(current_map[0]) else 1
        return abs(perp_wall_dist), wall_type, side, wall_x

    def apply_shade_fast(self, surface, shade):
        shade_value = int(255 * shade)
        shade_color = (shade_value, shade_value, shade_value)
        surface.fill(shade_color, special_flags=pygame.BLEND_RGB_MULT)
        return surface

