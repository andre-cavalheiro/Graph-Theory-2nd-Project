import numpy as np
import itertools
from copy import deepcopy
from utils import *
import random
import matplotlib.pyplot as plt
from os.path import join

class evolutionIndirectReciprocitySimulation:

    nodes = []

    def __init__(self, numNodes, numInteractions, numGenerations, initialScore=0,
                 benefit=1, cost=0.1, strategyLimits=[-5,6], scoreLimits=[-5,5], mutationRebelChild=False,
                 mutationNonPublicScores=False, mutationMyScoreMatters=False, logFreq=3, numObservers=10,
                 mutationMyScoreMattersStrategy=None, reproduce='normal'):

        # todo -> find out, Are costs and benefits updated during runtime? (original paper end of legend of fig 1)
        self.logFreq = logFreq
        self.numNodes = numNodes
        self.numInteractions = numInteractions
        self.numGenerations = numGenerations

        self.initialScore = initialScore

        self.payoffBenefit = benefit
        self.payoffCost = cost
        self.strategyLimits = strategyLimits
        self.scoreLimits = scoreLimits
        self.mutationRebelChild = mutationRebelChild
        self.mutationNonPublicScores = mutationNonPublicScores
        self.mutationMyScoreMatters = mutationMyScoreMatters
        self.mutationMyScoreMattersStrategy = mutationMyScoreMattersStrategy
        self.numObservers = numObservers
        self.reproduceMethod = reproduce

        assert(benefit > cost)
        assert(not (mutationNonPublicScores == True and mutationMyScoreMatters == True))    # Can't both be on
        if mutationMyScoreMatters:
            assert (mutationMyScoreMattersStrategy is not None)

        self.idIterator = 0
        self.idToIndex = {}     # id:index
        self.initiateNodes()

    def runSimulation(self):
        print('=====    Initiating simulation   ======')
        perGenLogs = []
        for i in range(self.numGenerations):
            print('-- Generation {} --'.format(i))
            self.runGeneration()
            if i%self.logFreq==0:
                # print('== Logging {} =='.format(i))

                l = self.perGenLogs(i)
                perGenLogs.append(l)
            if self.reproduceMethod == 'normal':
                self.reproduce()
            elif self.reproduceMethod == 'moran':
                self.reproduce_Moran()
            elif self.reproduceMethod == 'social':
                self.reproduce_Social()
            else:
                print('Wrong reproduce method, check original values')
                exit()

        finalLogs(perGenLogs)

    def runGeneration(self):
        interactionPairs = pickInteractionPairs(self.nodes, self.numInteractions)
        for pair in interactionPairs:
            self.runInteraction(pair)

        # # print(self.nodes)
        return {}

    def runInteraction(self, pair):
        donor = pair[0]
        recipient = pair[1]
        score = self.checkRecipientScore(donor, recipient)

        if self.mutationMyScoreMatters:
            action = self.myScoreMattersInteraction(donor, score)
        else:
            if score >= donor['strategy']:      # Each node has its own strategy
                # Cooperate
                action = 'cooperate'
            else:
                # Deflect
                action = 'deflect'

        self.updateScoreAndPayoff(donor, recipient, action)
        donor['payoff'] += 0.1
        return

    def myScoreMattersInteraction(self, donor, recipientScore):
        firstCond = recipientScore > donor['strategy']      # In the paper they don't say "or equal to"
        secondCond = donor['score'] < donor['strategySelf'] # In the paper they don't say "or equal to"

        if self.mutationMyScoreMattersStrategy == 'and':
            if firstCond and secondCond:
                return 'cooperate'
            else:
                return 'deflect'
        elif self.mutationMyScoreMattersStrategy == 'or':
            if firstCond or secondCond:
                return 'cooperate'
            else:
                return 'deflect'
        else:
            print('Unknown strategy for mutation: "My score matters" - exiting')
            exit(-1)

    def updateScoreAndPayoff(self, donor, recipient, action):
        if self.mutationNonPublicScores:
            if action == 'cooperate':
                # Change random observer's views of the donor + the recipient
                possibleObservers = self.nodes.copy()
                possibleObservers.remove(donor)
                possibleObservers.remove(recipient)
                observers = random.sample(possibleObservers, self.numObservers)
                observers.append(recipient)
                for obs in observers:
                    for nodeScores in self.nodes[self.idToIndex[obs['id']]]['otherScoresForMe']:
                        if nodeScores['id'] == donor['id']:
                            nodeScores['score'] += 1

                donor['payoff'] -= self.payoffCost
                recipient['payoff'] += self.payoffBenefit

            elif action == 'deflect':
                # Change random observer's views of the donor
                possibleObservers = self.nodes.copy()
                possibleObservers.remove(donor)
                possibleObservers.remove(recipient)
                observers = random.sample(possibleObservers, self.numObservers)
                observers.append(recipient)
                for obs in observers:
                    for nodeScores in self.nodes[self.idToIndex[obs['id']]]['otherScoresForMe']:
                        if nodeScores['id'] == donor['id']:
                            nodeScores['score']-=1

            else:
                print('Something is very wrong here unkown action !!!!')
                print('Something is very wrong here unkown action !!!!')

        else:
            if action == 'cooperate':
                if donor['score'] < self.scoreLimits[1]:
                    donor['score'] += 1

                donor['payoff'] -= self.payoffCost
                recipient['payoff'] += self.payoffBenefit

            elif action == 'deflect':
                if donor['score'] > self.scoreLimits[0]:
                    donor['score'] -= 1
                # Payoff does not change
            else:
                print('Something is very wrong here unkown action !!!!')
                print('Something is very wrong here unkown action !!!!')

    def reproduce(self):
        print('== Raising new generation ==')
        newNodes = []
        self.idToIndex = {}

        payoffs = [node['payoff'] for node in self.nodes]
        totalPayoff = sum(payoffs)

        numChilds = [p*self.numNodes/totalPayoff for p in payoffs]
        # # print(payoffs)
        numChilds = round_series_retain_integer_sum(numChilds)

        for i, node in enumerate(self.nodes):
            offspring = numChilds[i]
            # # print('{} - {}'.format(numChilds[i], offspring))
            # # print('Reproducing {}'.format(offspring))
            for c in range(offspring):
                newNode = node.copy()
                newNode['score'] = 0
                newNode['payoff'] = 0
                newNode['id'] = self.idIterator

                if self.mutationRebelChild:     # fixme - should also change h for mutation: 'my score matters'
                    if casino(0.001):
                    # if casino(0.2):
                        print('JACKPOT')
                        newNode['strategy'] = random.randrange(self.strategyLimits[0], self.strategyLimits[1]+1)

                newNodes.append(newNode)

                self.idToIndex[self.idIterator] = len(newNodes)-1
                self.idIterator += 1
            else:
                # # print('Not reproducing :( ')
                pass

        # Set initial scores
        for node in newNodes:
            if self.mutationNonPublicScores:
                node['otherScoresForMe'] = [{'score': 0, 'id': i['id']} for i in newNodes if i['id'] != node['id']]
            else:
                node['score'] = 0

        self.nodes = newNodes

        # print('Size of new generation is {}'.format(len(self.nodes)))
        # # print(self.nodes)

    def reproduce_Moran(self):
        # print('== Moran in the House ==')
        newNodes = []
        threshold = []

        payoffs = [node['payoff'] for node in self.nodes]
        strat = [node['strategy'] for node in self.nodes if node['payoff'] != 0]

        totalPayoff = 0
        for p in payoffs:
            totalPayoff += p
            if p > 0:
                threshold.append(totalPayoff)

        for i , node in enumerate(self.nodes):
            r = random.uniform(0, totalPayoff)
            newNode = node.copy()
            newNode['score'] = 0
            newNode['payoff'] = 0
            newNode['id'] = self.idIterator
            self.idIterator += 1
            for n in range(len(threshold)):
                if n == 0 and r <= threshold[n]:
                    newNode['strategy'] = strat[n]
                elif threshold[n-1] <= r < threshold[n]:
                    newNode['strategy'] = strat[n]
            if self.mutation:
                if casino(0.001): # print('JACKPOT')
                    newNode['strategy'] = random.randrange(self.strategyLimits[0], self.strategyLimits[1] + 1)

            newNodes.append(newNode)
        self.nodes = newNodes

        # print('Size of new generation is {}'.format(len(self.nodes)))
        # # print(self.nodes)

    def reproduce_Social(self): # social learning where nodes copy another node's strategy with a given probability if that node's payoff is better
        interactionPairs = pickInteractionPairs(self.nodes, self.numInteractions)
        beta = 10
        for pair in interactionPairs:
            mine = pair[0]
            partner = pair[1]
            if partner['payoff'] > mine['payoff']:
                prob = 1/(1+math.exp(-beta * (partner['payoff'] - mine['payoff'])))
                if casino(prob):
                    mine['strategy'] = partner['strategy']
        self.reset_scores()

    def reset_scores(self):
        newNodes=[]
        for i , node in enumerate(self.nodes):
            newNode = node.copy()
            newNode['score'] = 0
            newNode['payoff'] = 0
            newNode['id'] = self.idIterator
            self.idIterator += 1
            newNodes.append(newNode)

        self.nodes = newNodes

    def checkRecipientScore(self, donor, recipient):
        if self.mutationNonPublicScores:
            recipientScore = None
            for d in donor['otherScoresForMe']:
                if d['id']==recipient['id']:
                    recipientScore = d['score']

            if recipientScore == None:
                print('SOMETHING IS WRONG HERE THIS SHOULD NOT HAPPEN')
                exit()
            return recipientScore
        else:
            # Simplest case:
            return recipient['score']

    def perGenLogs(self, it):
        # print('== Logging Results ==')

        # # print(self.nodes)

        # Strategy Distribution
        if self.mutationMyScoreMatters:
            vals = list(range(self.strategyLimits[0], self.strategyLimits[1]+1))
            indexes = {val:it for it, val in enumerate(vals)}
            freq = [[0 for _ in vals] for _ in vals]

            for node in self.nodes:
                k = node['strategy']
                h = node['strategySelf']
                freq[indexes[k]][indexes[h]]+=1

            x, y, z = [], [], []
            for k in vals:
                for h in vals:
                    x.append(k)
                    y.append(h)
                    z.append(freq[indexes[k]][indexes[h]])

            scaleSizes = [i*10 for i in z]
            plt.scatter(x, y, s=scaleSizes, c="blue", alpha=0.4)
            plt.grid()
            plt.savefig(join(dir, 'strategyDistributionScatter - {}'.format(it)))
            plt.close()

        else:
            strategies = [n['strategy'] for n in self.nodes]
            plt.hist(x=strategies, bins=range(self.strategyLimits[0], self.strategyLimits[1]+1), align='left', alpha=0.8, rwidth=0.85)
            plt.xticks(range(self.strategyLimits[0], self.strategyLimits[1]+1))
            plt.savefig(join(dir, 'strategyDistribution - {}'.format(it)))
            plt.close()

        # Average Payoff
        payoffs = [n['payoff'] for n in self.nodes]
        avgPayoff = sum(payoffs)/len(payoffs)

        return {'generation': it, 'avgPayoff': avgPayoff}

    def calculateInitialStrategies(self):
        initialStrategies = [random.randrange(self.strategyLimits[0], self.strategyLimits[1]+1) for _ in range(self.numNodes)]
        return initialStrategies

    def initiateNodes(self):

        initialStrategies = self.calculateInitialStrategies()

        if self.mutationNonPublicScores:
            for i in range(self.numNodes):
                self.nodes.append({
                    'id': self.idIterator,
                    'payoff': 0,
                    'strategy': initialStrategies[i]
                })
                self.idToIndex[self.idIterator] = len(self.nodes)-1
                self.idIterator += 1

            for node in self.nodes:
                node['otherScoresForMe'] = [{'score': 0, 'id': i['id']} for i in self.nodes if i['id']!=node['id']]

        elif self.mutationMyScoreMatters:
            initialSelfStrategies = self.calculateInitialStrategies()

            for i in range(self.numNodes):
                self.nodes.append({
                    'id': self.idIterator,
                    'payoff': 0,
                    'score': 0,
                    'strategy': initialStrategies[i],
                    'strategySelf': initialSelfStrategies[i],
                })
                self.idToIndex[self.idIterator] = len(self.nodes) - 1
                self.idIterator += 1

        else:
            for i in range(self.numNodes):
                self.nodes.append({
                    'id': self.idIterator,
                    'payoff': 0,
                    'score': 0,
                    'strategy': initialStrategies[i]
                })
                self.idToIndex[self.idIterator] = len(self.nodes)-1
                self.idIterator += 1

        return


if __name__ == "__main__":
    # Original paper values:
    originalPaperValues = {
        'logFreq': 50,
        'numNodes': 100,
        'numInteractions':  250,
        'numGenerations': 1000,
        'initialScore': 0,
        'benefit': 1,
        'cost': 0.1,
        'strategyLimits': [-5, 6],
        'scoreLimits': [-5, 5],
        'mutationRebelChild': False,
        'mutationNonPublicScores': False,
        'mutationMyScoreMatters': False,
        'mutationMyScoreMattersStrategy': 'and',  # 'and' or 'or'
        'reproduce': 'social', # 'normal', 'moran' or 'social'
    }

    dir = 'output'
    sim = evolutionIndirectReciprocitySimulation(**originalPaperValues)
    sim.runSimulation()

