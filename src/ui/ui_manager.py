import pygame
from src import config
from src.ui.button import Button
from PIL import Image, ImageSequence

class UIManager:
    def __init__(self, game_controller):
        self.game = game_controller
        
        self.title_font = pygame.font.Font(None, 80)
        self.options_font = pygame.font.Font(None, 40)
        self.prompt_font = pygame.font.Font(None, 36)
        self.instructions_font = pygame.font.Font(None, 32)
        self.credits_font = pygame.font.Font(None, 48)
        self.credits_title_font = pygame.font.Font(None, 72)
        self.hud_font = pygame.font.Font(None, 40)

        self.buttons = {
            'main_menu': [], 'options_main': [], 'options_resolution': [],
            'options_graphics': [], 'paused': [], 'how_to_play': []
        }
        self.pause_background = None
        
        self.loading_frames = []
        self.loading_frame_index = 0
        self.loading_animation_speed = 0.1
        self.last_frame_update = 0
        self.gif_animation_finished = False

        self.credits_text = [
            "CRÉDITOS",
            "",
            "Desenvolvido por:",
            "Lucas Costa",
            "",
            "---------------------------",
            "UM JOGO DE LUCAS COSTA",
            "---------------------------",
            "",
            "CRIADO POR",
            "LUCAS COSTA",
            "",
            "GAME DESIGN",
            "LUCAS COSTA",
            "",
            "PROGRAMAÇÃO DA ENGINE",
            "LUCAS COSTA",
            "",
            "LEVEL DESIGN",
            "LUCAS COSTA",
            "",
            "UI / UX DESIGN",
            "LUCAS COSTA",
            "",
            "DEPURAÇÃO E TESTES",
            "LUCAS COSTA",
            "",
            "ENGENHARIA DE PROMPT COM IA",
            "LUCAS COSTA",
            "",
            "---------------------------",
            "",
            "Agradecimentos Especiais:",
            "Professor Ricardo Martins",
            "id Software",
            "John Romero",
            "Pixel Art Village",
            "Fumito Ueda",
            "Shinji Mikami",
            "Hideo Kojima",
            "Gemini",
            "",
            "Projeto da matéria de Tópicos Especiais I",
            "Curso de Ciência da Computação - 7º Período",
            "IFSULDEMINAS - Campus Muzambinho",
            "24 de Julho de 2025",
            "",
            "Obrigado por Jogar!",
        ]

        self.credits_scroll_y = config.WIN_HEIGHT
        self.credits_scroll_speed = 1.99
        self.credits_total_height = len(self.credits_text) * 60 

        self.create_all_menus()

    def update(self):
        if self.game.get_current_state() == 'credits':
            self.credits_scroll_y -= self.credits_scroll_speed
            final_y_pos = self.credits_scroll_y + self.credits_total_height
            if final_y_pos < 0: 
                self.game.change_state('main_menu')

    def draw_loading_screen(self, screen):
        screen.fill((0, 0, 0))
        if not self.loading_frames: return
        
        current_time = pygame.time.get_ticks()
        if current_time - self.last_frame_update > self.loading_animation_speed * 1000:
            self.last_frame_update = current_time
            if not self.gif_animation_finished:
                self.loading_frame_index += 1
                if self.loading_frame_index >= len(self.loading_frames):
                    self.loading_frame_index = len(self.loading_frames) - 1
                    self.gif_animation_finished = True

        current_frame = self.loading_frames[self.loading_frame_index]
        scaled_frame = pygame.transform.scale(current_frame, (config.WIN_WIDTH, config.WIN_HEIGHT))
        screen.blit(scaled_frame, (0, 0))

    def _draw_prompt(self, screen, text):
        text_surface = self.prompt_font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(config.WIN_WIDTH / 2, config.WIN_HEIGHT - 50))
        bg_rect = text_rect.inflate(20, 10)
        bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 150))
        screen.blit(bg_surface, bg_rect)
        screen.blit(text_surface, text_rect)

    def draw_game_hud(self, screen):
        marks_used = 5 - self.game.player.marks_left
        hud_text = f"Marcações: {marks_used} / 5"
        text_surface = self.hud_font.render(hud_text, True, (255, 255, 255))
        screen.blit(text_surface, (20, config.WIN_HEIGHT - 40))

        target = self.game.player.interaction_target
        
        if self.game.player.prompt_timer > 0:
            self._draw_prompt(screen, "Você não tem mais marcações")
        elif target:
            if target['type'] == 9:
                self._draw_prompt(screen, "Pressione E para interagir")
            elif 0 < target['type'] < 10:
                self._draw_prompt(screen, "Pressione F para marcar a parede")
            elif target['type'] > 10 and target['type'] % 11 == 0:
                self._draw_prompt(screen, "Pressione F para remover a marcação")

    def handle_events(self, events, state):
        buttons_to_check = self.buttons.get(state, [])
        for event in events:
            if event.type == pygame.QUIT: self.game.quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if state in ['paused', 'options_main', 'options_resolution', 'options_graphics', 'how_to_play']: 
                        self.game.pop_state()
                    elif state == 'main_menu': self.game.quit_game()
            for button in buttons_to_check: button.handle_event(event)

    def draw(self, screen, state):
        draw_functions = {
            'main_menu': self.draw_main_menu, 
            'options_main': self.draw_options_main,
            'options_resolution': self.draw_options_resolution, 
            'options_graphics': self.draw_options_graphics,
            'paused': self.draw_pause_menu, 
            'level_transition': self.draw_loading_screen,
            'credits': self.draw_credits,
            'how_to_play': self.draw_how_to_play_menu # Novo
        }

        if state in draw_functions:
            draw_functions[state](screen)

        if state == 'playing':
            self.draw_game_hud(screen)

    def draw_how_to_play_menu(self, screen):
        screen.fill((20, 20, 30))
        title_surface = self.title_font.render('Como Jogar', True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(config.WIN_WIDTH // 2, 100))
        screen.blit(title_surface, title_rect)

        instructions = [
            "Objetivo:",
            "  Você está preso em uma série de labirintos. Encontre a porta de saída",
            "  em cada nível para escapar. Use sua perspicácia e as ferramentas",
            "  disponíveis para não se perder.",
            "",
            "Marcações de Parede:",
            "  Você pode marcar as paredes para saber por onde já passou. Isso",
            "  ajuda a evitar andar em círculos. Você tem um número limitado de",
            "  marcações, mas pode removê-las para usá-las em outro lugar.",
            "",
            "Comandos:",
            "  - W: Mover para frente",
            "  - S: Mover para trás",
            "  - A / D: Girar a visão para esquerda / direita",
            "  - E: Interagir com a porta de saída",
            "  - F: Marcar uma parede / Remover uma marcação",
            "  - ESC: Pausar o jogo / Voltar nos menus"
        ]
        
        start_y = 200
        for i, line in enumerate(instructions):
            line_surface = self.instructions_font.render(line, True, (220, 220, 220))
            screen.blit(line_surface, (config.WIN_WIDTH / 2 - 400, start_y + i * 35))

        for button in self.buttons['how_to_play']:
            button.update()
            button.draw(screen)


    def create_all_menus(self):
        for key in self.buttons:
            self.buttons[key].clear()

        cx, cy = config.WIN_WIDTH // 2, config.WIN_HEIGHT // 2

        self.buttons['main_menu'].extend([
            Button(cx - 150, cy - 80, 300, 50, 'Iniciar Jogo', self.game.start_game),
            Button(cx - 150, cy - 10, 300, 50, 'Como Jogar', lambda: self.game.push_state('how_to_play')),
            Button(cx - 150, cy + 60, 300, 50, 'Opções', lambda: self.game.push_state('options_main')),
            Button(cx - 150, cy + 130, 300, 50, 'Sair', self.game.quit_game)
        ])
        
        self.buttons['how_to_play'].append(
            Button(cx - 150, config.WIN_HEIGHT - 100, 300, 50, 'Voltar', self.game.pop_state)
        )

        fullscreen_text = f"Tela Cheia: {'Sim' if config.FULLSCREEN else 'Não'}"
        self.buttons['options_main'].extend([Button(cx-150, cy-100, 300, 50, 'Resolução', lambda: self.game.push_state('options_resolution')), Button(cx-150, cy-30, 300, 50, 'Gráficos', lambda: self.game.push_state('options_graphics')), Button(cx-150, cy+40, 300, 50, fullscreen_text, self.game.toggle_fullscreen), Button(cx-150, cy+110, 300, 50, 'Voltar', self.game.pop_state)])
        resolutions = [(1280, 720), (1600, 900), (1920, 1080)]
        for i, (w, h) in enumerate(resolutions):
            self.buttons['options_resolution'].append(Button(cx-150, cy-100+i*70, 300, 50, f"{w}x{h}", lambda w=w,h=h:self.game.change_resolution(w,h)))
        self.buttons['options_resolution'].append(Button(cx-150, cy-100+len(resolutions)*70, 300, 50, 'Voltar', self.game.pop_state))
        qualities = ['low', 'medium', 'high']
        for i, quality in enumerate(qualities):
            self.buttons['options_graphics'].append(Button(cx-150, cy-100+i*70, 300, 50, f"Qualidade: {quality.capitalize()}", lambda q=quality:self.game.set_graphics_quality(q)))
        self.buttons['options_graphics'].append(Button(cx-150, cy-100+len(qualities)*70, 300, 50, 'Voltar', self.game.pop_state))
        self.buttons['paused'].extend([Button(cx-150, cy-50, 300, 50, 'Continuar', self.game.resume_game), Button(cx-150, cy+20, 300, 50, 'Opções', lambda: self.game.push_state('options_main')), Button(cx-150, cy+90, 300, 50, 'Sair para o Menu', lambda: self.game.change_state('main_menu'))])

    def draw_menu(self, screen, title, button_key):
        screen.fill((20, 20, 30))
        title_surface = self.title_font.render(title, True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(config.WIN_WIDTH // 2, 150))
        screen.blit(title_surface, title_rect)

        for button in self.buttons[button_key]:
            button.update()
            button.draw(screen)

    def draw_main_menu(self, screen):
        self.draw_menu(screen, 'Labirintity', 'main_menu')

    def draw_options_main(self, screen):
        self.draw_menu(screen, 'Opções', 'options_main')

    def draw_options_resolution(self, screen):
        self.draw_menu(screen, 'Resolução', 'options_resolution')

    def draw_options_graphics(self, screen):
        self.draw_menu(screen, 'Gráficos', 'options_graphics')

    def draw_pause_menu(self, screen):
        if self.pause_background: 
            screen.blit(self.pause_background, (0, 0))

        overlay = pygame.Surface((config.WIN_WIDTH, config.WIN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        title_surface = self.title_font.render('Pausado', True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(config.WIN_WIDTH // 2, 150))
        screen.blit(title_surface, title_rect)

        for button in self.buttons['paused']:
            button.update(); button.draw(screen)

    def draw_credits(self, screen):
        screen.fill((0, 0, 0)); y = int(self.credits_scroll_y)
        for i, line in enumerate(self.credits_text):
            font = self.credits_title_font if i == 0 else self.credits_font
            color = (255, 255, 0) if i == 0 else (255, 255, 255)
            text_surface = font.render(line, True, color)
            text_rect = text_surface.get_rect(center=(config.WIN_WIDTH // 2, y + i * 60))
            screen.blit(text_surface, text_rect)

    def load_gif_frames(self, gif_path):
        self.loading_frames.clear()
        try:
            with Image.open(gif_path) as gif:
                for frame in ImageSequence.Iterator(gif):
                    frame = frame.convert('RGBA')
                    pygame_frame = pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode).convert_alpha()
                    self.loading_frames.append(pygame_frame)
        except FileNotFoundError: print(f"Erro: Arquivo GIF não encontrado em '{gif_path}'")

