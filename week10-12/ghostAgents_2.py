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


class GhostAgent(Agent):
    def __init__(self, index):
        self.index = index

    def getAction(self, state):
        dist = self.getDistribution(state)
        if len(dist) == 0:
            return Directions.STOP
        else:
            return util.chooseFromDistribution(dist)

    def getDistribution(self, state):
        "Returns a Counter encoding a distribution over actions from the provided state."
        util.raiseNotDefined()


class RandomGhost(GhostAgent):
    "A ghost that chooses a legal action uniformly at random."

    def getDistribution(self, state):
        dist = util.Counter()
        for a in state.getLegalActions(self.index): dist[a] = 1.0
        dist.normalize()
        return dist


class DirectionalGhost(GhostAgent):
    "A ghost that prefers to rush Pacman, or flee when scared."

    def __init__(self, index, prob_attack=0.8, prob_scaredFlee=0.8):
        self.index = index
        self.prob_attack = prob_attack
        self.prob_scaredFlee = prob_scaredFlee

    def getDistribution(self, state):
        # Read variables from state
        ghostState = state.getGhostState(self.index)
        legalActions = state.getLegalActions(self.index)
        pos = state.getGhostPosition(self.index)
        isScared = ghostState.scaredTimer > 0

        speed = 1
        if isScared: speed = 0.5

        actionVectors = [Actions.directionToVector(a, speed) for a in legalActions]
        newPositions = [(pos[0] + a[0], pos[1] + a[1]) for a in actionVectors]
        pacmanPosition = state.getPacmanPosition()

        # Select best actions given the state
        distancesToPacman = [manhattanDistance(pos, pacmanPosition) for pos in newPositions]
        if isScared:
            bestScore = max(distancesToPacman)
            bestProb = self.prob_scaredFlee
        else:
            bestScore = min(distancesToPacman)
            bestProb = self.prob_attack
        bestActions = [action for action, distance in zip(legalActions, distancesToPacman) if distance == bestScore]

        # Construct distribution
        dist = util.Counter()
        for a in bestActions: dist[a] = bestProb / len(bestActions)
        for a in legalActions: dist[a] += (1 - bestProb) / len(legalActions)
        dist.normalize()
        return dist


class Minimax(GhostAgent):
    def __init__(self, index, evalFun='scoreEvaluationFunctionGhost', depth='2'):
        # print index
        self.index = index
        self.evaluationFunction = util.lookup(evalFun, globals())
        self.depth = int(depth)
        # print self.depth

    def getAction(self, gameState):
        Flag_min = float('inf')
        legalActions = gameState.getLegalActions(self.index)
        result = Directions.STOP
        choices=[]
        eval = []
        for action in legalActions:
            temp = self.max_method(gameState, 1, self.index, self.index)
            if action is not Directions.STOP:
                # if temp < Flag_min:
                #     Flag_min = temp
                #     result = action
                eval.append(temp)
                choices.append(action)

        Sco = min(eval)
        best = [index for index in range(len(eval)) if eval[index]==Sco]
        # print best
        temp_action = []
        for item in best:
            temp_action.append(choices[item])
        # chosenIndex = random.choice(best)
        # # self.check(gameState)
        # # successorGameState = gameState.generatePacmanSuccessor(choices[chosenIndex])
        #
        # # return  self.check(best,choices,gameState)
        # # print 11111111111
        # return choices[chosenIndex]
        return self.check(gameState,temp_action,self.index)
    def check(self,currentGameState,best,index):
        if len(best) == 1:
            return best[0]
        else:
            score = currentGameState.getScore()
            newPos = currentGameState.getPacmanPosition()
            flag = float('inf')
            result = 0
            ttt = index-1
            for item in best:
                state = currentGameState.generateSuccessor(index,item).getGhostStates()[ttt].getPosition()
                distance = abs(state[0]-newPos[0])+abs(state[1]-newPos[1])
                if distance<flag:
                    flag = distance
                    result = item
            return result
    def max_method(self, state, depth, agent, now_agent):
        if depth >= self.depth and depth != 1:
            return self.evaluationFunction(state)
        Flag = float('-inf')
        legalActions = state.getLegalActions(now_agent)

        for action in legalActions:
                Flag = max(Flag, self.min_method(state.generateSuccessor(now_agent, action), depth, agent, 0))
        return Flag

    def min_method(self, state, depth, agent, now_agent):
        if depth >= self.depth and depth != 1:
            return self.evaluationFunction(state)
        Flag = float('inf')
        legalActions = state.getLegalActions(now_agent)
        for action in legalActions:
            Flag = min(Flag, self.max_method(state.generateSuccessor(now_agent, action), depth + 1, agent, agent))
        return Flag



def scoreEvaluationFunctionGhost(currentGameState):
    """
      Ghost Agent
    """
    return currentGameState.getScore()
