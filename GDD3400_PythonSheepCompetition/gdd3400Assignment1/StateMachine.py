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

class StateMachine:
	""" Machine that manages the set of states and their transitions """

	def __init__(self, startState):
		""" Initialize the state machine and its start state"""
		self.__currentState = startState
		self.__currentState.enter()



	def getCurrentState(self):
		""" Get the current state """
		return self.__currentState



	def update(self, gameState):
		""" Run the update on the current state and determine if we should transition """
		nextState = self.__currentState.update(gameState)

		# If the nextState that is returned by current state's update is not the same
		# state, then transition to that new state
		if nextState != None and type(nextState) != type(self.__currentState):
			self.transitionTo(nextState)



	def transitionTo(self, nextState):
		""" Transition to the next state """
		self.__currentState.exit()
		self.__currentState = nextState
		self.__currentState.enter()



	def draw(self, screen):
		""" Draw any debugging information associated with the states """
		self.__currentState.draw(screen)






class State:
	def enter(self):
		""" Enter this state, perform any setup required """
		print("Entering " + self.__class__.__name__)
		
	def exit(self):
		""" Exit this state, perform any shutdown or cleanup required """
		print("Exiting " + self.__class__.__name__)

	def update(self, gameState):
		""" Update this state, before leaving update, return the next state """
		#print("Updating " + self.__class__.__name__)

	def draw(self, screen):
		""" Draw any debugging info required by this state """
		pass

			
	
