# Implementation of asteroid objects.

class Asteroid:
    """The asteroid object."""
    def __init__(self, x, y):
        self.x = x
        self.y = y

class AbstractCluster:
    """Used as a precursor to the cluster, encodes the cluster's position."""
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Cluster:
    """A collection of asteroids."""
    def __init__(self, *args):
        self.asteroids = list(args)
    def add_asteroid(self, asteroid):
        self.asteroids.append(asteroid)