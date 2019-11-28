import numpy as np
import random
import itertools


class evolutionIndirectReciprocitySimulation:

    nodes = []
    validNodeIds = []

    def __init__(self, numNodes, numInteractions, initialScore=0, thresholdScore=0):

        self.numNodes = numNodes
        self.numInteractions = numInteractions
        self.initialScore = initialScore
        self.thresholdScore = thresholdScore

        self.initiateNodes()

    def RunSimulation(self):
        interactionPairs = self.pickInteractionPairs(self.nodes, self.numInteractions)

        for pair in interactionPairs:
            self.runInteraction(pair)
        print('== Logging ==')
        print(self.nodes)
        self.logs()

    def initiateNodes(self):
        for i in range(self.numNodes):
            self.nodes.append({
                'id': i,
                'score': self.initialScore,
            })
            self.validNodeIds.append(i)

    def pickInteractionPairs(self, ids, numPairs):
        # todo - We should guarantee that each pair interacts once at most.
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
        print(pairs)
        print("- {} pairs calculated".format(len(pairs)))
        return pairs

    def runInteraction(self, pair):
        giver = pair[0]
        receiver = pair[1]
        score = self.checkRecipientScore(receiver)

        if score >= self.thresholdScore:
            # cooperate
            giver['score'] += 1

        else:
            # Deflect
            giver['score'] -= 1
        return

    def checkRecipientScore(self, node):
        return node['score']

    def logs(self):
        print('== Logging Results ==')


if __name__ == "__main__":
    numNodes = 10
    numInteractions = 100
    sim = evolutionIndirectReciprocitySimulation(numNodes, numInteractions)
    sim.RunSimulation()
