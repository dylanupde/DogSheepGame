import pygame
import Vector
import StateMachine

from Vector import Vector
from Agent import *
from enum import Enum
from pygame import *
from StateMachine import *

class SearchType(Enum):
	BREADTH = 1
	DJIKSTRA = 2
	BEST = 3
	A_STAR = 4 

class Dog(Agent):
	""" The herding dog """

	def __init__(self, image, position, size, color, speed, angularSpeed):
		""" Initialize the dog """
		super().__init__(image, position, size, color, speed, angularSpeed)
		self.searchType = SearchType.A_STAR
		self.gateNumber = 0
		self.isFollowingPath = False
		self.path = []
		self.stateMachine = StateMachine(FindSheepState())
		self.targetSheep = None

	def setTargetSheep(self, sheep):
		""" Set the sheep that the dog is currently targetting """
		self.targetSheep = sheep

	def getTargetSheep(self):
		""" Return the sheep that the dog is currently targetting """
		return self.targetSheep

	def getPathLength(self):
		""" Get the length of the dog's current path, if zero, the dog doesn't have a path """
		return len(self.path)

	def calculatePathToNewTarget(self, target):
		""" Calculate the path to the new target """
		if self.searchType == SearchType.BREADTH:
			self.path = self.graph.findPath_Breadth(self.center, target)
		elif self.searchType == SearchType.DJIKSTRA:
			self.path = self.graph.findPath_Dijkstra(self.center, target)
		elif self.searchType == SearchType.BEST:
			self.path = self.graph.findPath_BestFirst(self.center, target)
		elif self.searchType == SearchType.A_STAR:
			self.path = self.graph.findPath_AStar(self.center, target)

		# If the path exists, head toward the first node in the path
		if len(self.path) > 0:
			self.isFollowingPath = True
			self.target = self.path.pop(0).center
			self.speed = self.maxSpeed

	def update(self, gameState):
		""" Update the dog based on the gameState """

		# Update the state machine
		self.stateMachine.update(gameState)
		self.graph = gameState.getGraph()

		# Select one of the searches based on user input
		if pygame.key.get_pressed()[K_f]:
			self.searchType = SearchType.BREADTH
		elif pygame.key.get_pressed()[K_d]:
			self.searchType = SearchType.DJIKSTRA
		elif pygame.key.get_pressed()[K_s]:
			self.searchType = SearchType.BEST
		elif pygame.key.get_pressed()[K_a]:
			self.searchType = SearchType.A_STAR

		# If we are following the path
		if self.isFollowingPath:
			vectorToTarget = self.target - self.center
			# if we've arrived at the first location in the path
			if (vectorToTarget).length() <= Constants.GRID_SIZE * .5:
				# Go to next position in path, if there is one
				if len(self.path) > 0:
					self.target = self.path.pop(0).center
				# Stop following the path if it is empty
				else:
					self.isFollowingPath = False
					self.speed = 0
			else:
				self.setVelocity(vectorToTarget)

		super().update(gameState)

	def draw(self, screen):
		""" Draw the dog """
		super().draw(screen)
		self.stateMachine.draw(screen)

		# Draw a line from the dog to the sheep it is targetting.
		if Constants.DEBUG_DOG_TARGET and self.targetSheep != None:
			pygame.draw.line(screen, (255, 0, 0), (self.center.x, self.center.y), 
				(self.targetSheep.center.x, self.targetSheep.center.y), DEBUG_DOG_TARGET_LINE_WIDTH)

