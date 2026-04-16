# Implements the spaceship object
from math import pi, sin, cos, atan2, degrees

THROTTLE_QUADRANTS = {'REVERSE': -0.25, 'STATIONARY': 0, 'FORWARD_1': 0.33, 'FORWARD_2': 0.66, 'AFTERBURNER': 1}
class Ship(object):
    def __init__(self, x, y, galaxy):
        self.x = x
        self.y = y
        self._speed = 0
        self.dir = degrees(atan2(-self.y, -self.x))
        self.galaxy = galaxy

        self.collided = False

        self.destination_x=0
        self.destination_y=0


    @property
    def direction(self):
        return self.dir
    @direction.setter
    def direction(self, value):
        self.dir = round(value % (2*pi),4)
    def _check_collision(self):
        for asteroid in self.galaxy.asteroids:
            if (self.x - asteroid.x)**2 + (self.y - asteroid.y)**2 < 1:
                self.collided = True
                break
    def update_position(self):
        self._check_collision()
        if not self.collided:
            self.x += self._speed * (cos(self.dir))
            self.y += self._speed * (sin(self.dir))

    @property
    def speed(self):
        return self._speed
    @speed.setter
    def speed(self, value):
        if type(value) == float:
            self._speed = round((value % 10), 3)
        if type(value) == str:
            try:
                self._speed = THROTTLE_QUADRANTS[value]
            except KeyError:
                self._speed = 0
        if type(value) == int:
            if value >= 10:
                self._speed = 10
            else:
                self._speed = value
        else:
            self._speed = 0

def generate_ship_position(galaxy, rng):
    ship_dev = rng.gen() * galaxy.size/10
    ship_phi = rng.gen() * 2*pi
    ship_r = galaxy.size - ship_dev
    ship_x = ship_r * cos(ship_phi)
    ship_y = ship_r * sin(ship_phi)

    return ship_x, ship_y

def generate_destination_position(ship,galaxy,rng):
    ship_phi = atan2(ship.y,ship.x)
    dest_phi = rng.gen()*2*pi
    if abs(dest_phi - ship_phi) < pi/2:
        dest_phi += pi
    dest_dev = rng.gen()*galaxy.size/10
    dest_r = galaxy.size + dest_dev
    dest_x = dest_r * cos(dest_phi)
    dest_y = dest_r * sin(dest_phi)
    return dest_x, dest_y


