# Implements the spaceship object
from math import pi, sin, cos, atan2, degrees, sqrt

THROTTLE_QUADRANTS = {'REVERSE': -0.1, 'STATIONARY': 0, 'FORWARD_1': 0.1, 'FORWARD_2': 0.25, 'AFTERBURNER': 0.4}
class Ship(object):
    def __init__(self, x, y, galaxy):
        self.x = x
        self.y = y
        self._speed = 0
        self.dir = atan2(-self.y, -self.x)
        self.galaxy = galaxy


        self.destination_x=0
        self.destination_y=0


    @property
    def direction(self):
        return self.dir
    @direction.setter
    def direction(self, value):
        self.dir = round(value % (2*pi),4)
    def update_position(self):
        self.x += self._speed * (cos(self.dir))
        self.y += self._speed * (sin(self.dir))

    @property
    def speed(self):
        return self._speed
    @speed.setter
    def speed(self, value):
        if type(value) == float:
            self._speed = value
        if type(value) == int:
            self._speed = value

def generate_ship_position(galaxy, rng):
    ship_dev = rng.gen() * galaxy.size/10
    ship_phi = rng.gen() * 2*pi
    ship_r = galaxy.size - ship_dev
    ship_x = ship_r * cos(ship_phi)
    ship_y = ship_r * sin(ship_phi)

    return ship_x, ship_y

def _try_new_position(ship,galaxy,rng):

    ship_phi = atan2(ship.y,ship.x)
    dest_phi = rng.gen()*2*pi
    dest_dev = rng.gen()*galaxy.size/10
    dest_r = galaxy.size + dest_dev
    dest_x = dest_r * cos(dest_phi)
    dest_y = dest_r * sin(dest_phi)
    return dest_x, dest_y

def generate_destination_position(ship,galaxy,rng):
    dest_x, dest_y = _try_new_position(ship,galaxy,rng)
    while sqrt((ship.x-dest_x)**2 + (ship.y-dest_y)**2) < 1000:
        dest_x, dest_y = _try_new_position(ship,galaxy,rng)
    return dest_x, dest_y


