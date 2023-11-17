import math


class vec:  # Currently only supports 2D vectors

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return vec(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return vec(self.x - other.x, self.y - other.y)

    def __mul__(self, num):
        return vec(self.x * num, self.y * num)

    def __rmul__(self, num):
        return vec(self.x * num, self.y * num)

    def __truediv__(self, num):
        return vec(self.x / num, self.y / num)

    def __str__(self):
        return f"vec({self.x}, {self.y})"

    def mag(self):
        return math.sqrt(self.x**2 + self.y**2)

    def unitVector(self):
        return vec(self.x / self.mag(), self.y / self.mag())

    def vectorTo(self, other):
        return vec(other.x - self.x, other.y - self.y)

    def asTuple(self):
        return (self.x, self.y)

    def getValues(self):
        return self.x, self.y

    def angleWith(self, other):
        return math.acos((self.x * other.x + self.y * other.y) / (self.mag() * other.mag()))

    def getPerpendicular(self):
        return vec(-self.y, self.x)