class FindTarget(State):
	""" This is an example state that simply picks the first sheep to target """

	def update(self, gameState):
		""" Update this state using the current gameState """
		super().update(gameState)
		dog = gameState.getDog()
		graph = gameState.getGraph()

		# Pick the closest sheep
		if dog.targetSheep == None:
			closestSheep = gameState.getHerd()[0]
			closestSheepDistance = (closestSheep.center - dog.center).length()
			dog.setTargetSheep(gameState.getHerd()[0])
			for thisSheep in gameState.getHerd():
				distanceFromDog = (thisSheep.center - dog.center).length()
				if distanceFromDog < closestSheepDistance:
					closestSheep = thisSheep
					closestSheepDistance = distanceFromDog
			dog.setTargetSheep(closestSheep)


		# Set the target for the pupper
		sheepTargetLocation = None
		# Check the top (BLUE) section
		if dog.targetSheep.center.y < 304:
		    sheepTargetLocation = Constants.FENCE_GOAL_COORD
		else:
			# Check the left (RED) section
			if dog.targetSheep.center.x < 432:
			    sheepTargetLocation = Constants.FENCE_GOAL_1
			else:
				# Check the GREEN section
				if dog.targetSheep.center.x < 520 and dog.targetSheep.center.y > 464:
				    sheepTargetLocation = Constants.FENCE_GOAL_3
				else:
					# Check the YELLOW section
					if dog.targetSheep.center.x <= 608 and dog.targetSheep.center.y > 464:
					    sheepTargetLocation = Constants.FENCE_GOAL_4
					else:
						# Check the ORANGE section
						if dog.targetSheep.center.x > 608:
						    sheepTargetLocation = Constants.FENCE_GOAL_2
		# If none of those take, then the shoop must be in the pen! That big silly shoop
		if sheepTargetLocation == None:
		    sheepTargetLocation = Constants.FENCE_GOAL_COORD

		# Get the our potential targets to go to!
		myUltimateTargetLocation = None
		dogsDistanceToSheepTargetLocation = (dog.center - sheepTargetLocation).length()
		sheepsDistanceToSheepTargetLocation = (dog.targetSheep.center - sheepTargetLocation).length()
		# If the dog is closer to the sheeps goal...
		#if dogsDistanceToSheepTargetLocation < sheepsDistanceToSheepTargetLocation:
		if dogsDistanceToSheepTargetLocation < sheepsDistanceToSheepTargetLocation:
			normalizedVectorFromSheepToDog = (dog.center - dog.targetSheep.center).normalize()
			vectorToAddToSheep = (Vector(-normalizedVectorFromSheepToDog.y, normalizedVectorFromSheepToDog.x)).scale(Constants.SHEEP_MIN_FLEE_DIST + 20)
			dogTargetLocation1 = dog.targetSheep.center + vectorToAddToSheep
			dogTargetLocation2 = dog.targetSheep.center - vectorToAddToSheep
			distFromSheepTargetLocationToTarget1 = (sheepTargetLocation - dogTargetLocation1).length()
			distFromSheepTargetLocationToTarget2 = (sheepTargetLocation - dogTargetLocation2).length()
			if distFromSheepTargetLocationToTarget1 < distFromSheepTargetLocationToTarget2:
			    myUltimateTargetLocation = dogTargetLocation2
			else:
				myUltimateTargetLocation = dogTargetLocation1
		else:
			vectorFromSheepToGoalNormalized = (sheepTargetLocation - dog.targetSheep.center).normalize()
			vectorToAddToSheep = vectorFromSheepToGoalNormalized.scale(Constants.SHEEP_MIN_FLEE_DIST - Constants.DOG_GO_AROUND_DIST)
			myUltimateTargetLocation = dog.targetSheep.center - vectorToAddToSheep

		# Make sure our ULTIMATE target location isn't out of bounds
		myUltimateTargetLocation = self.ClampVectorWithinScreen(myUltimateTargetLocation)
		
		# If we're in an unwalkable spot, get all spots around it
		while graph.getNodeFromPoint(myUltimateTargetLocation).isWalkable == False:
			print("Unwalkable spot! Trying a nearby spot")
			myUltimateTargetLocation.x = myUltimateTargetLocation.x + Constants.GRID_SIZE
			myUltimateTargetLocation = self.ClampVectorWithinScreen(myUltimateTargetLocation)
			if graph.getNodeFromPoint(myUltimateTargetLocation).isWalkable == False:
				myUltimateTargetLocation.x = myUltimateTargetLocation.x - ( 2 * Constants.GRID_SIZE )
				if graph.getNodeFromPoint(myUltimateTargetLocation).isWalkable == False:
					myUltimateTargetLocation.x = myUltimateTargetLocation.x + Constants.GRID_SIZE
					myUltimateTargetLocation.y = myUltimateTargetLocation.y + Constants.GRID_SIZE
					if graph.getNodeFromPoint(myUltimateTargetLocation).isWalkable == False:
					    myUltimateTargetLocation.y = myUltimateTargetLocation.y - ( 2 * Constants.GRID_SIZE )


		dog.calculatePathToNewTarget(myUltimateTargetLocation)

		# If there's no path, return this to try again next frame. Otherwise, move on to following the path!
		if len(dog.path) > 0:
		    return FollowingPath()
		else:
			print("Can't get to node at", graph.getNodeFromPoint(myUltimateTargetLocation))
			return FindTarget()


	def ClampVectorWithinScreen(self, inputVector):
		vectorToOutput = inputVector
		if vectorToOutput.x < 1:
			vectorToOutput.x = 1
		elif vectorToOutput.x > Constants.WORLD_WIDTH:
			vectorToOutput.x = Constants.WORLD_WIDTH - 2
		if vectorToOutput.y < 1:
			vectorToOutput.y = 1
		elif vectorToOutput.y > Constants.WORLD_HEIGHT:
			vectorToOutput.y = Constants.WORLD_HEIGHT - 2
		return vectorToOutput



class Idle(State):
	""" This is an idle state where the dog does nothing """

	def update(self, gameState):
		super().update(gameState)
		print("Hey im idle lol")
		
		# If the dog isn't following and there's sheep, return FindSheepState
		if not gameState.getDog().isFollowingPath and len(gameState.getHerd()) > 0:
			print("Golly! I should herd a sheep!")
			return FindTarget()
		else :
			return Idle()



class FollowingPath(State):
	"""A state where the doggo just follows a path"""

	def update(self, gameState):
		super().update(gameState)
		dog = gameState.getDog()

		if dog.targetSheep == None:
		    return Idle()
		elif not dog.isFollowingPath:
			return FindTarget()
		else:
			return FollowingPath()