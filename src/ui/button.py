import pygame

class Button:
    def __init__(self, x, y, width, height, text, callback, font_size=32):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback

        self.color_normal = (50, 50, 60)
        self.color_hover = (80, 80, 90)
        self.color_text = (255, 255, 255)
        self.color = self.color_normal

        self.font = pygame.font.Font(None, font_size)
        self.text_surface = self.font.render(self.text, True, self.color_text)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

        self.is_hovered = False


    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                self.callback()


    def update(self):
        self.color = self.color_hover if self.is_hovered else self.color_normal


    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=3)
        surface.blit(self.text_surface, self.text_rect)
