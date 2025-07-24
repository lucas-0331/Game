import math
import pygame
from src import config
from src.maps.maps import Maps

class Player:
    def __init__(self, lvl):
        self.x = config.X_POSITION
        self.y = config.Y_POSITION
        self.rot = config.ROTATION_R
        self.speed = config.MOVE_SPEED
        self.sensitivity = config.SENSITIVITY
        self.maps = Maps()
        self.map = self.maps.get_map(lvl)
        self.collision_radius = 0.2
        
        self.interaction_target = None

    def update(self):
        self.check_interaction()
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_e] and self.interaction_target is not None:
            if self.interaction_target == 1:
                return 'goal_reached'

        dx, dy = 0, 0
        if keys[pygame.K_w]:
            dx += self.speed * math.cos(self.rot)
            dy += self.speed * math.sin(self.rot)
        if keys[pygame.K_s]:
            dx -= self.speed * math.cos(self.rot)
            dy -= self.speed * math.sin(self.rot)
        
        if keys[pygame.K_a]:
            self.rot -= self.sensitivity
        if keys[pygame.K_d]:
            self.rot += self.sensitivity
        self.rot %= (2 * math.pi)

        if self.can_move_to(self.x + dx, self.y):
            self.x += dx
        if self.can_move_to(self.x, self.y + dy):
            self.y += dy
            
        return None

    def check_interaction(self):
        check_dist = self.collision_radius * 2.5
        check_x = self.x + check_dist * math.cos(self.rot)
        check_y = self.y + check_dist * math.sin(self.rot)
        map_x, map_y = int(check_x), int(check_y)

        if 0 <= map_y < len(self.map) and 0 <= map_x < len(self.map[0]):
            tile_type = self.map[map_y][map_x]
            if tile_type == 1:
                self.interaction_target = tile_type
                return
        self.interaction_target = None

    def can_move_to(self, x, y):
        for offset_x in [-self.collision_radius, self.collision_radius]:
            for offset_y in [-self.collision_radius, self.collision_radius]:
                map_x = int(x + offset_x)
                map_y = int(y + offset_y)

                if not (0 <= map_y < len(self.map) and 0 <= map_x < len(self.map[0])):
                    return False
                
                if self.map[map_y][map_x] != 0:
                    return False
        
        return True

