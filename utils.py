import math
import matplotlib.pyplot as plt
from os.path import join
import random


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


def finalLogs(logs):
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

def casino(percentage):
    return (random.random() < percentage);
