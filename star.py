from encodings.punycode import selective_find
from math import pi,sin,cos

class Star:
    def __init__(self,x,y,rng):
        self.x = x
        self.y = y
        self.rng = rng
    def update(self):
        if self.rng.gen()>0.1:
            pass
        else:
            direction = self.rng.gen()*2*pi
            movement = self.rng.gen()*3

            self.x += movement*cos(direction)
            self.y += movement*sin(direction)