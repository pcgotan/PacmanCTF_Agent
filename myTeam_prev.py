# myTeam.py
# ---------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from captureAgents import CaptureAgent
import random
import time
import util
from util import nearestPoint
from game import Directions
import game

#################
# Team creation #
#################


def createTeam(firstIndex, secondIndex, isRed,
               first='OffensiveAgent', second='DefensiveAgent'):
    """
    This function should return a list of two agents that will form the
    team, initialized using firstIndex and secondIndex as their agent
    index numbers.  isRed is True if the red team is being created, and
    will be False if the blue team is being created.
    As a potentially helpful development aid, this function can take
    additional string-valued keyword arguments ("first" and "second" are
    such arguments in the case of this function), which will come from
    the --redOpts and --blueOpts command-line arguments to capture.py.
    For the nightly contest, however, your team will be created without
    any extra arguments, so you should make sure that the default
    behavior is what you want for the nightly contest.
    """

    # The following line is an example only; feel free to change it.
    return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########


class MySmartAgent(CaptureAgent):
    """
    A base class for search agents that chooses score-maximizing actions.
    """

    def registerInitialState(self, gameState):

        CaptureAgent.registerInitialState(self, gameState)
        self.boundary_top = True
        if gameState.getAgentState(self.index).getPosition()[0] == 1:
            self.isRed = True
        else:
            self.isRed = False

        self.boundaries = self.boundaryTravel(gameState)
        self.treeDepth = 3

    def chooseAction(self, gameState):
        """
        Picks among the actions with the highest Q(s,a).
        """
        actions = gameState.getLegalActions(self.index)

        # You can profile your evaluation time by uncommenting these lines
        start = time.time()
        values = [self.evaluate(gameState, a) for a in actions]
        if time.time() - start > 0.9:
            print 'eval time for agent %d: %.4f' % (
                self.index, time.time() - start)
        maxValue = max(values)

        bestActions = [action for action, value in zip(
            actions, values) if value == maxValue]

        return random.choice(bestActions)

    def getSuccessor(self, gameState, action):
        """
        Finds the next successor which is a grid position (location tuple).
        """
        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentState(self.index).getPosition()
        if pos != nearestPoint(pos):
            # Only half a grid position was covered
            return successor.generateSuccessor(self.index, action)
        else:
            return successor

    def evaluate(self, gameState, action):
        """
        Computes a linear combination of features and feature weights
        """
        features = self.getFeatures(gameState, action)
        weights = self.getWeights(gameState, action)
        return features * weights

    def getFeatures(self, gameState, action):
        """
        Returns a counter of features for the state
        """
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)
        features['successorScore'] = self.getScore(successor)
        return features

    def getWeights(self, gameState, action):
        """
        Normally, weights do not depend on the gamestate.  They can be either
        a counter or a dictionary.
        """
        return {'successorScore': 1.0}

    def boundaryTravel(self, gameState):
        return (0, 0), (0, 0)


