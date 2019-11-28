import numpy as np
import random
import itertools
import matplotlib.pyplot as plt

class evolutionIndirectReciprocitySimulation:

    nodes = []
    validNodeIds = []

    def __init__(self, numNodes, numInteractions, numGenerations, initialScore=0,
                 benefit=1, cost=0.1, strategyLimits=[-5,6], scoreLimits=[-5,5], mutation=False):

        # todo - scores between -5:+5
        # todo strategies between -5:+6 => -5=uncond cooperators ; +6=uncond defectors
        # todo -> find out, Are costs and benefits updated during runtime? (original paper end of legend of fig 1)

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
        logs = []
        print('=====    Initiating simulation   ======')
        for i in range(self.numGenerations):
            print('-- Generation {} --'.format(i))
            l = self.runGeneration()
            logs.append(l)

            # self.printPayoffs()
            self.reproduce()

        print('== Logging ==')
        self.logs(logs)

    def runGeneration(self):
        interactionPairs = self.pickInteractionPairs(self.nodes, self.numInteractions)
        for pair in interactionPairs:
            self.runInteraction(pair)

        # print(self.nodes)
        return {}

    def runInteraction(self, pair):
        donner = pair[0]
        recipient = pair[1]
        score = self.checkRecipientScore(recipient)

        if score >= donner['strategy']:      # Each node has its own strategy
            # Cooperate
            if[donner['score'] < self.scoreLimits[1]]:
                donner['score'] += 1
            donner['payoff'] -= self.payoffCost
            donner['payoff'] += self.payoffBenefit

            # todo - talk with the teacher to make sure this is right
            '''donner['score'] += 0.1
            recipient['score'] += 0.1'''


        else:
            # Deflect
            if[donner['score'] > self.scoreLimits[0]]:
                donner['score'] -= 1


        return

    def reproduce(self):
        print('== Raising new generation ==')
        newNodes = []

        payoffs = [node['payoff'] for node in self.nodes]
        totalPayoff = 0
        for p in payoffs:
            totalPayoff += p

        numChilds = [p*self.numNodes/totalPayoff for p in payoffs]
        # print(payoffs)
        numChilds = self.round_series_retain_integer_sum(numChilds)

        for i, node in enumerate(self.nodes):
            offspring = numChilds[i]
            # print('{} - {}'.format(numChilds[i], offspring))
            # print('Reproducing {}'.format(offspring))
            for c in range(offspring):
                newNode = node.copy()
                newNode['score'] = 0
                newNode['id'] = self.idIterator
                self.idIterator += 1

                if self.mutation:
                    # if self.casino(0.001):
                    if self.casino(0.2):
                        print('JACKPOT')
                        newNode['strategy'] = random.randrange(self.strategyLimits[0], self.strategyLimits[1]+1)

                newNodes.append(newNode)
            else:
                # print('Not reproducing :( ')
                pass
        self.nodes = newNodes

        print('Size of new generation is {}'.format(len(self.nodes)))
        # print(self.nodes)

    def round_series_retain_integer_sum(self, xs):
        N = sum(xs)
        Rs = [round(x) for x in xs]
        K = N - sum(Rs)
        # assert(K == round(K))
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

    def checkRecipientScore(self, node):
        # Simplest case:
        return node['score']

    def logs(self, logs):
        print('== Logging Results ==')
        # print(self.nodes)
        strategies = [n['strategy'] for n in self.nodes]
        plt.hist(x=strategies, bins=range(-5, 7), align='left', alpha=0.8, rwidth=0.85)
        plt.xticks(range(-5,7))
        plt.show()

    def calculateInitialScores(self):
        initialScores = [random.randrange(self.strategyLimits[0], self.strategyLimits[1]+1) for _ in range(self.numNodes)]
        return initialScores

    def initiateNodes(self):

        initialScores = self.calculateInitialScores()

        for i in range(self.numNodes):
            self.nodes.append({
                'id': self.idIterator,
                'payoff': 0,
                'score': self.initialScore,
                'strategy':  initialScores[i]
            })
            self.idIterator += 1
            self.validNodeIds.append(i)

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
        'mutation': True,
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
    sim = evolutionIndirectReciprocitySimulation(**originalPaperValues)
    # sim = evolutionIndirectReciprocitySimulation(**testValues)
    sim.runSimulation()
