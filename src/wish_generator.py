import random


def read_wishes(path):
    """"Reads in birthday wishes from a given path."""
    f = open(path, "r")
    wishes = f.read().splitlines()
    f.close()
    return wishes


def select_random_wish(path):
    """Returns a random birthday wish from a given path"""
    wishes = read_wishes(path)
    return random.choice(wishes)
