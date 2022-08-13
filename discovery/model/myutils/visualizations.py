import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# %matplotlib inline
from sklearn.cluster import KMeans
import seaborn as sns
import matplotlib.pyplot as plt

def showClusterViz(input, algo):
    X = np.array(input)

    print(algo.cluster_centers_)
    print(algo.labels_)

    plt.scatter(X[:,0],X[:,1], c=algo.labels_, cmap='rainbow')

    data = X
    # data = np.array(X)
    labels = algo.labels_


    #######################################################################


    plt.subplots_adjust(bottom = 0.1)
    plt.scatter(data[:, 0], data[:, 1], c=algo.labels_, cmap='rainbow')

    for label, x, y in zip(labels, data[:, 0], data[:, 1]):
        plt.annotate(
            label,
            xy=(x, y), xytext=(-20, 20),
            textcoords='offset points', ha='right', va='bottom',
            # bbox=dict(boxstyle='round,pad=0.5', fc='red', alpha=0.5),
            # arrowprops=dict(arrowstyle = '->', connectionstyle='arc3,rad=0')
        )

    plt.show()