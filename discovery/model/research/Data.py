import collections

# from torch import cdist
# from wikipedia2vec import Wikipedia2Vec
# from numba import jit, cuda

import scipy
from sentence_transformers import SentenceTransformer

from model.myutils.clustering_utils import map_cluster_to_data, summarize_clusters
from model.myutils.data_utils import get_sentences, map_cluster_to_data_expanded, map_cluster_to_doc_expanded
from model.myutils.graph_builder import build_doc_graph, connect_mm_doc_to_clusters

from model.research.clusters import get_agg_clust_assignment
from model.research.embeddings import get_sentence_embedding, search_through_embeddings
from model.research.results_aggregate import get_all_vertical_results

# if __name__ == '__main__':
#     fetch_results_json(engine='qwant', type = 'web')

query = 'mcdonalds'

search_results = get_all_vertical_results(query=query, num=100, engine="google")

search_results_sentences = get_sentences(search_results)
# get sentence embeddings
search_result_sentence_embeddings = get_sentence_embedding(search_results_sentences)

# Search the query for snip view
search_through_embeddings(query, search_result_sentence_embeddings, search_results)

# perform agg clustering
# search_results_cluster_assignment = dbscan(search_result_sentence_embeddings)  # [1, 2,23...]
search_results_cluster_assignment = get_agg_clust_assignment(search_result_sentence_embeddings, 15)  # [1, 2,23...]
# replace cluster assignment to data: clust1 -> snippet 1, 2, .....
bucket_cluster_assignment_sentences = map_cluster_to_data(search_results_cluster_assignment, search_results_sentences)
# bind cluster assignment to the data snippet1 -> url, date, cluster_assignment
assigned_search_results_cluster = map_cluster_to_data_expanded(search_results_cluster_assignment, search_results)
# get each cluster summary: clust [2]-> summary, clust [3]-> summary
summarized_clusters = summarize_clusters(bucket_cluster_assignment_sentences)


# Build MM Docs
G = build_doc_graph(assigned_search_results_cluster, summarized_clusters)

# get mm docs
mm_doc_sentences = list()
od = collections.OrderedDict(sorted(summarized_clusters.items()))
for k, item in od.items():
    mm_doc_sentences.append(item)

mm_doc_sentences_embeddings = get_sentence_embedding(mm_doc_sentences)

#perform agg clust on sentences
mm_doc_clusters = get_agg_clust_assignment(mm_doc_sentences_embeddings, 15)
# replace cluster assignment to data: clust [1] -> snippet 1, 2, .....
bucket_of_mm_doc_cluster = map_cluster_to_data(mm_doc_clusters, mm_doc_sentences)
# For Summarization
summarized_mm_doc_clusters = summarize_clusters(bucket_of_mm_doc_cluster)
# bind cluster assignment to the data mm_doc_1 -> cluster_assignment
expanded_dict_of_mm_clusters = map_cluster_to_doc_expanded(mm_doc_clusters, od)

# replace cluster with summary data
# building graph
G = connect_mm_doc_to_clusters(G, expanded_dict_of_mm_clusters, summarized_mm_doc_clusters)