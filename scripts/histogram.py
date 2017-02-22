import sys
import csv

import numpy as np
import matplotlib.pyplot as plt

'''
Creates Histograms of the recovery times
'''

def get_times_hist (fn, get_leaf = True):
    times = []

    with open(fn, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            has_children = (row[-2] == "1")
            if not get_leaf and has_children:
                times.append(row[-1])
            elif get_leaf and not has_children:
                times.append(row[-1])

    times = np.asarray(map (lambda x: np.float64(x), times))

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.hist(times, bins=[0, 25, 50, 100, 250, 500, 1000])
    plt.savefig("outputs/" + ("leaf_page" if get_leaf else "node_page") + "_hist.png")


if __name__ == '__main__':
    get_times_hist (sys.argv[1])
    get_times_hist (sys.argv[1], False)
