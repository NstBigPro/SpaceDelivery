import pygame
import sys
import json
import datetime


if sys.platform == "win32":
    import ctypes
    ctypes.windll.user32.SetProcessDPIAware()

import map_generator
from ship import *
from galaxy import Galaxy
from random import random
from math import sqrt, pi, sin, cos, atan2, degrees, radians


DEATH_CAUSES: dict[str, str] = {'ALIVE':'0', 'ASTEROID_COLLISION':'1', 'LEFT_MAP':'2', 'FUEL_DEPLETED':'3',
                                'ENGINE_EXPLODED': '4', 'ENGINE_FAILURE': '5'}

class SpaceDelivery:
    def __init__(self):

        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.surface = pygame.Surface((1920,1080))
        self.death_surface = pygame.Surface(self.screen.get_size())
        self.main_panel = pygame.image.load("assets/main_panel.png")


        self.rng = map_generator.RandomNumberGenerator(datetime.datetime.now().timestamp())

        self.galaxy = Galaxy()
        self.ship_x, self.ship_y = generate_ship_position(self.galaxy,self.rng)

        self.ship_x = 1000
        self.ship_y = 0

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
        self.fire_extinguish = pygame.image.load("assets/fire_button.png")
        self.cargo_button = pygame.image.load("assets/fire_button.png")

        self.l_fire_indicator = pygame.image.load("assets/l_fire.png")
        self.r_fire_indicator = pygame.image.load("assets/r_fire.png")

        self.l_engine_offset_x = 540
        self.l_engine_offset_y = 670

        self.r_engine_offset_x = 540
        self.r_engine_offset_y = 740

        self.l_engine_extinguish_offset_x = 1500
        self.l_engine_extinguish_offset_y = 830

        self.r_engine_extinguish_offset_x = 1760
        self.r_engine_extinguish_offset_y = 830

        self.l_engine_fire_offset_x = 1400
        self.l_engine_fire_offset_y = 640

        self.r_engine_fire_offset_x = 1670
        self.r_engine_fire_offset_y = 640

        self.l_engine_active = False
        self.r_engine_active = False

        self.l_engine_broken = False
        self.r_engine_broken = False

        self.l_engine_fire = False
        self.l_engine_fire_time = -1
        self.r_engine_fire = False
        self.r_engine_fire_time = -1

        self.failure_factor = 1

        self.start_top_left_corner_x = 850
        self.start_top_left_corner_y = 660

        self.start_bottom_right_corner_x = 930
        self.start_bottom_right_corner_y = 740

        self.has_started = False
        self.start_time = -1
        self.elapsed_time = pygame.time.get_ticks()

        self.turning_left = False
        self.turning_right = False

        self.cargo_offset_x = 540
        self.cargo_offset_y = 870

        self.cargo_drop_offset_x = 560
        self.cargo_drop_offset_y = 970

        self.ship_turning_factor = pi/800

        self.font = pygame.font.Font("assets/font.ttf", size=20)

        self.cause_of_death = 'ALIVE'
        with open("assets/death_msg.json",'r') as f:
            self.death_messages = json.load(f)

        self.death_theme = pygame.mixer.Sound("assets/ost_star_dust.wav")

        map_generator.generate_map(self.galaxy, self.rng)

        pygame.display.set_caption("Space Delivery")
    def update_navigator(self):
        if self.has_started:
            dx = self.ship.destination_x - self.ship.x
            dy = self.ship.destination_y - self.ship.y
            scale = 0.1 # derived from picture as radius of navigator is ~200pixels, and galaxy diameter is 2000
            rad = atan2(dy,dx)
            angle = (degrees(rad) - degrees(self.ship.direction)) % 360
            dist = sqrt((self.ship.x-self.ship.destination_x)**2+(self.ship.y-self.ship.destination_y)**2)
            if dist > 2000: dist = 2000
            dist *= scale
            screen_x=dist * cos(radians(angle+90)) + self.nav_offset_x
            screen_y=self.nav_offset_y - dist * sin(radians(angle+90))
            self.surface.blit(self.waypoint_image, (screen_x, screen_y)) #destination
            self.surface.blit(self.waypoint_image, (self.nav_offset_x, self.nav_offset_y)) # own ship

    def update_radar(self):
        if self.has_started:
            for asteroid in self.galaxy.asteroids:
                dist = sqrt((self.ship.x - asteroid.x)**2 +  (self.ship.y - asteroid.y)**2)
                if  dist < 100:
                    dx = asteroid.x-self.ship.x
                    dy = asteroid.y-self.ship.y
                    rad = atan2(dy,dx)  # calculate bearing
                    angle = (degrees(rad) - degrees(self.ship.direction)) % 360 # compare bearings to check if angle is within radar search cone
                    if angle <= 45 or angle >= 315:
                        dist *= 3
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


    def update_throttle(self):
        if self.throttle_quadrant == "REVERSE":
            self.surface.blit(self.throttle_r, (self.throttle_offset_x,self.throttle_offset_y))
        if self.throttle_quadrant == "FORWARD_1":
            self.surface.blit(self.throttle_1, (self.throttle_offset_x,self.throttle_offset_y))
        if self.throttle_quadrant == "FORWARD_2":
            self.surface.blit(self.throttle_2, (self.throttle_offset_x,self.throttle_offset_y))
        if self.throttle_quadrant == "AFTERBURNER":
            self.surface.blit(self.throttle_a, (self.throttle_offset_x,self.throttle_offset_y))
        if self.fuel >= 0:
            self.ship.speed = THROTTLE_QUADRANTS[self.throttle_quadrant] * self.failure_factor
        else:
            self.ship.speed = 0
            self.l_engine_active = False
            self.r_engine_active = False
            self.cause_of_death = 'FUEL_DEPLETED'
    def update_fuel(self):
        if self.has_started:
            screen_x=round(self.fuel * self.fuel_scale_factor + self.fuel_offset_x)
            self.surface.blit(self.fuel_indicator, (screen_x, self.fuel_offset_y_1))
            self.surface.blit(self.fuel_indicator, (screen_x, self.fuel_offset_y_2))
        if self.throttle_quadrant == "REVERSE":
           self.fuel -= 0.02 * self.failure_factor
        if self.throttle_quadrant == "FORWARD_1":
            self.fuel -= 0.004 * self.failure_factor
        if self.throttle_quadrant == "FORWARD_2":
            self.fuel -= 0.01 * self.failure_factor
        if self.throttle_quadrant == "AFTERBURNER":
            self.fuel -= 0.3 * self.failure_factor
    def update_engine_indicators(self):
        if self.l_engine_active:
            self.surface.blit(self.engine_indicator, (self.l_engine_offset_x, self.l_engine_offset_y))
        if self.r_engine_active:
            self.surface.blit(self.engine_indicator, (self.r_engine_offset_x, self.r_engine_offset_y))

    def update_fire_indicators(self):
        if self.l_engine_fire:
            self.surface.blit(self.fire_extinguish, (self.l_engine_extinguish_offset_x, self.l_engine_extinguish_offset_y))
            self.surface.blit(self.l_fire_indicator, (self.l_engine_fire_offset_x, self.l_engine_fire_offset_y))
            self.failure_factor = 0.5
        if self.r_engine_fire:
            self.surface.blit(self.fire_extinguish, (self.r_engine_extinguish_offset_x, self.r_engine_extinguish_offset_y))
            self.surface.blit(self.r_fire_indicator, (self.r_engine_fire_offset_x, self.r_engine_fire_offset_y))
            self.failure_factor = 0.5

    def extinguish_left_engine(self):
        if self.l_engine_fire:
            self.l_engine_active = False
            self.l_engine_fire = False

    def extinguish_right_engine(self):
        if self.r_engine_fire:
            self.r_engine_active = False
            self.r_engine_fire = False

    def update_direction(self):
        if self.has_started:
            if self.turning_left:
                self.ship.direction += self.ship_turning_factor * sqrt(abs(self.ship.speed))
            if self.turning_right:
                self.ship.direction -= self.ship_turning_factor * sqrt(abs(self.ship.speed))

    def update_cargo(self):
        if self.has_started:
            self.surface.blit(self.engine_indicator, (self.cargo_offset_x, self.cargo_offset_y))
            dist = sqrt((self.ship.x-self.ship.destination_x) ** 2 + (self.ship.y-self.ship.destination_y) ** 2)
            if dist < 20:
                self.surface.blit(self.cargo_button, (self.cargo_drop_offset_x,self.cargo_drop_offset_y))

    def check_collisions(self):
        for asteroid in self.galaxy.asteroids:
            dist = sqrt((self.ship.x - asteroid.x)**2 +  (self.ship.y - asteroid.y)**2)
            if dist < 2:
                failure = self.rng.gen_int(1,6)
                if failure == 1:
                    self.cause_of_death = 'ASTEROID_COLLISION'
                elif self.l_engine_broken == False and(failure == 2 or failure == 3):
                    self.l_engine_fire = True
                    self.l_engine_broken = True
                    self.l_engine_fire_time = pygame.time.get_ticks()
                elif self.r_engine_broken == False and (failure == 4 or failure == 5):
                    self.r_engine_fire = True
                    self.r_engine_broken = True
                    self.r_engine_fire_time = pygame.time.get_ticks()
                del self.galaxy.asteroids[self.galaxy.asteroids.index(asteroid)]

    def check_distance(self):
        dist = sqrt(self.ship.x**2+self.ship.y**2)
        if dist > 1200:
            self.cause_of_death = 'LEFT_MAP'

    def check_engine_explosion(self):
        if self.l_engine_fire and pygame.time.get_ticks() - self.l_engine_fire_time > 3000:
            self.cause_of_death = 'ENGINE_EXPLODED'
        if self.r_engine_fire and pygame.time.get_ticks() - self.r_engine_fire_time > 3000:
            self.cause_of_death = 'ENGINE_EXPLODED'

    def check_engine_on(self):
        if self.has_started and self.l_engine_broken and self.r_engine_broken:
            self.cause_of_death = 'ENGINE_FAILURE'

    def _debug_plot(self):
        for asteroid in self.galaxy.asteroids:
            screen_x = asteroid.x/4 + 800
            screen_y = 400 - asteroid.y/4
            self.surface.blit(self.asteroid_contact_image, (screen_x, screen_y))
        screen_x = self.ship.x/4 + 800
        screen_y = 400 - self.ship.y/4
        self.surface.blit(self.waypoint_image, (screen_x, screen_y))
        screen_x = (self.ship.x/4+10*cos(self.ship.direction)) + 800
        screen_y = 400 - (self.ship.y/4+10*sin(self.ship.direction))
        self.surface.blit(self.waypoint_image, (screen_x, screen_y))
        screen_x = self.ship.destination_x/4 + 800
        screen_y = 400 - self.ship.destination_y/4
        self.surface.blit(self.fuel_indicator, (screen_x, screen_y))

    def death(self):
        death_time = pygame.time.get_ticks()
        self.elapsed_time = death_time
        if self.cause_of_death == 'ASTEROID_COLLISION' or self.cause_of_death == 'ENGINE_EXPLODED':
            while self.elapsed_time - death_time < 100:
                self.death_surface.fill((255,0,0))
                self.screen.blit(self.death_surface, (0,0))
                pygame.display.flip()
                self.elapsed_time = pygame.time.get_ticks()
        elif self.cause_of_death == 'LEFT_MAP' or self.cause_of_death == 'FUEL_DEPLETED' or self.cause_of_death == 'ENGINE_FAILURE':
            pygame.display.flip()
            self.has_started = False
            self.surface.blit(self.main_panel, (0, 0))
            self.screen.blit(pygame.transform.scale(self.surface, self.screen.get_size()), (0, 0))
        self.death_surface.fill((0, 0, 0))
        if self.cause_of_death == 'ASTEROID_COLLISION' or self.cause_of_death == 'ENGINE_EXPLODED':
            self.screen.blit(self.death_surface, (0, 0))
        pygame.display.flip()
        if self.cause_of_death in ['LEFT_MAP', 'FUEL_DEPLETED', 'ENGINE_FAILURE'] and self.elapsed_time - death_time < 1000:
            self.screen.blit(self.death_surface, (0, 0))

        while self.elapsed_time - death_time < 1500:
            self.elapsed_time = pygame.time.get_ticks()
        self.death_theme.play()
        while 1500 <= self.elapsed_time - death_time < 5500:
            self.elapsed_time = pygame.time.get_ticks()
            text = self.font.render(self.death_messages[DEATH_CAUSES[self.cause_of_death]][0], False,
                                    (255, 255, 255))
            text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
            self.death_surface.fill((0, 0, 0))
            self.death_surface.blit(text, text_rect)
            self.screen.blit(self.death_surface, (0, 0))
            pygame.display.flip()
        while 5500 <= self.elapsed_time - death_time < 9500:
            self.elapsed_time = pygame.time.get_ticks()
            text = self.font.render(self.death_messages[DEATH_CAUSES[self.cause_of_death]][1], False,
                                    (255, 255, 255))
            text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
            self.death_surface.fill((0, 0, 0))
            self.death_surface.blit(text, text_rect)
            self.screen.blit(self.death_surface, (0, 0))
            pygame.display.flip()
        while 9500 <= self.elapsed_time - death_time < 13500:
            self.elapsed_time = pygame.time.get_ticks()
            text = self.font.render(self.death_messages[DEATH_CAUSES[self.cause_of_death]][2], False,
                                    (255, 255, 255))
            text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
            self.death_surface.fill((0, 0, 0))
            self.death_surface.blit(text, text_rect)
            self.screen.blit(self.death_surface, (0, 0))
            pygame.display.flip()
        while 13500 <= self.elapsed_time - death_time < 17500:
            self.elapsed_time = pygame.time.get_ticks()
            text = self.font.render(self.death_messages[DEATH_CAUSES[self.cause_of_death]][3], False,
                                    (255, 255, 255))
            text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
            self.death_surface.fill((0, 0, 0))
            self.death_surface.blit(text, text_rect)
            self.screen.blit(self.death_surface, (0, 0))
            pygame.display.flip()
        self.death_theme.stop()
        self.__init__()
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
                    if event.key == pygame.K_a:
                        self.turning_left = True
                    if event.key == pygame.K_d:
                        self.turning_right = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.turning_left = False
                    if event.key == pygame.K_d:
                        self.turning_right = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if self.start_top_left_corner_x <= mouse_x <= self.start_bottom_right_corner_x and self.start_top_left_corner_y <= mouse_y <= self.start_bottom_right_corner_y:
                        self.start_time = pygame.time.get_ticks()
                    if self.l_engine_extinguish_offset_x <= mouse_x <= self.l_engine_extinguish_offset_x + 60 and self.l_engine_extinguish_offset_y <= mouse_y <= self.l_engine_extinguish_offset_y + 60:
                        self.extinguish_left_engine()
                    if self.r_engine_extinguish_offset_x <= mouse_x <= self.r_engine_extinguish_offset_x + 60 and self.r_engine_extinguish_offset_y <= mouse_y <= self.r_engine_extinguish_offset_y + 60:
                        self.extinguish_right_engine()

            self.elapsed_time = pygame.time.get_ticks()
            if self.elapsed_time - self.start_time > 1000 and not self.has_started and self.start_time >= 0:
                self.l_engine_active = True

            if self.elapsed_time - self.start_time > 2500 and not self.has_started and self.start_time >= 0:
                self.r_engine_active = True

            if self.elapsed_time - self.start_time > 4000 and not self.has_started and self.start_time >= 0:
                self.has_started = True

            if self.cause_of_death == 'ALIVE':
                self.surface.blit(self.main_panel, (0, 0))
                self.update_radar()
                self.update_navigator()
                self.update_throttle()
                self.update_fuel()
                self.update_engine_indicators()
                self.ship.update_position()
                self.update_direction()
                self.update_fire_indicators()
                self.update_cargo()
                self.check_distance()
                self.check_engine_on()
                self.check_engine_explosion()
                #self._debug_plot()
                self.screen.blit(pygame.transform.scale(self.surface, self.screen.get_size()), (0, 0))
            else:
                self.death()


            self.check_collisions()

            pygame.display.flip()



if __name__ == "__main__":
    space_delivery = SpaceDelivery()
    space_delivery.run_game()
