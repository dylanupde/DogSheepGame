import math

from math import sqrt

class Vector:
	def __init__(self, x, y):
		self.x = x
		self.y = y

	def __str__(self):
		return 'Vector (%f, %f)' % (self.x, self.y)

	def __add__(self,other):
		return Vector(self.x + other.x, self.y + other.y)

	def __sub__(self,other):
		return Vector(self.x - other.x, self.y - other.y)

	def dot(self, other):
		return self.x * other.x + self.y * other.y

	def scale(self, scalar):
		return Vector(self.x * scalar, self.y * scalar)

	def length(self):
		return math.sqrt(self.dot(self))

	def normalize(self):
		len = self.length()
		if not len == 0:
			return Vector(self.x / len, self.y / len)
		else:
			return Vector(self.x, self.y)

	def lerp(self, end, percent):
		 return self + (end - self).scale(percent)