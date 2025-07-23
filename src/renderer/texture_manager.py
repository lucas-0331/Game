import pygame
import os
import math
from src import config

class TextureManager:
    def __init__(self):
        self.textures = {}
        self.scaled_cache = {} 
        self.max_cache_size = config.MAX_TEXTURE_CACHE_SIZE
        self.cache_access_count = 0
        self.load_textures()
    

    def load_textures(self):
        assets_path = "assets/textures/"
        try:
            if os.path.exists(assets_path):
                for filename in os.listdir(assets_path):
                    if filename.lower().endswith(('.png', '.jpg', '.bmp')):
                        path = os.path.join(assets_path, filename)
                        try:
                            tex_id = int(filename.split('.')[0])
                            original = pygame.image.load(path)
                            texture_size = (config.TEXTURE_SIZE, config.TEXTURE_SIZE)
                            self.textures[tex_id] = pygame.transform.scale(original, texture_size)
                        except (ValueError, pygame.error):
                            continue
        except OSError:
            pass
        
    
    def get_wall_texture(self, wall_type):
        if not config.ENABLE_TEXTURES:
            return None
            
        return self.textures.get(wall_type, self.textures.get(1))
    

    def get_scaled_texture(self, wall_type, size):
        if not config.ENABLE_TEXTURES:
            return None
            
        cache_key = (wall_type, size)
        
        if cache_key in self.scaled_cache:
            return self.scaled_cache[cache_key]
        
        base_texture = self.get_wall_texture(wall_type)
        if base_texture and len(self.scaled_cache) < self.max_cache_size:
            try:
                actual_size = (
                    int(size[0] * config.TEXTURE_QUALITY),
                    int(size[1] * config.TEXTURE_QUALITY)
                )
                
                scaled = pygame.transform.scale(base_texture, actual_size)
                self.scaled_cache[cache_key] = scaled
                
                self.cache_access_count += 1
                if self.cache_access_count % config.CACHE_CLEANUP_INTERVAL == 0:
                    self.cleanup_cache()
                
                return scaled
            except pygame.error:
                return base_texture
        
        return base_texture
    

    def cleanup_cache(self):
        if len(self.scaled_cache) > self.max_cache_size * 0.8:
            items_to_remove = len(self.scaled_cache) // 4
            cache_keys = list(self.scaled_cache.keys())
            
            for i in range(items_to_remove):
                if cache_keys:
                    key_to_remove = cache_keys[i]
                    if key_to_remove in self.scaled_cache:
                        del self.scaled_cache[key_to_remove]
    

    def clear_cache(self):
        self.scaled_cache.clear()
        self.cache_access_count = 0
    

    def get_texture_info(self):
        return {
            'loaded_textures': len(self.textures),
            'cached_textures': len(self.scaled_cache),
            'cache_access_count': self.cache_access_count,
            'texture_size': config.TEXTURE_SIZE,
            'textures_enabled': config.ENABLE_TEXTURES
        }
