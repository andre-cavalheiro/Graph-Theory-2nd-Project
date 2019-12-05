import math
import matplotlib.pyplot as plt
from os.path import join
import random
import networkx as nx
import matplotlib.pyplot as plt
from itertools import count

from networkx import grid_graph

class MyGraph(nx.Graph):
    def __init__(self, nNodes, avdDegree):
        super().__init__()
        self.num_nodes = nNodes
        self.target_deg = avdDegree
        self.add_nodes_from(range(self.num_nodes))
        while self.avg_deg() < self.target_deg:
            n1, n2 = random.sample(self.nodes(), 2)
            self.add_edge(n1, n2, weight=1)

    def avg_deg(self):
        return self.number_of_edges() * 2 / self.num_nodes


def createGrid(n):
    G = grid_graph(dim=[int(n), int(n)])
    return G

def drawGraph(G, nodeInfo, dir, it):

    # get unique groups
    arr = ['-5', '-4', '-3', '-2', '-1', '0', '1', '2', '3', '4', '5', '6']
    groups = set(arr)
    mapping = dict(zip(sorted(groups), count()))
    nodes = G.nodes()
    colors = [mapping[str(n['strategy'])] for n in nodeInfo]

    # drawing nodes and edges separately so we can capture collection for colobar
    pos = nx.spring_layout(G)
    ec = nx.draw_networkx_edges(G, pos, alpha=0.2)

    nc = nx.draw_networkx_nodes(G, pos, nodelist=nodes, node_color=colors,
                                with_labels=False, node_size=100, cmap=plt.cm.jet, vmin=0, vmax=11)
    plt.colorbar(nc)
    plt.axis('off')
    plt.ylim
    plt.savefig(join(dir, 'graph{}.png'.format(it)))
    plt.close()

def getNeighborPairs(G, nodeInfo, pos):
    pairs = []
    # The index of each node in nodeInfo corresponds
    # to the node with the same index in G.nodes
    # Get every neighbors for every node
    pairs = []
    for it, n in enumerate(nodeInfo):
        neighbors = G.neighbors(n['pos'])
        for neighbor in neighbors:
            neighborIt = pos.index(neighbor)
            pairs.append([n, nodeInfo[neighborIt]])
    random.shuffle(pairs)
    return pairs

def pickInteractionPairs(ids, numPairs):
    # todo - We should guarantee that each pair interacts once at most.
    # todo - never with the same partner twice (doesnt matter if in different roles)
    # print("> Calculating interaction pairs ")

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
    # # print(pairs)
    # print("- {} pairs calculated".format(len(pairs)))
    random.shuffle(pairs)

    return pairs

def round_series_retain_integer_sum(xs):
    N = sum(xs)
    # Rs = [round(x) for x in xs]
    Rs = [math.trunc(x) for x in xs]
    K = int(N - sum(Rs))
    assert (K == round(K))
    fs = [x - round(x) for x in xs]
    indices = [i for order, (e, i) in enumerate(reversed(sorted((e, i) for i, e in enumerate(fs)))) if order < K]
    ys = [R + 1 if i in indices else R for i, R in enumerate(Rs)]
    return ys

def finalLogs(logs, dir):

    avgPayoff = [l['avgPayoff'] for l in logs if 'avgPayoff' in l.keys()]
    generationItPayoff = [l['generation'] for l in logs if 'avgPayoff' in l.keys()]

    cooperationRatio = [l['cooperationRatio'] for l in logs]
    generationItCoopRat = [l['generation'] for l in logs]

    # Average payoff
    fig, ax = plt.subplots()
    ax.plot(generationItPayoff, avgPayoff)

    plt.ylabel('Average Payoff')
    plt.xlabel('Generation')
    plt.savefig(join(dir, 'AvgPayoff.png'))
    plt.close()

    # Cooperation ratio
    fig, ax = plt.subplots()
    ax.plot(generationItCoopRat, cooperationRatio)
    plt.ylabel('Cooperation Ratio')
    plt.xlabel('Generation')
    plt.savefig(join(dir, 'CooperationRatio.png'))
    plt.close()

    # Average score
    if 'avgScore' in logs[0].keys():    # fixme - hardecoded
        avgScore = [l['avgScore'] for l in logs]

        fig, ax = plt.subplots()
        ax.plot(generationItCoopRat, avgScore)
        plt.ylabel('Average Score')
        plt.xlabel('Generation')
        ax.set_ylim(ymin=-5)
        ax.set_ylim(ymax=5)
        plt.savefig(join(dir, 'AvgScore.png'))
        plt.close()

def casino(percentage):
    return (random.random() < percentage);

def countFreq(arr):
    mp = dict()

    # Traverse through array elements
    # and count frequencies
    for i in range(len(arr)):
        if arr[i] in mp.keys():
            mp[arr[i]] += 1
        else:
            mp[arr[i]] = 1

    # Normalize
    for k in mp.keys():
        mp[k] = mp[k]/len(arr)
    return mp

