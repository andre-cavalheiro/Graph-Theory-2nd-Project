import numpy as np
import random
import itertools
import matplotlib.pyplot as plt
from os.path import join
import math

class evolutionIndirectReciprocitySimulation:

    nodes = []
    validNodeIds = []

    def __init__(self, numNodes, numInteractions, numGenerations, initialScore=0,
                 benefit=1, cost=0.1, strategyLimits=[-5,6], scoreLimits=[-5,5], mutation=False, logFreq=3):

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
        self.mutation = mutation

        assert(benefit > cost)

        self.idIterator = 0

        self.initiateNodes()

    def runSimulation(self):
        # print('=====    Initiating simulation   ======')
        perGenLogs = []
        for i in range(self.numGenerations):
            # print('-- Generation {} --'.format(i))
            self.runGeneration()

            # self.printPayoffs()
            if i%self.logFreq==0:
                # print('== Logging {} =='.format(i))
                l = self.perGenLogs(i)
                perGenLogs.append(l)

            #self.reproduce()
            self.reproduce_Moran()

        self.finalLogs(perGenLogs)

    def runGeneration(self):
        interactionPairs = self.pickInteractionPairs(self.nodes, self.numInteractions)
        for pair in interactionPairs:
            self.runInteraction(pair)

        # # print(self.nodes)
        return {}

    def runInteraction(self, pair):
        donor = pair[0]
        recipient = pair[1]
        score = self.checkRecipientScore(recipient)

        if score >= donor['strategy']:      # Each node has its own strategy
            # Cooperate
            if donor['score'] < self.scoreLimits[1]:
                donor['score'] += 1
            donor['payoff'] -= self.payoffCost
            recipient['payoff'] += self.payoffBenefit

        else:
            # Deflect
            if donor['score'] > self.scoreLimits[0]:
                donor['score'] -= 1

        # todo - talk with the teacher to make sure this is right
        donor['payoff'] += 0.1
        return

    def reproduce(self):
        # print('== Raising new generation ==')
        newNodes = []

        payoffs = [node['payoff'] for node in self.nodes]
        totalPayoff = sum(payoffs)

        numChilds = [p*self.numNodes/totalPayoff for p in payoffs]
        # # print(payoffs)
        numChilds = self.round_series_retain_integer_sum(numChilds)

        for i, node in enumerate(self.nodes):
            offspring = numChilds[i]
            # # print('{} - {}'.format(numChilds[i], offspring))
            # # print('Reproducing {}'.format(offspring))
            for c in range(offspring):
                newNode = node.copy()
                newNode['score'] = 0
                newNode['payoff'] = 0
                newNode['id'] = self.idIterator
                self.idIterator += 1

                if self.mutation:
                    if self.casino(0.001):
                    # if self.casino(0.2):
                        # print('JACKPOT')
                        newNode['strategy'] = random.randrange(self.strategyLimits[0], self.strategyLimits[1]+1)

                newNodes.append(newNode)
            else:
                # # print('Not reproducing :( ')
                pass
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
                if self.casino(0.001):
                  # print('JACKPOT')
                    newNode['strategy'] = random.randrange(self.strategyLimits[0], self.strategyLimits[1] + 1)
            newNodes.append(newNode)

        self.nodes = newNodes

        # print('Size of new generation is {}'.format(len(self.nodes)))
        # # print(self.nodes)

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

        # print("> Calculating interaction pairs ")

        # Generate all possible non-repeating pairs
        pairs = list(itertools.combinations(ids, 2))
        # Randomly shuffle these pairs
        random.shuffle(pairs)
        return pairs

        pairs = []
        while len(pairs) < numPairs:
            rand1 = random.choice(ids)
            rand2 = rand1
            while rand2["id"] == rand1["id"]:
                rand2 = random.choice(ids)
            pair = [rand1, rand2]
            pairs.append(pair)
        # # print(pairs)
        # print("- {} pairs calculated".format(len(pairs)))
        return pairs

    def checkRecipientScore(self, node):
        # Simplest case:
        return node['score']

    def perGenLogs(self, it):
        # print('== Logging Results ==')

        # # print(self.nodes)

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

        for i in range(self.numNodes):
            self.nodes.append({
                'id': self.idIterator,
                'payoff': 0,
                'score': 0,
                'strategy':  initialStrategies[i]
            })
            self.idIterator += 1
            self.validNodeIds.append(i)

    def newNode(self, id, strategy):
        pass

    def printPayoffs(self):
        for node in self.nodes:
            print(node['payoff'])

    def casino(self, percentage):
        return (random.random() < percentage);


if __name__ == "__main__":
    # Original paper values:
    originalPaperValues = {
        'logFreq': 1,
        'numNodes': 100,
        'numInteractions':  125,
        'numGenerations': 200,
        'initialScore': 0,
        'benefit': 1,
        'cost': 0.1,
        'strategyLimits': [-5, 6],
        'scoreLimits': [-5, 5],
        'mutation': False,
    }

    testValues = {
        'numNodes': 10,
        'numInteractions':  15,
        'numGenerations': 10,
        'initialScore': 0,
        'benefit': 1,
        'cost': 0.1,
        'mutation': False,
    }

    dir = 'output'
    sim = evolutionIndirectReciprocitySimulation(**originalPaperValues)
    # sim = evolutionIndirectReciprocitySimulation(**testValues)
    sim.runSimulation()

