import pygame
import os
import math
from src import config

class TextureManager:
    def __init__(self):
        self.textures = {}
        self.scaled_cache = {}  # Cache para texturas redimensionadas
        self.max_cache_size = 50  # Limitar cache
        self.load_textures()
    
    def load_textures(self):
        """Carrega texturas otimizadas"""
        # Texturas padrão menores para melhor performance
        default_textures = {
            1: self.create_optimized_brick_texture(),
            2: self.create_optimized_stone_texture(),
            3: self.create_optimized_wood_texture()
        }
        
        # Tentar carregar texturas do disco
        assets_path = "assets/textures/"
        try:
            if os.path.exists(assets_path):
                for filename in os.listdir(assets_path):
                    if filename.lower().endswith(('.png', '.jpg', '.bmp')):
                        path = os.path.join(assets_path, filename)
                        try:
                            tex_id = int(filename.split('.')[0])
                            # Carregar e redimensionar para performance
                            original = pygame.image.load(path)
                            optimized_size = (32, 32)  # Textura menor
                            self.textures[tex_id] = pygame.transform.scale(original, optimized_size)
                        except (ValueError, pygame.error):
                            continue
        except OSError:
            pass
        
        # Usar texturas padrão para IDs não carregados
        for tex_id, texture in default_textures.items():
            if tex_id not in self.textures:
                self.textures[tex_id] = texture
    
    def create_optimized_brick_texture(self):
        """Textura de tijolo otimizada (menor e mais simples)"""
        texture = pygame.Surface((32, 32))  # Reduzido de 64x64
        texture.fill((120, 80, 60))
        
        # Padrão mais simples
        for y in range(0, 32, 8):
            pygame.draw.line(texture, (80, 50, 30), (0, y), (32, y), 1)
        for x in range(0, 32, 16):
            pygame.draw.line(texture, (80, 50, 30), (x, 0), (x, 16), 1)
            pygame.draw.line(texture, (80, 50, 30), (x + 8, 16), (x + 8, 32), 1)
        
        return texture
    
    def create_optimized_stone_texture(self):
        """Textura de pedra otimizada"""
        texture = pygame.Surface((32, 32))
        texture.fill((100, 100, 120))
        
        # Padrão mais simples
        for x in range(0, 32, 4):
            for y in range(0, 32, 4):
                variation = (x + y) % 20 - 10
                color = (max(80, 100 + variation), 
                        max(80, 100 + variation), 
                        max(100, 120 + variation//2))
                pygame.draw.rect(texture, color, (x, y, 4, 4))
        
        return texture
    
    def create_optimized_wood_texture(self):
        """Textura de madeira otimizada"""
        texture = pygame.Surface((32, 32))
        texture.fill((160, 100, 60))
        
        # Grãos mais simples
        for y in range(0, 32, 2):
            variation = int(10 * math.sin(y * 0.5))
            color = (max(140, 140 + variation), 
                    max(70, 80 + variation//2), 
                    max(40, 40 + variation//3))
            pygame.draw.line(texture, color, (0, y), (32, y), 1)
        
        return texture
    
    def get_wall_texture(self, wall_type):
        """Retorna textura para tipo de parede"""
        if not config.ENABLE_TEXTURES:
            return None
            
        return self.textures.get(wall_type, self.textures.get(1))
    
    def get_scaled_texture(self, wall_type, size):
        """Obtém textura redimensionada com cache"""
        if not config.ENABLE_TEXTURES:
            return None
            
        cache_key = (wall_type, size)
        
        if cache_key in self.scaled_cache:
            return self.scaled_cache[cache_key]
        
        base_texture = self.get_wall_texture(wall_type)
        if base_texture and len(self.scaled_cache) < self.max_cache_size:
            try:
                scaled = pygame.transform.scale(base_texture, size)
                self.scaled_cache[cache_key] = scaled
                return scaled
            except pygame.error:
                return base_texture
        
        return base_texture
    
    def clear_cache(self):
        """Limpa cache de texturas"""
        self.scaled_cache.clear()

