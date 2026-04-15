import pygame
import sys

import map_generator
from asteroid import Asteroid
from ship import Ship,generate_ship_position
from galaxy import Galaxy

from math import sqrt, pi, sin, cos, atan2, degrees, radians

class SpaceDelivery:
    def __init__(self):

        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.main_panel = pygame.image.load("assets/main-panel.png")


        self.rng = map_generator.RandomNumberGenerator()

        self.galaxy = Galaxy()
        self.ship_x, self.ship_y = generate_ship_position(self.galaxy,self.rng)
        self.ship = Ship(self.ship_x, self.ship_y, self.galaxy)

        self.asteroid_contact_image = pygame.image.load("assets/red_pixel.png")
        self.radar_offset_x=250
        self.radar_offset_y=945
        map_generator.generate_map(self.galaxy, self.rng)
        self.galaxy.add_asteroid(Asteroid(800,0))

        pygame.display.set_caption("Space Delivery")

    def update_radar(self):
        for asteroid in self.galaxy.asteroids:
            dist = sqrt((self.ship.x - asteroid.x)**2 +  (self.ship.y - asteroid.y)**2)
            if  dist < 300:
                dx = asteroid.x-self.ship.x
                dy = asteroid.y-self.ship.y
                rad = atan2(dy,dx)  # calculate bearing
                angle = (degrees(rad) - self.ship.direction) % 360 # compare bearings to check if angle is within radar search cone
                if angle <= 45 or angle >= 315:
                    screen_x=dist * cos(radians(angle+90)) + self.radar_offset_x
                    screen_y=self.radar_offset_y - dist * sin(radians(angle+90)) # add 90 so that 0 degrees is y axis

                    self.screen.blit(self.asteroid_contact_image, (screen_x, screen_y))

    def run_game(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            self.screen.blit(self.main_panel, (0,0))

            self.update_radar()
            pygame.display.flip()



if __name__ == "__main__":
    space_delivery = SpaceDelivery()
    space_delivery.run_game()
