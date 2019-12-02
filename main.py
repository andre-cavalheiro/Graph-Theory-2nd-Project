import numpy as np
import itertools
import random
import matplotlib.pyplot as plt
from os.path import join
import math
from copy import deepcopy

class evolutionIndirectReciprocitySimulation:

    nodes = []

    def __init__(self, numNodes, numInteractions, numGenerations, initialScore=0,
                 benefit=1, cost=0.1, strategyLimits=[-5,6], scoreLimits=[-5,5], mutationRebelChild=False,
                 mutationNonPublicScores=False, logFreq=3, numObservers=10):

        # todo - scores between -5:+5
        # todo strategies between -5:+6 => -5=uncond cooperators ; +6=uncond defectors
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
        self.numObservers = numObservers

        assert(benefit > cost)

        self.idIterator = 0
        self.idToIndex = {}     # id:index

        self.initiateNodes()

    def runSimulation(self):
        print('=====    Initiating simulation   ======')
        perGenLogs = []
        for i in range(self.numGenerations):
            print('-- Generation {} --'.format(i))
            self.runGeneration()

            # self.printPayoffs()
            if i%self.logFreq==0:
                print('== Logging {} =='.format(i))
                l = self.perGenLogs(i)
                perGenLogs.append(l)

            self.reproduce()

        self.finalLogs(perGenLogs)

    def runGeneration(self):
        interactionPairs = self.pickInteractionPairs(self.nodes, self.numInteractions)
        for pair in interactionPairs:
            self.runInteraction(pair)

        # print(self.nodes)
        return {}

    def runInteraction(self, pair):
        donor = pair[0]
        recipient = pair[1]
        score = self.checkRecipientScore(donor, recipient)

        if score >= donor['strategy']:      # Each node has its own strategy
            # Cooperate
            self.updateScoreAndPayoff(donor, recipient, 'cooperate')

            # todo - talk with the teacher to make sure this is right
        else:
            # Deflect
            self.updateScoreAndPayoff(donor, recipient, 'deflect')

        donor['payoff'] += 0.1
        recipient['payoff'] += 0.1   # I think this shouldn't be
        return

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

            u=1
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
        # print(payoffs)
        numChilds = self.round_series_retain_integer_sum(numChilds)

        for i, node in enumerate(self.nodes):
            offspring = numChilds[i]
            # print('{} - {}'.format(numChilds[i], offspring))
            # print('Reproducing {}'.format(offspring))
            for c in range(offspring):
                newNode = node.copy()

                if self.mutationRebelChild:
                    if self.casino(0.001):
                        # if self.casino(0.2):
                        print('JACKPOT')
                        newNode['strategy'] = random.randrange(self.strategyLimits[0], self.strategyLimits[1] + 1)

                newNode['payoff'] = 0
                newNode['id'] = self.idIterator
                newNodes.append(newNode)

                self.idToIndex[self.idIterator] = len(newNodes)-1
                self.idIterator += 1
            else:
                # print('Not reproducing :( ')
                pass

        # Set initial scores
        for node in newNodes:
            if self.mutationNonPublicScores:
                node['otherScoresForMe'] = [{'score': 0, 'id': i['id']} for i in newNodes if i['id'] != node['id']]
            else:
                node['score'] = 0

        self.nodes = newNodes

        print('Size of new generation is {}'.format(len(self.nodes)))
        # print(self.nodes)

    def round_series_retain_integer_sum(self, xs):
        N = sum(xs)
        # Rs = [round(x) for x in xs]
        Rs = [math.trunc(x) for x in xs]
        K = int(N - sum(Rs))
        assert(K == round(K))
        fs = [x - round(x) for x in xs]
        indices = [i for order, (e, i) in enumerate(reversed(sorted((e, i) for i, e in enumerate(fs)))) if order < K]
        ys = [R + 1 if i in indices else R for i, R in enumerate(Rs)]
        return ys

    def pickInteractionPairs(self, ids, numPairs):
        # todo - We should guarantee that each pair interacts once at most.
        # todo - never with the same partner twice (doesnt matter if in different roles)

        print("> Calculating interaction pairs ")

        # Generate all possible non-repeating pairs
        '''pairs = list(itertools.combinations(ids, 2))
        # Randomly shuffle these pairs                                
        random.shuffle(pairs)
        return pairs'''

        pairs = []
        while len(pairs) < numPairs:
            rand1 = random.choice(ids)
            rand2 = rand1
            while rand2["id"] == rand1["id"]:
                rand2 = random.choice(ids)
            pair = [rand1, rand2]
            pairs.append(pair)
        # print(pairs)
        print("- {} pairs calculated".format(len(pairs)))
        return pairs

    def checkRecipientScore(self, donor, recipient):
        if self.mutationNonPublicScores:
            recipientScore = None
            for d in donor['otherScoresForMe']:
                if d['id']==recipient['id']:
                    recipientScore = d['score']

            if recipientScore == None:
                print('SOMETHING IS WRONG HERE THIS SHOULD NOT HAPPEN')
                print('SOMETHING IS WRONG HERE THIS SHOULD NOT HAPPEN')
                print('SOMETHING IS WRONG HERE THIS SHOULD NOT HAPPEN')
                print('SOMETHING IS WRONG HERE THIS SHOULD NOT HAPPEN')
                print('SOMETHING IS WRONG HERE THIS SHOULD NOT HAPPEN')
                exit()
            return recipientScore
        else:
            # Simplest case:
            return recipient['score']

    def perGenLogs(self, it):
        print('== Logging Results ==')

        # print(self.nodes)

        # Strategy Distribution
        strategies = [n['strategy'] for n in self.nodes]
        plt.hist(x=strategies, bins=range(self.strategyLimits[0], self.strategyLimits[1]+1), align='left', alpha=0.8, rwidth=0.85)
        plt.xticks(range(self.strategyLimits[0], self.strategyLimits[1]+1))
        plt.savefig(join(dir, 'strategyDistribution - {}'.format(it)))
        plt.close()

        # Average Payoff
        payoffs = [n['payoff'] for n in self.nodes]
        avgPayoff = sum(payoffs)/len(payoffs)
        return {'generation': it, 'avgPayoff': avgPayoff}

    def finalLogs(self, logs):
        avgPayoff = [l['avgPayoff'] for l in logs]
        generationIt = [l['generation'] for l in logs]

        fig, ax = plt.subplots()
        ax.plot(generationIt, avgPayoff)

        # plt.ylabel(yAxes)
        # ax.set_ylim(bottom=ymin)
        # ax.set_ylim(top=ymax + ymax * 0.1)
        # ax.legend()
        # outputName = buildOutputName(x, ys, dir)

        plt.savefig(join(dir, 'AvgPayoff.png'))
        plt.close()

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

    def newNode(self, id, strategy):
        pass

    def printPayoffs(self):
        for node in self.nodes:
            print(node['payoff'])

    def casino(self, percentage):
        return (random.randrange(100) < percentage);


if __name__ == "__main__":
    # Original paper values:
    originalPaperValues = {
        'numNodes': 100,
        'numInteractions':  125,
        'numGenerations': 200,
        'initialScore': 0,
        'benefit': 1,
        'cost': 0.1,
        'strategyLimits': [-5, 6],
        'scoreLimits': [-5, 5],
        'mutationRebelChild': True,
        'mutationNonPublicScores': True
    }

    testValues = {
        'numNodes': 10,
        'numInteractions':  15,
        'numGenerations': 10,
        'initialScore': 0,
        'benefit': 1,
        'cost': 0.1,
        'mutationRebelChild': False,
        'mutationNonPublicScores': True
    }

    dir = 'output'
    sim = evolutionIndirectReciprocitySimulation(**originalPaperValues)
    # sim = evolutionIndirectReciprocitySimulation(**testValues)
    sim.runSimulation()
