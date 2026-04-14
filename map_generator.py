# Map generator
# Used to generate the map and provides RNG implementations


import random
import datetime
import math

from asteroid import *
from galaxy import Galaxy

class RandomNumberGenerator:
    """A basic RNG. Epoch time of object initialization is used as default seed"""
    def __init__(self, initial_seed=datetime.datetime.now().timestamp()):
        self.seed = initial_seed
        random.seed(self.seed)
    def gen(self):
        """Generate a random number between 0 and 1"""
        return random.random()
    def gen_int(self, *args):
        """Generates a random integer based on upper bound (or both bounds if provided)"""
        if len(args) == 1:
            return random.randint(*args)
        if len(args) == 2:
            return random.randint(*args)
        if len(args) >= 3 or len(args) == 0:
            return None
        return None


def _generate_map(abstract_cluster_collection, galaxy, rng):
    """Populates the map with asteroids based on abstract clusters position"""
    for abstract_cluster in abstract_cluster_collection:
        size = rng.gen_int(2, 20)
        amount = rng.gen_int(10, 100)
        cluster = Cluster()
        while len(cluster.asteroids) < amount:
            asteroid_r = rng.gen() * size
            asteroid_phi = rng.gen() * 2 * math.pi
            asteroid_x = asteroid_r * math.cos(asteroid_phi) + abstract_cluster.x
            asteroid_y = asteroid_r * math.sin(asteroid_phi) + abstract_cluster.y
            asteroid = Asteroid(asteroid_x, asteroid_y)
            cluster.add_asteroid(asteroid)
            galaxy.add_asteroid(asteroid)
        galaxy.add_cluster(cluster)

def _populate_abstract_clusters(galaxy, abstract_cluster_collection, amount, rng):
    """Generates abstract cluster positions in a ring-like pattern"""
    for i in range(amount):
        abstract_cluster_deviation = rng.gen() * galaxy.size / 3 #to obtain ring-like pattern, we deviate from the ring with half the size of the galaxy by a factor of a third of the size of the galaxy
        abstract_cluster_phi = rng.gen() * 2 * math.pi
        abstract_cluster_r = abstract_cluster_deviation + galaxy.size /2
        abstract_cluster_x = abstract_cluster_r * math.cos(abstract_cluster_phi)
        abstract_cluster_y = abstract_cluster_r * math.sin(abstract_cluster_phi)

        abstract_cluster = AbstractCluster(abstract_cluster_x, abstract_cluster_y)
        abstract_cluster_collection.append(abstract_cluster)

def generate_map(galaxy: Galaxy, rng: RandomNumberGenerator) -> None:
    abstract_cluster_collection = []
    _populate_abstract_clusters(galaxy, abstract_cluster_collection, 200, rng)
    _generate_map(abstract_cluster_collection, galaxy, rng)


