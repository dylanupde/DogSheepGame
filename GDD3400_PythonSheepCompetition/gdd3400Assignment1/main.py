import pygame
import random
import Vector
import Agent
import Dog
import Sheep
import Constants
import Graph
import Node
import GameState

from Constants import *
from pygame import *
from random import *
from Vector import *
from Agent import *
from Sheep import *
from Dog import *
from Graph import *
from Node import *
from GameState import *

#################################################################################
# Helper Functions
#################################################################################

# Build the gate and the pen procedurally, add it to the graph
def buildGates(graph):
	X = 0
	Y = 1
	# Add the gates to the game
	# pick one end, then pick the second end about 50 spaces away (pick a direction, generate the far end
	for gate in PEN:
		graph.placeObstacle(Vector(gate[0][X], gate[0][Y]), (0, 255, 0))
		graph.placeObstacle(Vector(gate[1][X], gate[1][Y]), (255, 0, 0))
		print("Placing Obstacles: " + str(gate[0]) + " " + str(gate[1]))

	# Initialize Pen Collision Rectangles
	penBounds = []

	# Add the final pen based on the final gate
	finalGate = gate[-2:]
	# If the gate is horizontally arranged
	if finalGate[0][Y] == finalGate[1][Y]:
		# If the green gate (the first gate) is on the right, paddock goes "up"
		if finalGate[0][X] > finalGate[1][X]:
			direction = -1

			# Create the gate's "entrance" collider
			penBounds.append(pygame.Rect(finalGate[1][X] + GRID_SIZE * 0.5, finalGate[1][Y] - GRID_SIZE * 0.5, \
											finalGate[0][X] - finalGate[1][X] - GRID_SIZE, GRID_SIZE))

			# Create the pen's "inside" collider
			penBounds.append(pygame.Rect(finalGate[1][X] + GRID_SIZE * 0.5, finalGate[1][Y] - PEN_DEPTH + GRID_SIZE * 0.5, \
											finalGate[0][X] - finalGate[1][X] - GRID_SIZE, PEN_DEPTH - GRID_SIZE * 2))
		else:
			direction = 1
			# Create the gate's "entrance" collider
			penBounds.append(pygame.Rect(finalGate[0][X] + GRID_SIZE * 0.5, finalGate[1][Y] - GRID_SIZE * 0.5, \
											finalGate[1][X] - finalGate[0][X] - GRID_SIZE, GRID_SIZE))

			# Create the pen's "inside" collider
			penBounds.append(pygame.Rect(finalGate[0][X] + GRID_SIZE * 0.5, finalGate[0][Y] + GRID_SIZE * 0.5, \
											finalGate[1][X] - finalGate[0][X] - GRID_SIZE, PEN_DEPTH - GRID_SIZE * 2))

		# Draw the two sides of the pen
		for y in range(finalGate[0][Y] + direction * GRID_SIZE, finalGate[0][Y] + direction * PEN_DEPTH, direction * GRID_SIZE):
			graph.placeObstacle(Vector(finalGate[0][X], y), (0, 0, 0))
			graph.placeObstacle(Vector(finalGate[1][X], y), (0, 0, 0))

		# Draw the far-end of the pen
		for x in range(finalGate[0][X] + direction * GRID_SIZE, finalGate[1][X], direction * GRID_SIZE):
			graph.placeObstacle(Vector(x, finalGate[0][Y] + direction * (PEN_DEPTH - GRID_SIZE)), (0, 0, 0))

	# Return the two collision rectangles that represent the pen
	return penBounds

# Create all of the obstacles in the world and add them to the graph
def buildObstacles(graph):
	# Random Obstacles
	for i in range(NBR_RANDOM_OBSTACLES):
		start = Vector(randrange(0, WORLD_WIDTH), randrange(0, WORLD_HEIGHT))
		graph.placeObstacle(start, (0, 0, 0))
		# For the number of obstacles in this clump
		for j in range(randrange(NBR_CLUMPED_OBSTACLES)):
			start += Vector((randrange(3) - 1) * GRID_SIZE, (randrange(3) - 1) * GRID_SIZE)
			# While the obstacle is invalid, create another
			while(start.x >= WORLD_WIDTH - GRID_SIZE or start.y >= WORLD_HEIGHT - GRID_SIZE):
				start += Vector((randrange(3) - 1) * GRID_SIZE, (randrange(3) - 1) * GRID_SIZE)
			graph.placeObstacle(start, (0, 0, 0))

