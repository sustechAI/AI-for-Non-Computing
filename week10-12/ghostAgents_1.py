# ghostAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from game import Agent
from game import Actions
from game import Directions
import random
from util import manhattanDistance
import util

class GhostAgent( Agent ):
    def __init__( self, index ):
        self.index = index

    def getAction( self, state ):
        dist = self.getDistribution(state)
        if len(dist) == 0:
            return Directions.STOP
        else:
            return util.chooseFromDistribution( dist )

    def getDistribution(self, state):
        "Returns a Counter encoding a distribution over actions from the provided state."
        util.raiseNotDefined()

class RandomGhost( GhostAgent ):
    "A ghost that chooses a legal action uniformly at random."
    def getDistribution( self, state ):
        dist = util.Counter()
        for a in state.getLegalActions( self.index ): dist[a] = 1.0
        dist.normalize()
        return dist

class DirectionalGhost( GhostAgent ):
    "A ghost that prefers to rush Pacman, or flee when scared."
    def __init__( self, index, prob_attack=0.8, prob_scaredFlee=0.8 ):
        self.index = index
        self.prob_attack = prob_attack
        self.prob_scaredFlee = prob_scaredFlee

    def getDistribution( self, state ):
        # Read variables from state
        ghostState = state.getGhostState( self.index )
        legalActions = state.getLegalActions( self.index )
        pos = state.getGhostPosition( self.index )
        isScared = ghostState.scaredTimer > 0

        speed = 1
        if isScared: speed = 0.5

        actionVectors = [Actions.directionToVector( a, speed ) for a in legalActions]
        newPositions = [( pos[0]+a[0], pos[1]+a[1] ) for a in actionVectors]
        pacmanPosition = state.getPacmanPosition()

        # Select best actions given the state
        distancesToPacman = [manhattanDistance( pos, pacmanPosition ) for pos in newPositions]
        if isScared:
            bestScore = max( distancesToPacman )
            bestProb = self.prob_scaredFlee
        else:
            bestScore = min( distancesToPacman )
            bestProb = self.prob_attack
        bestActions = [action for action, distance in zip( legalActions, distancesToPacman ) if distance == bestScore]

        # Construct distribution
        dist = util.Counter()
        for a in bestActions: dist[a] = bestProb / len(bestActions)
        for a in legalActions: dist[a] += ( 1-bestProb ) / len(legalActions)
        dist.normalize()
        return dist

class MinimaxGhost(GhostAgent):

    """
      Your minimax agent (question 1)

      useage: python2 pacman.py -p ExpectimaxAgent -l specialNew -g MinimaxGhost -a depth=4
              python2 pacman.py -l specialNew -g MinimaxGhost
              python2 pacman.py -p ExpectimaxAgent -l smallClassic -g MinimaxGhost -a depth=4
              python2 pacman.py -l smallClassic -g MinimaxGhost
              python2 pacman.py -p MinimaxAgent -l smallClassic -g MinimaxGhost  -numGames=5 -q

    """
    "*** YOUR CODE HERE ***"
    def __init__(self, index, evalFun = 'scoreEvaluationFunctionGhost',depth = '2'):
        self.index = index
        self.evaluationFunction = util.lookup(evalFun, globals())
        self.depth = int(depth)
    def getAction( self, gameState ):
        def max_value(state, depth = 1):
            if state.isWin() or state.isLose():
                return self.evaluationFunction(state)
            v = float('-Inf')
            for direction in state.getLegalActions(0):
                v = max(v, min_value(state.generateSuccessor(0, direction), depth))
            return v
        def min_value(state, depth, ghostNumber=1):
            #depth = depth + 1
            if state.isWin() or state.isLose():
                return self.evaluationFunction(state)
            if depth == self.depth:
                return self.evaluationFunction(state)
            v = float('Inf')
            for direction in state.getLegalActions(ghostNumber):
                if ghostNumber < state.getNumAgents() - 1:
                    v = min(v, min_value(state.generateSuccessor(ghostNumber, direction), depth, ghostNumber + 1))
                if ghostNumber == state.getNumAgents() - 1:
                    v = min(v, max_value(state.generateSuccessor((state.getNumAgents() - 1), direction), depth+1))
            return v

        if gameState.getNumAgents() - 1 == 1:
            legalMoves = gameState.getLegalActions(1)
            scores = [max_value(gameState.generateSuccessor(1, action)) for action in legalMoves]
            bestScore = min(scores)
            bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
            chosenIndex = random.choice(bestIndices)
            return legalMoves[chosenIndex]
        if gameState.getNumAgents() - 1 == 2:
            legalMoves1 = gameState.getLegalActions(1)
            legalMoves2 = gameState.getLegalActions(2)
            scores = []
            for move1 in legalMoves1:
                score = []
                state = gameState.generateSuccessor(1, move1)
                for move2 in legalMoves2:
                    if state.isWin() or state.isLose():
                        score.append(max_value(gameState.generateSuccessor(2, move2)))
                    else:
                        score.append(max_value(state.generateSuccessor(2, move2)))
                scores.append(score)
            temp = [min(a) for a in scores]
            tempindex = [a.index(min(a)) for a in scores]
            bestScore = min(temp)
            bestIndices1 = temp.index(min(temp))
            bestIndices2 = tempindex[bestIndices1]
            Moves = [legalMoves1[bestIndices1],legalMoves2[bestIndices2]]
            return Moves[self.index-1]

def scoreEvaluationFunctionGhost(currentGameState):
    score = currentGameState.getScore()
    pacman_pos = currentGameState.getPacmanPosition()
    #foodPos = currentGameState.getFood().asList()
    ghosts = currentGameState.getGhostStates()
    ghostList = []
    for ghost in ghosts:
        ghostPos = ghost.getPosition()
        ghostList.append(manhattanDistance(pacman_pos, ghostPos))
    #nearestGhostDist = min(ghostList)
    sumdistance = sum(ghostList)

    return score+sumdistance



def betterEvaluationFunctionGhost(currentGameState):
    """
        Ghost evaluation function
    """



# Abbreviation
ghostEval = betterEvaluationFunctionGhost

