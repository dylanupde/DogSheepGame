import pygame
import Vector
import random
import Constants

from Vector import Vector
from DrawableObject import *

class Agent(DrawableObject):

	def __init__(self, image, position, size, color, speed, angularSpeed):
		super().__init__(image, position, size, color)
		self.maxSpeed = speed
		self.speed = 0
		self.angularSpeed = angularSpeed
		self.velocity = Vector(random.random() - 0.5, random.random() - 0.5).normalize()
		self.target = Vector(0, 0)
		self.targetVelocity = self.velocity

	def __str__(self):
		return 'Agent (%d, %d, %d, %d)' % (self.size, self.center, self.velocity)

	def setVelocity(self, velocity):
		self.targetVelocity = velocity.normalize()

	def moveTowardTargetVelocity(self):
		velocityDiff = self.targetVelocity - self.velocity
		if (velocityDiff.length() < self.angularSpeed):
			self.velocity = self.targetVelocity
		else:
			#self.velocity = self.velocity.lerp(self.targetVelocity, self.angularSpeed / velocityDiff.length())
			self.velocity += velocityDiff.normalize().scale(self.angularSpeed)
		self.velocity = self.velocity.normalize()

	def update(self, gameState):
		self.moveTowardTargetVelocity()
		self.center = self.center + self.velocity.scale(self.speed)

		# Check to make sure the object is still in the bounds of the world
		self.center.x = max(self.boundingRect.width * 0.5, min(self.center.x, gameState.getWorldBounds().x - self.boundingRect.width * 0.5))
		self.center.y = max(self.boundingRect.height * 0.5, min(self.center.y, gameState.getWorldBounds().y - self.boundingRect.height * 0.5))
		self.calcSurface()

	def draw(self, screen):
		self.angle = math.degrees(math.atan2(-self.velocity.y, self.velocity.x)) - 90
		super().draw(screen)
		if Constants.DEBUG_VELOCITY:
			# draw the bounding rect
			pygame.draw.line(screen, self.color, (self.center.x, self.center.y), 
					   (self.center.x + (self.velocity.x * self.boundingRect.width * 2), 
						self.center.y + (self.velocity.y * self.boundingRect.height * 2)), 
						Constants.DEBUG_LINE_WIDTH)

