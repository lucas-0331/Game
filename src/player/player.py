import math
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

    def update(self):
        X, Y = self.x, self.y

        if config.W_KEY:
            X += self.speed * math.cos(self.rot)
            Y += self.speed * math.sin(self.rot)
        if config.S_KEY:
            X -= self.speed * math.cos(self.rot)
            Y -= self.speed * math.sin(self.rot)
        if config.A_KEY:
            self.rot -= self.sensitivity
        if config.D_KEY:
            self.rot += self.sensitivity

        if self.map[int(Y)][int(X)] == 0:
            self.x, self.y = X, Y

        config.X_POSITION = self.x
        config.Y_POSITION = self.y
        config.ROTATION_R = self.rot