class OffensiveAgent(MySmartAgent):
    """
    A reflex agent that seeks food. This is an agent
    we give you to get an idea of what an offensive agent might look like,
    but it is by no means the best or only way to build an offensive agent.
    """

    def getAction(self, gameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction
        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        opponents = {}
        for enemy in self.getOpponents(gameState):
            opponents[enemy] = gameState.getAgentState(enemy).getPosition()
        directions = {'north': (0, 1), 'south': (
            0, -1), 'east': (1, 0), 'west': (-1, 0)}
        ghost_weights = {'distance': 5, 'scared': 5}

        def get_ghost_actions(current_pos):
            walls = gameState.getWalls().asList()

            max_x = max([wall[0] for wall in walls])
            max_y = max([wall[1] for wall in walls])

            actions = []
            for direction in directions:
                action = directions[direction]
                new_pos = (int(current_pos[0] + action[0]),
                           int(current_pos[1] + action[1]))
                if new_pos not in walls:
                    if (1 <= new_pos[0] < max_x) and (1 <= new_pos[1] < max_y):
                        actions.append(direction.title())
            return actions

        def get_new_position(current_pos, action):
            act = directions[[direction for direction in directions if str(
                action).lower() == direction][0]]
            return (current_pos[0] + act[0], current_pos[1] + act[1])

        def expectation(gamestate, position, legalActions):
            ghost_dict = {}
            for action in legalActions:
                newPos = get_new_position(position, action)
                ghost_dict[action] = self.getMazeDistance(
                    position, newPos) * ghost_weights['distance']

            min_action = min(ghost_dict)

            # print (ghost_dict)
            # print (min_action)
            # time.sleep(5)

            for action in ghost_dict:
                if ghost_dict[action] == min_action:
                    ghost_dict[action] = .8
                else:
                    ghost_dict[action] = .2/len(legalActions)
            return ghost_dict

        def ghost_eval(gamestate, opponents, opponent):
            newPos = opponents[opponent]
            enemy = gamestate.getAgentState(opponent)
            myPos = gamestate.getAgentState(self.index).getPosition()

            if enemy.scaredTimer != 0:
                distance = - self.getMazeDistance(myPos, newPos) * \
                    ghost_weights['distance']

            else:
                distance = self.getMazeDistance(
                    myPos, newPos)*ghost_weights['distance']
            return distance

        def minimax(gamestate, depth, agent, opponents, alpha=-float('inf'), beta=float('inf')):
            """
            """
            # Get legal moves per agent
            legalActions = [action for action in gamestate.getLegalActions(
                self.index) if action != Directions.STOP]

            # Generate optimal action recursively
            actions = {}
            if agent == self.index:
                maxVal = -float('inf')
                for action in legalActions:
                    eval = self.evaluate(gamestate, action)
                    if depth == self.treeDepth:
                        value = eval
                    else:
                        value = eval + \
                            minimax(self.getSuccessor(gamestate, action),
                                    depth, agent+1, opponents, alpha, beta)
                    maxVal = max(maxVal, value)
                    if beta < maxVal:
                        return maxVal
                    else:
                        alpha = max(alpha, maxVal)
                    if depth == 1:
                        actions[value] = action
                if depth == 1:          # If you're up to the first depth, return a legal action
                    return actions[maxVal]
                return maxVal
            else:
                minVal = float('inf')
                for opponent in opponents:
                    if gamestate.getAgentState(opponent).getPosition() is not None:
                        legalActions = get_ghost_actions(opponents[opponent])
                        expectations = expectation(
                            gamestate, opponents[opponent], legalActions)
                        for action in legalActions:
                            new_opponents = opponents.copy()
                            new_opponents[opponent] = get_new_position(
                                opponents[opponent], action)
                            ghost_val = ghost_eval(
                                gamestate, new_opponents, opponent)*expectations[action]
                            value = ghost_val + \
                                minimax(gamestate, depth+1, self.index,
                                        new_opponents, alpha, beta)
                            minVal = min(minVal, value)
                            if minVal < alpha:
                                return minVal
                            else:
                                beta = min(beta, minVal)
                if minVal == float('inf'):
                    return 0
                return minVal

        return minimax(gameState, 1, self.index, opponents)

    def getFeatures(self, gameState, action):
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)
        features['successorScore'] = self.getScore(successor)

        myState = successor.getAgentState(self.index)
        myPos = myState.getPosition()

        # Computes distance to enemy ghosts
        enemies = [successor.getAgentState(i)
                   for i in self.getOpponents(successor)]
        ghosts = [a for a in enemies if not a.isPacman and a.getPosition()
                  != None]
        invaders = [a for a in enemies if a.isPacman and a.getPosition()
                    != None]

        features['invaderDistance'] = 0.0
        if len(invaders) > 0:
            features['invaderDistance'] = min([self.getMazeDistance(
                myPos, invader.getPosition()) for invader in invaders]) + 1

        if len(ghosts) > 0:
            ghostEval = 0.0
            scaredDistance = 0.0
            regGhosts = [ghost for ghost in ghosts if ghost.scaredTimer == 0]
            scaredGhosts = [ghost for ghost in ghosts if ghost.scaredTimer > 0]
            if len(regGhosts) > 0:
                ghostEval = min([self.getMazeDistance(
                    myPos, ghost.getPosition()) for ghost in regGhosts])
                if ghostEval <= 1:
                    ghostEval = -float('inf')

            if len(scaredGhosts) > 0:
                scaredDistance = min([self.getMazeDistance(
                    myPos, ghost.getPosition()) for ghost in scaredGhosts])
            if scaredDistance < ghostEval or ghostEval == 0:

                if scaredDistance == 0:
                    features['ghostScared'] = -10
            features['distanceToGhost'] = ghostEval

        # Compute distance to the nearest food
        foodList = self.getFood(successor).asList()
        if len(foodList) > 0:  # This should always be True,  but better safe than sorry
            minDistance = min([self.getMazeDistance(myPos, food)
                               for food in foodList])
            features['distanceToFood'] = minDistance
            features['foodRemaining'] = len(foodList)

        # Compute distance to capsules
        capsules = self.getCapsules(gameState)
        if len(capsules) > 0:
            minDistance = min([self.getMazeDistance(myPos, capsule)
                               for capsule in capsules])
            if minDistance == 0:
                minDistance = -100
            features['distanceToCapsules'] = minDistance

        if action == Directions.STOP:
            features['stop'] = 1
        rev = Directions.REVERSE[gameState.getAgentState(
            self.index).configuration.direction]
        if action == rev:
            features['reverse'] = 1

        return features

    def getWeights(self, gameState, action):
        return {'successorScore': 100, 'invaderDistance': -50, 'distanceToFood': -1, 'foodRemaining': -1, 'distanceToGhost': 2, 'ghostScared': -1, 'distanceToCapsules': -1, 'stop': -100, 'reverse': -20}


