import pygame
from src import config
from src.player.player import Player
from src.maps.maps import Maps
from src.renderer.renderer import Renderer
from src.renderer.texture_manager import TextureManager
from src.ui.ui_manager import UIManager

class Game:
    def __init__(self):
        self.maps = Maps()
        self.texture_manager = TextureManager()
        self.running = True

        self.current_level = 1
        self.map = self.maps.get_map(self.current_level)
        if self.map is None: raise ValueError(f"Mapa para o nível {self.current_level} não encontrado!")
        self.player = Player(self.current_level)
        
        self.renderer = Renderer(config.DISPLAY, self)
        self.ui_manager = UIManager(self)

        self.state_stack = ['main_menu']
        self.transition_start_time = 0 
        self.credits_timer = 0 
        self.credits_duration = 15000

    def get_current_state(self):
        return self.state_stack[-1] if self.state_stack else None

    def run(self):
        while self.running:
            config.CLOCK.tick(config.FPS)
            events = pygame.event.get()
            current_state = self.get_current_state()
            self.update_states(events, current_state)

            if current_state == 'playing':
                self.renderer.render_game_world()
            
            self.ui_manager.draw(config.DISPLAY, current_state)

            # pygame.display.set_caption(f"FPS: {int(config.CLOCK.get_fps())}")
            pygame.display.set_caption('Labirintity')
            pygame.display.flip()
        pygame.quit()

    def update_states(self, events, state):
        if state in ['main_menu', 'options_main', 'options_resolution', 'options_graphics', 'paused']:
            self.ui_manager.handle_events(events, state)
        elif state == 'playing':
            self.handle_playing_events(events)
            player_status = self.player.update()
            if player_status == 'goal_reached':
                self.start_level_transition()
        elif state == 'level_transition':
            if self.ui_manager.gif_animation_finished:
                self.start_next_level()
        elif state == 'credits':
            self.ui_manager.update()
            for event in events:
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    self.pop_state()
    
    def handle_playing_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.quit_game()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.ui_manager.pause_background = config.DISPLAY.copy()
                self.push_state('paused')
    
    def start_level_transition(self):
        self.change_state('level_transition')
        self.ui_manager.load_gif_frames('assets/loading/door.gif')
        self.ui_manager.loading_frame_index = 0
        self.ui_manager.gif_animation_finished = False

    def push_state(self, state): self.state_stack.append(state)
    def pop_state(self):
        if len(self.state_stack) > 1: self.state_stack.pop()
    def change_state(self, state): self.state_stack = [state]

    def start_game(self):
        self.current_level = 1; self.reset_level(); self.change_state('playing')

    def start_next_level(self):
        self.current_level += 1
        if not self.maps.get_map(self.current_level):
            self.change_state('credits')
            self.ui_manager.credits_scroll_y = config.WIN_HEIGHT
            return
        self.reset_level(); self.change_state('playing')

    def reset_level(self):
        self.map = self.maps.get_map(self.current_level)
        self.player = Player(self.current_level)
        self.renderer.player = self.player
        self.renderer.texture_column_cache.clear()

    def toggle_fullscreen(self):
        config.FULLSCREEN = not config.FULLSCREEN
        self.change_resolution(config.WIN_WIDTH, config.WIN_HEIGHT)

    def change_resolution(self, w, h):
        config.WIN_WIDTH, config.WIN_HEIGHT = w, h
        flags = pygame.FULLSCREEN if config.FULLSCREEN else 0
        config.DISPLAY = pygame.display.set_mode((w, h), flags)
        self.renderer.setup_optimizations()
        self.ui_manager.create_all_menus()

    def set_graphics_quality(self, quality):
        config.GRAPHICS_QUALITY = quality
        if quality == 'low': config.COLUMN_WIDTH = 8; config.FOG_DISTANCE = 8
        elif quality == 'medium': config.COLUMN_WIDTH = 4; config.FOG_DISTANCE = 12
        elif quality == 'high': config.COLUMN_WIDTH = 1; config.FOG_DISTANCE = 24
        self.renderer.setup_optimizations()
        self.ui_manager.create_all_menus()

    def resume_game(self): self.pop_state()
    def quit_game(self): self.running = False
    def return_to_main_menu(self): self.change_state('main_menu')

