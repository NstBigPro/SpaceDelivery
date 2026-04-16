import pygame
import sys

import map_generator
from asteroid import Asteroid
from ship import *
from galaxy import Galaxy

from math import sqrt, pi, sin, cos, atan2, degrees, radians

class SpaceDelivery:
    def __init__(self):

        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.surface = pygame.Surface((1920,1080))
        self.main_panel = pygame.image.load("assets/main_panel.png")


        self.rng = map_generator.RandomNumberGenerator()

        self.galaxy = Galaxy()
        self.ship_x, self.ship_y = generate_ship_position(self.galaxy,self.rng)

        self.ship = Ship(self.ship_x, self.ship_y, self.galaxy)


        self.ship.destination_x, self.ship.destination_y = generate_destination_position(self.ship,self.galaxy,self.rng)

        self.asteroid_contact_image = pygame.image.load("assets/red_pixel.png")
        self.waypoint_image = pygame.image.load("assets/blue_pixel.png")
        self.fuel_indicator = pygame.image.load("assets/white_pixel.png")
        self.radar_offset_x=250
        self.radar_offset_y=945

        self.fuel = 1000

        self.fuel_offset_x=1110
        self.fuel_offset_y_1=810
        self.fuel_offset_y_2=830

        self.fuel_scale_factor = 260/self.fuel

        self.nav_offset_x=250
        self.nav_offset_y=260

        self.throttle_quadrant = "STATIONARY"

        self.throttle_r = pygame.image.load("assets/throttle_r.png")
        self.throttle_1 = pygame.image.load("assets/throttle_1.png")
        self.throttle_2 = pygame.image.load("assets/throttle_2.png")
        self.throttle_a = pygame.image.load("assets/throttle_a.png")

        self.throttle_offset_x = 1400
        self.throttle_offset_y = 120

        self.engine_indicator = pygame.image.load("assets/engine_indicator.png")

        self.l_engine_offset_x = 540
        self.l_engine_offset_y = 670

        self.r_engine_offset_x = 540
        self.r_engine_offset_y = 740

        self.l_engine_active = False
        self.r_engine_active = False

        self.start_top_left_corner_x = 850
        self.start_top_left_corner_y = 660

        self.start_bottom_right_corner_x = 930
        self.start_bottom_right_corner_y = 740

        self.has_started = False
        self.start_time = -1
        self.elapsed_time = pygame.time.get_ticks()
        print(self.elapsed_time)
        map_generator.generate_map(self.galaxy, self.rng)

        pygame.display.set_caption("Space Delivery")

        print(self.ship.destination_x, self.ship.destination_y, self.ship.x, self.ship.y)
    def update_navigator(self):
        if self.has_started:
            scale = 0.1 # derived from picture as radius of navigator is ~200pixels, and galaxy diameter is 2000
            angle = atan2(-self.ship.y,-self.ship.x)
            r = sqrt((self.ship.x-self.ship.destination_x)**2+(self.ship.y-self.ship.destination_y)**2) * scale
            screen_x = r*cos(angle) + self.nav_offset_x
            screen_y = r*sin(angle) + self.nav_offset_y
            self.surface.blit(self.waypoint_image, (screen_x, screen_y)) #destination
            self.surface.blit(self.waypoint_image, (self.nav_offset_x, self.nav_offset_y)) # own ship

    def update_radar(self):
        if self.has_started:
            for asteroid in self.galaxy.asteroids:
                dist = sqrt((self.ship.x - asteroid.x)**2 +  (self.ship.y - asteroid.y)**2)
                if  dist < 300:
                    dx = asteroid.x-self.ship.x
                    dy = asteroid.y-self.ship.y
                    rad = atan2(dy,dx)  # calculate bearing
                    angle = (degrees(rad) - self.ship.direction) % 360 # compare bearings to check if angle is within radar search cone
                    if angle <= 45 or angle >= 315:
                        screen_x=dist * cos(radians(angle+90)) + self.radar_offset_x # add 90 so that 0 degrees is y-axis
                        screen_y=self.radar_offset_y - dist * sin(radians(angle+90)) # we subtract since range increases as y coord decreases

                        self.surface.blit(self.asteroid_contact_image, (screen_x, screen_y))

    def increase_throttle(self):
        if self.has_started:
            if self.throttle_quadrant == "REVERSE":
                self.throttle_quadrant = "STATIONARY"
            elif self.throttle_quadrant == "STATIONARY":
                self.throttle_quadrant = "FORWARD_1"
            elif self.throttle_quadrant == "FORWARD_1":
                self.throttle_quadrant = "FORWARD_2"
            elif self.throttle_quadrant == "FORWARD_2":
                self.throttle_quadrant = "AFTERBURNER"

    def decrease_throttle(self):
        if self.has_started:
            if self.throttle_quadrant == "AFTERBURNER":
                self.throttle_quadrant = "FORWARD_2"
            elif self.throttle_quadrant == "FORWARD_2":
                self.throttle_quadrant = "FORWARD_1"
            elif self.throttle_quadrant == "FORWARD_1":
                self.throttle_quadrant = "STATIONARY"
            elif self.throttle_quadrant == "STATIONARY":
                self.throttle_quadrant = "REVERSE"

        print(self.throttle_quadrant)

    def update_throttle(self):
        if self.throttle_quadrant == "REVERSE":
            self.surface.blit(self.throttle_r, (self.throttle_offset_x,self.throttle_offset_y))
        if self.throttle_quadrant == "FORWARD_1":
            self.surface.blit(self.throttle_1, (self.throttle_offset_x,self.throttle_offset_y))
        if self.throttle_quadrant == "FORWARD_2":
            self.surface.blit(self.throttle_2, (self.throttle_offset_x,self.throttle_offset_y))
        if self.throttle_quadrant == "AFTERBURNER":
            self.surface.blit(self.throttle_a, (self.throttle_offset_x,self.throttle_offset_y))

    def update_fuel(self):
        if self.has_started:
            screen_x=round(self.fuel * self.fuel_scale_factor + self.fuel_offset_x)
            self.surface.blit(self.fuel_indicator, (screen_x, self.fuel_offset_y_1))
            self.surface.blit(self.fuel_indicator, (screen_x, self.fuel_offset_y_2))

    def update_engine_indicators(self):
        if self.l_engine_active:
            self.surface.blit(self.engine_indicator, (self.l_engine_offset_x, self.l_engine_offset_y))
        if self.r_engine_active:
            self.surface.blit(self.engine_indicator, (self.r_engine_offset_x, self.r_engine_offset_y))

    def run_game(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        self.increase_throttle()
                    if event.key == pygame.K_s:
                        self.decrease_throttle()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if self.start_top_left_corner_x <= mouse_x <= self.start_bottom_right_corner_x and self.start_top_left_corner_y <= mouse_y <= self.start_bottom_right_corner_y:
                        self.start_time = pygame.time.get_ticks()

            self.surface.blit(self.main_panel, (0,0))
            self.elapsed_time = pygame.time.get_ticks()
            if self.elapsed_time - self.start_time > 1000 and not self.has_started and self.start_time >= 0:
                self.l_engine_active = True

            if self.elapsed_time - self.start_time > 2500 and not self.has_started and self.start_time >= 0:
                self.r_engine_active = True

            if self.elapsed_time - self.start_time > 4000 and not self.has_started and self.start_time >= 0:
                self.has_started = True

            self.update_radar()
            self.update_navigator()
            self.update_throttle()
            self.update_fuel()
            self.update_engine_indicators()
            self.screen.blit(pygame.transform.scale(self.surface, self.screen.get_size()), (0,0))
            pygame.display.flip()



if __name__ == "__main__":
    space_delivery = SpaceDelivery()
    space_delivery.run_game()
