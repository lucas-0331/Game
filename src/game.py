import pygame
from pygame.locals import QUIT
import math
import numpy as np
from src import config
from src.player.player import Player
from src.maps.maps import Maps
from src.ui.button import Button
from src.renderer.texture_manager import TextureManager
from PIL import Image, ImageSequence

class Game:
    def __init__(self):
        self.maps = Maps()
        self.current_level = 1
        self.player = Player(self.current_level)
        self.map = self.maps.get_map(self.current_level)
        self.texture_manager = TextureManager()
        self.setup_optimizations()

        self.floor_texture = pygame.image.load('assets/textures/floor.png')
        self.floor_tex_array = pygame.surfarray.array3d(self.floor_texture)

        self.tex_size = self.floor_texture.get_width()

        self.loading_frames = []
        self.loading_frame_index = 0.9
        self.loading_animation_speed = 0.1 
        self.last_frame_update = 0 

        self.game_state = 'main_menu' 
        self.resolutions = [(1280, 720), (1600, 900), (1920, 1080)]

        self.main_menu_buttons = []
        self.options_menu_buttons = []
        self.pause_menu_buttons = []

        self.title_font = pygame.font.Font(None, 80)
        self.options_font = pygame.font.Font(None, 40)
        
        self.prompt_font = pygame.font.Font(None, 36)

        self.credits_text = [
            "CRÉDITOS",
            "",
            "Desenvolvimento:",
            "Lucas Costa",
            "",
            "Agradecimentos:",
            "Professor Ricardo Martins",
            "id Software",
            "Pixel Art Village",
            "Pixel Art",
            "Iliad",
            "Fumito Ueda",
            "Shinji Mikami",
            "Hideo Kojima",
            "John Romero",
            "Gemini",
            "",
            "Projeto da matéria de Tópicos Especiais",
            "Curso de Ciência da Computação",
            "7º Período - 2025",
            "IFSULDEMINAS - Campus Muzambinho",
            "",
            "Obrigado por Jogar!",
        ]
        self.credits_scroll_y = config.WIN_HEIGHT  
        self.credits_scroll_speed = 1.7
        self.credits_font = pygame.font.Font(None, 48)
        self.credits_title_font = pygame.font.Font(None, 72)
        self.credits_timer = 0 
        self.credits_duration = 15000

        self.create_all_menus()

        self.setup_optimizations()


    def load_gif_frames(self, gif_path):
        self.loading_frames = []
        try:
            with Image.open(gif_path) as gif:
                for frame in ImageSequence.Iterator(gif):
                    frame = frame.convert('RGBA')
                    pygame_frame = pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode).convert_alpha()
                    self.loading_frames.append(pygame_frame)
        except FileNotFoundError:
            print(f"Erro: Arquivo GIF não encontrado em '{gif_path}'")
            fallback_surface = pygame.Surface((100, 100))
            fallback_surface.fill((255, 0, 255))
            self.loading_frames.append(fallback_surface)
            

    def start_credits(self):
        self.game_state = 'credits'
        self.credits_scroll_y = config.WIN_HEIGHT
        self.credits_timer = pygame.time.get_ticks()


    def update_credits(self):
        if self.game_state == 'credits':
            self.credits_scroll_y -= self.credits_scroll_speed
            if pygame.time.get_ticks() - self.credits_timer > self.credits_duration:
                self.return_to_main_menu() 


    def draw_credits(self):
        config.DISPLAY.fill((0, 0, 0))
        y = int(self.credits_scroll_y)

        for line in self.credits_text:
            text_surface = self.credits_font.render(line, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(config.WIN_WIDTH // 2, y))
            config.DISPLAY.blit(text_surface, text_rect)
            y += 60 

        if y < -len(self.credits_text) * 60: 
            pass


    def start_next_level(self):
        self.loading_frames.clear()

        self.current_level += 1 

        next_map = self.maps.get_map(self.current_level)
        if next_map is None:
            print('Zerado')
            self.start_credits()
            return
        
        self.map = next_map
        self.player = Player(self.current_level)

        self.texture_manager.clear_cache()
        if hasattr(self, 'texture_column_cache'):
            self.texture_column_cache.clear()

        self.game_state = 'playing'


    def create_all_menus(self):
        self.create_main_menu()
        self.create_options_menu()
        self.create_pause_menu()


    def start_game(self):
        self.game_state = 'playing' 
        self.player = Player(self.current_level)
        self.texture_manager.clear_cache()


    def open_options(self):
        self.game_state = 'options_menu' 
        

    def return_to_main_menu(self):
        self.game_state = 'main_menu' 


    def resume_game(self):
        self.game_state = 'playing'


    def change_resolution(self, width, height):
        config.WIN_WIDTH = width
        config.WIN_HEIGHT = height

        config.DISPLAY = pygame.display.set_mode((config.WIN_WIDTH, config.WIN_HEIGHT))
        
        self.create_all_menus()

        self.game_state = 'options_menu' 


    def quit_game(self):
        config.RUNNING = False


    def create_main_menu(self):
        self.main_menu_buttons.clear()
        cx = config.WIN_WIDTH // 2
        cy = config.WIN_HEIGHT // 2 

        self.main_menu_buttons.append(Button(cx - 150, cy - 50, 300, 50, 'Iniciar Jogo', self.start_game))
        self.main_menu_buttons.append(Button(cx - 150, cy + 20, 300, 50, 'Opções', self.open_options))
        self.main_menu_buttons.append(Button(cx - 150, cy + 90, 300, 50, 'Sair', self.quit_game))

    
    def create_options_menu(self):
        self.options_menu_buttons.clear()
        cx = config.WIN_WIDTH // 2 
        cy = config.WIN_HEIGHT // 2 - 100 

        for i, (w, h) in enumerate(self.resolutions):
            text = f"{w} x {h}"
            callback = lambda width=w, height=h: self.change_resolution(width, height)
            self.options_menu_buttons.append(Button(cx - 150, cy + i * 70, 300, 50, text, callback))

            self.options_menu_buttons.append(Button(cx - 150, cy + len(self.resolutions) * 70 + 20, 300, 50, 'Voltar', self.return_to_main_menu))


    def create_pause_menu(self):
        self.pause_menu_buttons.clear()
        cx = config.WIN_WIDTH // 2 
        cy = config.WIN_HEIGHT // 2

        self.pause_menu_buttons.append(Button(cx - 150, cy - 50, 300, 50, 'Continuar', self.resume_game))
        self.pause_menu_buttons.append(Button(cx - 150, cy + 20, 300, 50, 'Opções', self.open_options))
        self.pause_menu_buttons.append(Button(cx - 150, cy + 90, 300, 50, 'Sair para o Menu', self.return_to_main_menu))


    def setup_optimizations(self):
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
            events = pygame.event.get()

            if self.game_state == 'main_menu':
                self.handle_menu_events(events, self.main_menu_buttons)
                self.draw_main_menu()
            elif self.game_state == 'options_menu':
                self.handle_menu_events(events, self.options_menu_buttons)
                self.draw_options_menu()
            elif self.game_state == 'paused':
                self.handle_menu_events(events, self.pause_menu_buttons)
                self.draw_pause_menu()
            elif self.game_state == 'playing':
                self.handle_playing_events(events)
                self.update()
                self.draw() 
            elif self.game_state == 'level_transition':
                self.draw_loading_screen()
                if pygame.time.get_ticks() - self.transition_start_time > 3000:
                    self.start_next_level()
            elif self.game_state == 'credits':
                self.update_credits()
                self.draw_credits()

            fps_text = f"FPS: {int(config.CLOCK.get_fps())} | Pos: ({self.player.x:.2f}, {self.player.y:.2f}) | Rot: {math.degrees(self.player.rot):.1f}°"
            pygame.display.set_caption(fps_text)
            pygame.display.flip()
            
        pygame.quit()


    def handle_menu_events(self, events, buttons):
        for event in events:
            if event.type == QUIT:
                config.RUNNING = False
            for button in buttons:
                button.handle_event(event)


    def handle_playing_events(self, events):
        for event in events:
            if event.type == QUIT:
                config.RUNNING = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game_state = 'paused' 
                self.pause_background = config.DISPLAY.copy()


    def draw_main_menu(self):
        config.DISPLAY.fill((20, 20, 30)) 
        
        title_surface = self.title_font.render('Labirintity', True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(config.WIN_WIDTH // 2, 150))
        config.DISPLAY.blit(title_surface, title_rect)
        
        for button in self.main_menu_buttons:
            button.update()
            button.draw(config.DISPLAY)
            

    def draw_options_menu(self):
        config.DISPLAY.fill((20, 20, 30))
        
        title_surface = self.title_font.render('Opções de Resolução', True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(config.WIN_WIDTH // 2, 100))
        config.DISPLAY.blit(title_surface, title_rect)

        current_res_text = f"Atual: {config.WIN_WIDTH} x {config.WIN_HEIGHT}"
        current_res_surface = self.options_font.render(current_res_text, True, (200, 200, 200))
        current_res_rect = current_res_surface.get_rect(center=(config.WIN_WIDTH // 2, 180))
        config.DISPLAY.blit(current_res_surface, current_res_rect)
        
        for button in self.options_menu_buttons:
            button.update()
            button.draw(config.DISPLAY)


    def draw_pause_menu(self):
        config.DISPLAY.blit(self.pause_background, (0, 0))
        
        overlay = pygame.Surface((config.WIN_WIDTH, config.WIN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150)) 
        config.DISPLAY.blit(overlay, (0, 0))
        
        title_surface = self.title_font.render('Pausado', True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(config.WIN_WIDTH // 2, 150))
        config.DISPLAY.blit(title_surface, title_rect)
        
        for button in self.pause_menu_buttons:
            button.update()
            button.draw(config.DISPLAY)


    def draw_loading_screen(self):
        config.DISPLAY.fill((0, 0, 0))

        if not self.loading_frames:
            return 

        current_time = pygame.time.get_ticks()
        if current_time - self.last_frame_update > self.loading_animation_speed * 1000:
            self.loading_frame_index = (self.loading_frame_index + 1) % len(self.loading_frames)
            self.last_frame_update = current_time

        current_frame = self.loading_frames[self.loading_frame_index]
        if current_frame:
            scaled_frame = pygame.transform.scale(current_frame, (config.WIN_WIDTH, config.WIN_HEIGHT))

            config.DISPLAY.blit(scaled_frame, (0, 0))


    def draw_floor(self):
        px, py, prot = self.player.x, self.player.y, self.player.rot
        
        ray_dir0_x = px + math.cos(prot - config.FOV / 200)
        ray_dir0_y = py + math.sin(prot - config.FOV / 200)
        ray_dir1_x = px + math.cos(prot + config.FOV / 200)
        ray_dir1_y = py + math.sin(prot + config.FOV / 200)

        for y in range(config.WIN_HEIGHT // 2, config.WIN_HEIGHT):
            p = y - config.WIN_HEIGHT // 2
            if p == 0: continue 
            
            row_distance = (0.5 * config.WIN_HEIGHT) / p
            
            step_x = row_distance * (ray_dir1_x - ray_dir0_x) / config.WIN_WIDTH
            step_y = row_distance * (ray_dir1_y - ray_dir0_y) / config.WIN_WIDTH

            floor_x = px + row_distance * ray_dir0_x
            floor_y = py + row_distance * ray_dir0_y
            
            shade = min(1.0, 1.0 - row_distance / config.FOG_DISTANCE)

            for x in range(config.WIN_WIDTH):
                tex_x = int(floor_x * self.tex_size) % self.tex_size
                tex_y = int(floor_y * self.tex_size) % self.tex_size

                floor_color = self.floor_tex_array[tex_x, tex_y]

                floor_color = (floor_color[0] * shade, floor_color[1] * shade, floor_color[2] * shade)
                
                self.screen_buffer.set_at((x, y), floor_color)

                floor_x += step_x
                floor_y += step_y

        
    def update(self):
        player_status = self.player.update()
        
        if player_status == 'goal_reached':
            print("Objetivo alcançado! Iniciando transição...")
            
            self.game_state = 'level_transition'
            self.transition_start_time = pygame.time.get_ticks()
            
            self.load_gif_frames('assets/loading/door.gif')
            self.loading_frame_index = 0


    def draw(self):
        self.screen_buffer.fill((0, 0, 0))
        self.draw_simple_background()
        self.optimized_textured_raycasting()
        self.draw_debug_info()

        if self.player.interaction_target is not None:
            prompt_text = f"Pressione T para interagir"
            text_surface = self.prompt_font.render(prompt_text, True, (255, 255, 255))

            text_rect = text_surface.get_rect(center=(config.WIN_WIDTH / 2, config.WIN_HEIGHT - 50))
            bg_rect = text_rect.inflate(20, 10)
            bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 150))

            self.screen_buffer.blit(bg_surface, bg_rect)
            self.screen_buffer.blit(text_surface, text_rect)

        config.DISPLAY.blit(self.screen_buffer, (0, 0))


    def draw_simple_background(self):
        # Céu
        pygame.draw.rect(self.screen_buffer, config.CEILING_COLOR, 
                        (0, 0, config.WIN_WIDTH, config.WIN_HEIGHT // 2))
        pygame.draw.rect(self.screen_buffer, config.FLOOR_COLOR,
                        (0, config.WIN_HEIGHT // 2, config.WIN_WIDTH, config.WIN_HEIGHT // 2))


    def optimized_textured_raycasting(self):
        self.wall_buffer.fill(float('inf'))
        
        px, py, prot = self.player.x, self.player.y, self.player.rot
        
        for i in range(config.NUM_RAYS):
            ray_angle = prot + self.ray_angles[i]
            
            dx = math.cos(ray_angle)
            dy = math.sin(ray_angle)
            
            distance, wall_type, hit_side, wall_x = self.improved_dda_with_texture(px, py, dx, dy)
            
            if distance > 0 and distance < config.MAX_DEPTH:
                corrected_distance = distance * self.distance_correction[i]
                
                wall_height = config.WIN_HEIGHT / max(corrected_distance, 0.0001) 

                wall_top = (config.WIN_HEIGHT / 2) - (wall_height / 2)
                wall_bottom = wall_top + wall_height  
                
                base_shade = max(config.MIN_SHADE, 1.0 - (distance / config.FOG_DISTANCE))
                if hit_side == 1:  
                    base_shade *= config.SIDE_SHADE_FACTOR
                
                self.draw_optimized_textured_column(
                    screen_x=i * config.COLUMN_WIDTH,
                    wall_top=int(wall_top),
                    wall_bottom=int(wall_bottom),
                    wall_type=wall_type,
                    shade=base_shade,
                    wall_x=wall_x,
                )
                self.wall_buffer[i] = corrected_distance


    def improved_dda_with_texture(self, px, py, dx, dy):
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


    def draw_optimized_textured_column(self, screen_x, wall_top, wall_bottom, wall_type, shade, wall_x):
        wall_height = wall_bottom - wall_top

        if wall_height <=0 or screen_x < 0 or screen_x >= config.WIN_WIDTH:
            return

        texture = self.texture_manager.get_wall_texture(wall_type)

        if config.ENABLE_TEXTURES and texture:
            self.draw_fast_textured_column(screen_x, wall_top, wall_height, texture, wall_x, shade)
        else:
            self.draw_solid_color_column(screen_x, wall_top, wall_bottom, wall_type, shade)


    def draw_fast_textured_column(self, screen_x, wall_top, wall_height, texture, wall_x, shade):
        tex_width, tex_height = texture.get_size()

        if wall_height <= 0:
            return

        cache_key = (id(texture), int(wall_x * tex_width), int(wall_height), int(shade * 100))

        if cache_key in self.texture_column_cache:
            cached_column = self.texture_column_cache[cache_key]
            self.screen_buffer.blit(cached_column, (screen_x, wall_top))
            return
        
        tex_x = int(wall_x * tex_width) % tex_width
        
        tex_column_rect = pygame.Rect(tex_x, 0, 1, tex_height)

        try:
            tex_column = texture.subsurface(tex_column_rect)

            scaled_column = pygame.transform.scale(tex_column, (config.COLUMN_WIDTH, int(wall_height)))

            if shade < 1.0:
                scaled_column = self.apply_shade_fast(scaled_column, shade)

            if len(self.texture_column_cache) < self.max_column_cache:
                self.texture_column_cache[cache_key] = scaled_column

            self.screen_buffer.blit(scaled_column, (screen_x, wall_top))

        except (ValueError, pygame.error):
            self.draw_solid_color_column(screen_x, wall_top, int(wall_top + wall_height), 1, shade)

            
    def apply_shade_fast(self, surface, shade):
        shade_value = int(255 * shade)

        shade_color = (shade_value, shade_value, shade_value)

        surface.fill(shade_color, special_flags=pygame.BLEND_RGB_MULT)
        
        return surface


    def blit_column_fast(self, screen_x, wall_top, column_surface):
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
        map_x, map_y = int(x), int(y)
        if (0 <= map_y < len(self.map) and 0 <= map_x < len(self.map[0])):
            return self.map[map_y][map_x]
        return "OOB"


    def clear_texture_cache(self):
        if len(self.texture_column_cache) > self.max_column_cache * 0.9:
            cache_items = list(self.texture_column_cache.items())
            for i in range(len(cache_items) // 2):
                del self.texture_column_cache[cache_items[i][0]]