class DefensiveAgent(MySmartAgent):
    """
    A reflex agent that keeps its side Pacman-free. Again,
    this is to give you an idea of what a defensive agent
    could be like.  It is not the best or only way to make
    such an agent.
    """

    def getFeatures(self, gameState, action):
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)
        features['successorScore'] = self.getScore(successor)

        myState = successor.getAgentState(self.index)
        myPos = myState.getPosition()

        enemies = [successor.getAgentState(i)
                   for i in self.getOpponents(successor)]
        invaders = [a for a in enemies if a.isPacman and a.getPosition()
                    != None]
        numInvaders = len([invader for invader in enemies if invader.isPacman])
        features['numInvaders'] = numInvaders
        defenseFood = self.getFoodYouAreDefending(successor).asList()
        numFood = len([food for food in defenseFood])
        boundaries = self.boundaries

        # Computes whether we're on defense (1) or offense (0)
        defense = 10
        if myState.isPacman:
            features['onDefense'] = 0
        else:
            features['onDefense'] = 1

        if numInvaders == 0:
            # If the agent needs to go to the upper bound, the bound is set to the upper bound. Otherwise it's the lower bound
            if self.boundary_top is True:
                bound = boundaries[0]
            else:
                bound = boundaries[1]

            # If the agent has reached the upper bound, set the top boundary to false and vice versa
            if myPos == bound:
                self.boundary_top = not(self.boundary_top)
            features['bound'] = self.getMazeDistance(myPos, bound)

        # Computes distance to invaders we can see and their distance to the food we are defending
        if not myState.isPacman and myState.scaredTimer > 0:
            # Compute distance to the nearest food
            foodList = self.getFood(successor).asList()
            if len(foodList) > 0:  # This should always be True,  but better safe than sorry
                minDistance = min([self.getMazeDistance(myPos, food)
                                   for food in foodList])
                features['distanceToFood'] = minDistance + 1
            features['defenseFoodDistance'] = 0.

        if len(invaders) > 0:
            dist = min([self.getMazeDistance(myPos, invader.getPosition())
                        for invader in invaders])
            if dist == 0:
                dist = -100
            features['invaderDistance'] = min([self.getMazeDistance(
                myPos, invader.getPosition()) for invader in invaders]) + 1
            features['distanceToFood'] = 0.0

        if action == Directions.STOP:
            features['stop'] = 1
        rev = Directions.REVERSE[gameState.getAgentState(
            self.index).configuration.direction]
        if action == rev:
            features['reverse'] = 1

        return features

    def getWeights(self, gameState, action):
        return {'numInvaders': -1000, 'onDefense': 50, 'invaderDistance': -100, 'distanceToFood': -1, 'defenseFoodDistance': -8, 'bound': -10, 'stop': -100, 'reverse': -15}

    def boundaryTravel(self, gameState):
        """
        Returns two points that act as a boundary line along which the agent travels
        """
        walls = gameState.getWalls().asList()
        max_y = max([wall[1] for wall in walls])

        if not self.isRed:
            mid_x = (max([wall[0] for wall in walls])/2) + 2
        else:
            mid_x = max([wall[0] for wall in walls])/2

        walls = gameState.getWalls().asList()

        # lower bound is 1/3 of grid. Upper bound is 2/3 of grid
        lower = max_y / 3
        upper = (max_y*2)/3

        # If the positions are illegal states, add 1 to get a legal state
        while (mid_x, lower) in walls:
            lower += 1
        while (mid_x, upper) in walls:
            upper -= 1

        return (mid_x, lower), (mid_x, upper)
