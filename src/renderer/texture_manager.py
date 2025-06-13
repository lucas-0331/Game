import pygame
import os
import math
from src import config

class TextureManager:
    def __init__(self):
        self.textures = {}
        self.scaled_cache = {}  # Cache para texturas redimensionadas
        self.max_cache_size = config.MAX_TEXTURE_CACHE_SIZE
        self.cache_access_count = 0
        self.load_textures()
    
    def load_textures(self):
        """Carrega texturas otimizadas"""
        # Texturas padrão usando variáveis configuráveis
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
                            # Carregar e redimensionar usando tamanho configurável
                            original = pygame.image.load(path)
                            texture_size = (config.TEXTURE_SIZE, config.TEXTURE_SIZE)
                            self.textures[tex_id] = pygame.transform.scale(original, texture_size)
                        except (ValueError, pygame.error):
                            continue
        except OSError:
            pass
        
        # Usar texturas padrão para IDs não carregados
        for tex_id, texture in default_textures.items():
            if tex_id not in self.textures:
                self.textures[tex_id] = texture
    
    def create_optimized_brick_texture(self):
        """Textura de tijolo otimizada usando variáveis configuráveis"""
        texture_size = config.TEXTURE_SIZE
        texture = pygame.Surface((texture_size, texture_size))
        texture.fill(config.BRICK_COLOR)
        
        # Padrão de tijolo escalável baseado no tamanho da textura
        brick_height = texture_size // 8
        brick_width = texture_size // 4
        mortar_color = (
            max(0, config.BRICK_COLOR[0] - 40),
            max(0, config.BRICK_COLOR[1] - 30),
            max(0, config.BRICK_COLOR[2] - 30)
        )
        
        # Desenhar linhas horizontais
        for y in range(0, texture_size, brick_height):
            pygame.draw.line(texture, mortar_color, (0, y), (texture_size, y), 2)
        
        # Desenhar linhas verticais alternadas
        for row in range(0, texture_size // brick_height):
            offset = (brick_width // 2) if row % 2 else 0
            y_pos = row * brick_height
            for x in range(offset, texture_size, brick_width):
                if x > 0:
                    pygame.draw.line(texture, mortar_color, 
                                   (x, y_pos), (x, y_pos + brick_height), 2)
        
        return texture
    
    def create_optimized_stone_texture(self):
        """Textura de pedra otimizada usando variáveis configuráveis"""
        texture_size = config.TEXTURE_SIZE
        texture = pygame.Surface((texture_size, texture_size))
        texture.fill(config.STONE_COLOR)
        
        # Padrão de pedra com variações
        block_size = texture_size // 8
        for x in range(0, texture_size, block_size):
            for y in range(0, texture_size, block_size):
                # Criar variação de cor baseada na posição
                variation = ((x + y) % (block_size * 3)) - block_size
                color = (
                    max(20, min(255, config.STONE_COLOR[0] + variation)),
                    max(20, min(255, config.STONE_COLOR[1] + variation)),
                    max(20, min(255, config.STONE_COLOR[2] + variation // 2))
                )
                
                # Desenhar bloco com bordas mais escuras
                block_rect = (x, y, block_size, block_size)
                pygame.draw.rect(texture, color, block_rect)
                
                # Adicionar bordas
                border_color = (
                    max(0, color[0] - 20),
                    max(0, color[1] - 20),
                    max(0, color[2] - 20)
                )
                pygame.draw.rect(texture, border_color, block_rect, 1)
        
        return texture
    
    def create_optimized_wood_texture(self):
        """Textura de madeira otimizada usando variáveis configuráveis"""
        texture_size = config.TEXTURE_SIZE
        texture = pygame.Surface((texture_size, texture_size))
        texture.fill(config.WOOD_COLOR)
        
        # Grãos de madeira verticais
        grain_spacing = texture_size // 16
        for x in range(0, texture_size, grain_spacing):
            # Criar variação senoidal para grãos naturais
            for y in range(texture_size):
                offset = int(math.sin(y * 0.1 + x * 0.05) * (grain_spacing // 2))
                grain_x = x + offset
                
                if 0 <= grain_x < texture_size:
                    # Cor do grão baseada na posição
                    grain_intensity = math.sin(y * 0.02) * 0.3 + 0.7
                    grain_color = (
                        max(0, min(255, int(config.WOOD_COLOR[0] * grain_intensity))),
                        max(0, min(255, int(config.WOOD_COLOR[1] * grain_intensity))),
                        max(0, min(255, int(config.WOOD_COLOR[2] * grain_intensity)))
                    )
                    
                    # Desenhar linha de grão
                    if y % 2 == 0:  # Reduzir densidade para performance
                        texture.set_at((grain_x, y), grain_color)
        
        return texture
    
    def get_wall_texture(self, wall_type):
        """Retorna textura para tipo de parede"""
        if not config.ENABLE_TEXTURES:
            return None
            
        return self.textures.get(wall_type, self.textures.get(1))
    
    def get_scaled_texture(self, wall_type, size):
        """Obtém textura redimensionada com cache inteligente"""
        if not config.ENABLE_TEXTURES:
            return None
            
        cache_key = (wall_type, size)
        
        # Verificar cache
        if cache_key in self.scaled_cache:
            return self.scaled_cache[cache_key]
        
        base_texture = self.get_wall_texture(wall_type)
        if base_texture and len(self.scaled_cache) < self.max_cache_size:
            try:
                # Aplicar fator de qualidade
                actual_size = (
                    int(size[0] * config.TEXTURE_QUALITY),
                    int(size[1] * config.TEXTURE_QUALITY)
                )
                
                scaled = pygame.transform.scale(base_texture, actual_size)
                self.scaled_cache[cache_key] = scaled
                
                # Gerenciar cache
                self.cache_access_count += 1
                if self.cache_access_count % config.CACHE_CLEANUP_INTERVAL == 0:
                    self.cleanup_cache()
                
                return scaled
            except pygame.error:
                return base_texture
        
        return base_texture
    
    def cleanup_cache(self):
        """Limpa cache quando necessário"""
        if len(self.scaled_cache) > self.max_cache_size * 0.8:
            # Remove 25% das entradas mais antigas (implementação simples)
            items_to_remove = len(self.scaled_cache) // 4
            cache_keys = list(self.scaled_cache.keys())
            
            for i in range(items_to_remove):
                if cache_keys:
                    key_to_remove = cache_keys[i]
                    if key_to_remove in self.scaled_cache:
                        del self.scaled_cache[key_to_remove]
    
    def clear_cache(self):
        """Limpa todo o cache de texturas"""
        self.scaled_cache.clear()
        self.cache_access_count = 0
    
    def get_texture_info(self):
        """Retorna informações sobre texturas carregadas (para debug)"""
        return {
            'loaded_textures': len(self.textures),
            'cached_textures': len(self.scaled_cache),
            'cache_access_count': self.cache_access_count,
            'texture_size': config.TEXTURE_SIZE,
            'textures_enabled': config.ENABLE_TEXTURES
        }