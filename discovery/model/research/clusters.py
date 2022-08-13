import hdbscan
from sklearn.cluster import AffinityPropagation, DBSCAN


def dbscan(sentence_embeddings):
    from sklearn.cluster import DBSCAN
    import numpy as np
    # dbscan = DBSCAN(eps=.1, min_samples=10) # you can change these parameters, given just for example
    # cluster_labels = dbscan.fit_predict(np.asarray(sentence_embeddings)) # where X
    clusterer = hdbscan.HDBSCAN(min_cluster_size=40, gen_min_span_tree=True)
    c = clusterer.fit_predict(sentence_embeddings)
    cluster_labels = c.labels_
    print(cluster_labels)
    # hdbclust(sentence_embeddings)
    exit(0)
    # for sentence, embedding in zip(sentences, sentence_embeddings):
    #     print("Sentence:", sentence)
    #     print("Embedding:", embedding)
    #     print("")


def get_agg_clust_assignment(sentence_embeddings, distance):
    # 1 Importing the libraries
    import numpy as np
    # import matplotlib.pyplot as plt
    # import pandas as pd
    # import scipy.cluster.hierarchy as sch
    # Lets create a dendrogram variable linkage is actually the algorithm #itself of hierarchical clustering and then in linkage we have to #specify on which data we apply and engage. This is X dataset
    X = np.asarray(sentence_embeddings)

    # Visualize cluster
    # dendrogram = sch.dendrogram(sch.linkage(X, method="ward"))
    # plt.title('Dendrogram')
    # plt.xlabel('Clusters')
    # plt.ylabel('Euclidean distances')
    # plt.show()

    # 4 Fitting hierarchical clustering to the Mall_Customes dataset
    # There are two algorithms for hierarchical clustering: #Agglomerative Hierarchical Clustering and
    # Divisive Hierarchical Clustering. We choose Euclidean distance and ward method for our algorithm class
    from sklearn.cluster import AgglomerativeClustering
    hc = AgglomerativeClustering(affinity='euclidean', linkage='ward', distance_threshold=distance, n_clusters=None)
    # Lets try to fit the hierarchical clustering algorithm  to dataset #X while creating the clusters vector that tells for each customer #which cluster the customer belongs to.
    y_hc = hc.fit_predict(X)
    cluster_assignment = hc.labels_

    # sch_score(X, y_hc, cluster_assignment, y_hc.cluster_centers_)

    return cluster_assignment
