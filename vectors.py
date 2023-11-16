import math

# Functions for vector operations

def vectorBetween(pos1, pos2):
    x1, y1 = pos1[0], pos1[1]
    x2, y2 = pos2[0], pos2[1]
    return (x2 - x1, y2 - y1)

def mag(vector):
    x, y = vector[0], vector[1]
    return math.sqrt(x**2 + y**2)

def norm(vector):
    magnitude = mag(vector)
    return (vector[0] / magnitude, vector[1] / magnitude)

