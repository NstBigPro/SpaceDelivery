# Implementation of the galaxy object

class Galaxy:
    def __init__(self, size=1000):
        self.size = size
        self.asteroids = []
        self.clusters = []

    def add_asteroid(self, asteroid):
        self.asteroids.append(asteroid)
    def add_cluster(self, cluster):
        self.clusters.append(cluster)