#################################################################################
# Main Functionality
#################################################################################

pygame.init();

# Comment-in this line if you want to test on the same exact configuration of
# objects as the last time.  Change the number to test out some variations
#random.seed(100)

# Set up the visual world
screen = pygame.display.set_mode((WORLD_WIDTH, WORLD_HEIGHT))
clock = pygame.time.Clock()
sheepImage = pygame.image.load('sheep.png')
dogImage = pygame.image.load('dog.png')
worldBounds = Vector(WORLD_WIDTH, WORLD_HEIGHT)

# Setup the graph
graph = Graph()

# Setup the gates and obstacles
penBounds = buildGates(graph)
buildObstacles(graph)
atEntrance = []

# Setup the dog
dog = Dog(dogImage, 
		  Vector(WORLD_WIDTH * .5, WORLD_HEIGHT * .5), 
		  Vector(DOG_WIDTH, DOG_HEIGHT), 
		  (0, 255, 0), 
		  DOG_SPEED, 
		  DOG_ANGULAR_SPEED)

# Setup the sheep (only 1 for now...)
herd = []
while len(herd) < Constants.SHEEP_COUNT:
	sheep = Sheep(sheepImage, 
					Vector(randrange(int(worldBounds.x * .05), int(worldBounds.x * .95)), 
							randrange(int(worldBounds.y * .05), int(worldBounds.y * .95))), 
					Vector(DOG_WIDTH, DOG_HEIGHT), 
					(0, 255, 0), 
					SHEEP_SPEED, 
					SHEEP_ANGULAR_SPEED)
	if not (sheep.boundingRect.colliderect(penBounds[0]) or sheep.boundingRect.colliderect(penBounds[1])):
		herd.append(sheep)

# Setup the "winning" message and time
font = pygame.font.SysFont('courier new', 32)

# While the user has not selected quit
gameState = GameState()
hasQuit = False
startTime = time.get_ticks()
while not hasQuit:
	# Clear the screen
	screen.fill(BACKGROUND_COLOR)

	# Process all in-game events
	for event in pygame.event.get():
		if event.type == pygame.QUIT \
			or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
			hasQuit = True

	# Update the GameState Object
	gameState.update(worldBounds, graph, dog, herd, penBounds)

	# Update the agents onscreen
	dog.update(gameState)
	for sheep in herd:
		sheep.update(gameState)	

	# Draw the agents onscreen
	graph.draw(screen)
	dog.draw(screen)
	for sheep in herd:
		sheep.draw(screen)

	# Draw the Goal colliders
	pygame.draw.rect(screen, (255, 0, 25), penBounds[1], 6)
	pygame.draw.rect(screen, (0, 0, 255), penBounds[0], 6)

	# See if one of the sheep has arrived in the pen by going through the gate
	for sheep in herd:
		# If the sheep is not at the entrance
		if sheep not in atEntrance:
			# If the sheep is colliding with the entrance to the pen, mark that sheep
			if sheep.boundingRect.colliderect(penBounds[0]):
				atEntrance.append(sheep)
		# If the sheep is at the entrance
		else:
			# If the sheep is also in the pen, remove the sheep
			if sheep.boundingRect.colliderect(penBounds[1]):
				herd.remove(sheep)
			# If they're not longer colliding with the entrance,
			# assume they have moved away from the entrance
			elif not sheep.boundingRect.colliderect(penBounds[0]):
				atEntrance.remove(sheep)
					   
	# Display the time since the game started
	endTime = time.get_ticks()
	elapsedTime = (endTime - startTime) / 1000
	text = font.render('%13s' % (' Time: ' + str(elapsedTime)).ljust(13,' '), True, (0, 255, 0), (0, 0, 255)) 
	textRect = text.get_rect()  
	textRect.center = (WORLD_WIDTH // 2, 25) 
	screen.blit(text, textRect) 

	# If all the sheep have been captured, the player has won!
	if len(herd) == 0:
		hasQuit = True
		print('Final Time: ' + str(elapsedTime))

	# Double buffer
	pygame.display.flip()

	# Limit to 60 FPS
	clock.tick(FRAME_RATE)

# Quit
pygame.quit()