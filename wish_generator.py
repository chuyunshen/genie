import random

def read_wishes(path):
    f = open(path, "r")
    wishes = f.readlines()
    f.close()
    return wishes

def select_random_wish(path):
    wishes = read_wishes(path)
    return random.choice(wishes)
