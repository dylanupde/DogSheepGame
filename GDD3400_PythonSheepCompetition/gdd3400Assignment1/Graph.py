import Constants
import Node
import pygame
import Vector

from pygame import *
from Vector import *
from Node import *
from enum import Enum

class Graph():
	def __init__(self):
		""" Initialize the Graph """
		self.nodes = []			# Set of nodes
		self.obstacles = []		# Set of obstacles - used for collision detection

		# Initialize the size of the graph based on the world size
		self.gridWidth = int(Constants.WORLD_WIDTH / Constants.GRID_SIZE)
		self.gridHeight = int(Constants.WORLD_HEIGHT / Constants.GRID_SIZE)

		# Create grid of nodes
		for i in range(self.gridHeight):
			row = []
			for j in range(self.gridWidth):
				node = Node(i, j, Vector(Constants.GRID_SIZE * j, Constants.GRID_SIZE * i), Vector(Constants.GRID_SIZE, Constants.GRID_SIZE))
				row.append(node)
			self.nodes.append(row)

		## Connect to Neighbors
		for i in range(self.gridHeight):
			for j in range(self.gridWidth):
				# Add the top row of neighbors
				if i - 1 >= 0:
					# Add the upper left
					if j - 1 >= 0:		
						self.nodes[i][j].neighbors += [self.nodes[i - 1][j - 1]]
					# Add the upper center
					self.nodes[i][j].neighbors += [self.nodes[i - 1][j]]
					# Add the upper right
					if j + 1 < self.gridWidth:
						self.nodes[i][j].neighbors += [self.nodes[i - 1][j + 1]]

				# Add the center row of neighbors
				# Add the left center
				if j - 1 >= 0:
					self.nodes[i][j].neighbors += [self.nodes[i][j - 1]]
				# Add the right center
				if j + 1 < self.gridWidth:
					self.nodes[i][j].neighbors += [self.nodes[i][j + 1]]
				
				# Add the bottom row of neighbors
				if i + 1 < self.gridHeight:
					# Add the lower left
					if j - 1 >= 0:
						self.nodes[i][j].neighbors += [self.nodes[i + 1][j - 1]]
					# Add the lower center
					self.nodes[i][j].neighbors += [self.nodes[i + 1][j]]
					# Add the lower right
					if j + 1 < self.gridWidth:
						self.nodes[i][j].neighbors += [self.nodes[i + 1][j + 1]]

	def getNodeFromPoint(self, point):
		""" Get the node in the graph that corresponds to a point in the world """
		point.x = max(0, min(point.x, Constants.WORLD_WIDTH - 1))
		point.y = max(0, min(point.y, Constants.WORLD_HEIGHT - 1))

		# Return the node that corresponds to this point
		return self.nodes[int(point.y/Constants.GRID_SIZE)][int(point.x/Constants.GRID_SIZE)]

	def placeObstacle(self, point, color):
		""" Place an obstacle on the graph """
		node = self.getNodeFromPoint(point)

		# If the node is not already an obstacle, make it one
		if node.isWalkable:
			# Indicate that this node cannot be traversed
			node.isWalkable = False		

			# Set a specific color for this obstacle
			node.color = color
			for neighbor in node.neighbors:
				neighbor.neighbors.remove(node)
			node.neighbors = []
			self.obstacles += [node]

	def reset(self):
		""" Reset all the nodes for another search """
		for i in range(self.gridHeight):
			for j in range(self.gridWidth):
				self.nodes[i][j].reset()

	def buildPath(self, endNode):
		""" Go backwards through the graph reconstructing the path """
		path = []
		node = endNode
		while node is not 0:
			node.isPath = True
			path = [node] + path
			node = node.backNode

		# If there are nodes in the path, reset the colors of start/end
		if len(path) > 0:
			path[0].isPath = False
			path[0].isStart = True
			path[-1].isPath = False
			path[-1].isEnd = True
		return path

	def findPath_Breadth(self, startNode, endNode):
		""" Breadth Search """
		print("BREADTH-FIRST")
		self.reset()
		
		startNode = self.getNodeFromPoint(startNode)
		endNode = self.getNodeFromPoint(endNode)

		startNode.isStart = True
		endNode.isEnd = True

		toVisit = [startNode]
		startNode.isVisited = True

		while len(toVisit) != 0:
			#print("startNodes backnode is: ", startNode.backNode)
			currentNode = toVisit[0]
			toVisit.pop(0)
			currentNode.isExplored = True

			for nextNode in currentNode.neighbors:
				if not nextNode.isVisited:
					toVisit.append(nextNode)
					nextNode.isVisited = True
					nextNode.backNode = currentNode
					if nextNode == endNode:
						return self.buildPath(endNode)

		return []


	def findPath_Dijkstra(self, startNode, endNode):
		""" Dijkstra's Search """
		print("DJIKSTRA")
		self.reset()
		return self.findPath_AStarOrDjikstra(startNode, endNode, False)


	def findPath_AStar(self, startNode, endNode):
		""" A Star Search """
		print("A*")
		self.reset()
		return self.findPath_AStarOrDjikstra(startNode, endNode, True)


	def findPath_BestFirst(self, startNode, endNode):
		""" Best First Search """
		print("BEST_FIRST")
		self.reset()
		
		startNode = self.getNodeFromPoint(startNode)
		endNode = self.getNodeFromPoint(endNode)

		startNode.isStart = True
		endNode.isEnd = True

		toVisit = [startNode]
		startNode.isVisited = True
		startNode.cost = 0

		while len(toVisit) != 0:
			currentNode = toVisit[0]
			toVisit.pop(0)
			currentNode.isExplored = True

			for nextNode in currentNode.neighbors:
				nextNode.cost = (nextNode.center - endNode.center).length()

				#print(currentDistance)
				if nextNode.isVisited == False:
					nextNode.isVisited = True
					nextNode.backNode = currentNode

					toVisit.append(nextNode)
					toVisit = sorted(toVisit, key=lambda thisNode: thisNode.cost)
					#print("PRINTING COST LIST!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
					#for thisNodeOk in toVisit:
					#    print(thisNodeOk.cost)

				if nextNode == endNode:
					return self.buildPath(endNode)

		return []


	def findPath_AStarOrDjikstra(self, startNode, endNode, actuallyDoingAStar):
		""" Djikstra's Search """
		self.reset()
		
		startNode = self.getNodeFromPoint(startNode)
		endNode = self.getNodeFromPoint(endNode)
		
		startNode.isStart = True
		endNode.isEnd = True

		toVisit = [startNode]
		startNode.isVisited = True
		startNode.cost = 0

		while len(toVisit) != 0:
			currentNode = toVisit[0]
			toVisit.pop(0)
			currentNode.isExplored = True

			for nextNode in currentNode.neighbors:
				moveCost = (nextNode.center - currentNode.center).length()
				totalCost = moveCost + currentNode.cost

				if actuallyDoingAStar:
					remainingDist = (nextNode.center - endNode.center).length()
					totalCost += remainingDist

				#print(currentDistance)
				if nextNode.isVisited == False:
					nextNode.isVisited = True
					nextNode.backNode = currentNode
					nextNode.cost = totalCost

					toVisit.append(nextNode)
					toVisit = sorted(toVisit, key=lambda thisNode: thisNode.cost)
					#print("PRINTING COST LIST!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
					#for thisNodeOk in toVisit:
					#    print(thisNodeOk.cost)
				else:
					if totalCost < nextNode.cost:
						nextNode.cost = totalCost
						nextNode.backNode = currentNode

				if nextNode == endNode:
					return self.buildPath(endNode)

		return []

	def draw(self, screen):
		""" Draw the graph """
		for i in range(self.gridHeight):
			for j in range(self.gridWidth):
				self.nodes[i][j].draw(screen)