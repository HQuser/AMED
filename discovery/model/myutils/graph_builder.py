import json
import statistics

import networkx as nx

from model.myutils.Preprocess import Preprocess
from model.myutils.my_files_utils import save_json, read_json

import networkx as nx

from model.myutils.sim_text_processor import normalize


def median(lst):
    sortedLst = sorted(lst)
    lstLen = len(lst)
    index = (lstLen - 1) // 2

    if (lstLen % 2):
        return sortedLst[index]
    else:
        return (sortedLst[index] + sortedLst[index + 1]) / 2.0


def jaccard(list1, list2):
    intersection = len(list(set(list1).intersection(list2)))
    # print(str(intersection))
    union = (len(list1) + len(list2)) - intersection
    # print(str(union))
    # print("wajeeh: " + str((intersection) / union))
    return float(intersection) / union


def build_doc_graph(data, cluster_summaries):
    G = nx.Graph()
    for k, v in cluster_summaries.items():
        createNodes(G, str(k) + "d", {'type': 'doc_summary', 'text': v})

    for key, item in data.items():
        createNodes(G, str(key), item)
        createEdges(G, str(item['clusterassignment']) + "d", str(key))

    # print(G.ad)
    # import matplotlib.pyplot as plt
    # # nx.draw(G)
    # nx.draw(G, nx.spring_layout(G, random_state=100))
    # plt.show()
    print(G.number_of_nodes())
    # nx.write_adjlist(G, "test.adjlist")
    # nx.write_graphml(G, "test.graphml")
    return G


def connect_mm_doc_to_clusters(graph, data, mm_cluster):
    G = graph

    for k, v in mm_cluster.items():
        createNodes(G, str(k) + "c", {'type': 'clust_summary', 'text': v})

    for key, item in data.items():
        # createNodes(key, item)
        createEdges(G, str(item['clusterassignment']) + "c", str(key) + "d")

    connectClustDocEdges(G)
    connectIntraClusterDocEdges(G)

    # nx.write_gml(G, "tatti.gml")
    # save_json('newgraph.json', nx.json_graph.dumps(G))
    # save_json('new.json', json.dumps(dict(nodes=G.nodes(), edges=G.edges())))
    # json.dumps(dict(nodes=G.nodes(), edges=G.edges()))
    from networkx.readwrite import json_graph
    with open('newdatatrimmedfixedNEW.json', 'w') as outfile1:
        outfile1.write(json.dumps(json_graph.node_link_data(G)))

    nx.write_graphml(G, "semanticgraph2.graphml")
    nx.write_graphml(G, "test.graphml")
    return G


def createNodes(G, nodes, dict_attrs={}):
    if len(dict_attrs) == 0:
        G.add_node(nodes)
    else:
        G.add_node(nodes, **dict_attrs)


def createEdges(G, node, items):
    G.add_edge(node, items)


def connectClustDocEdges(G):
    clusters = [x for x, y in G.nodes(data=True) if y['type'] == 'clust_summary']  # get clusters

    unorderedPairGenerator = ((x, y) for x in clusters for y in clusters if y > x)

    graph = G.nodes(data=True)

    pairs_ordered = []
    sim_scores = []

    for pair in unorderedPairGenerator:
        item_1_normalized_text = normalize(graph[pair[0]]['text'])  # [:12]
        item_2_normalized_text = normalize(graph[pair[1]]['text'])  # [:12]
        sim_scores.append(jaccard(item_1_normalized_text, item_2_normalized_text))
        pairs_ordered.append([pair[0], pair[1]])

    avg = statistics.mean(sim_scores)
    more = statistics.stdev(sim_scores)

    i = 0
    for p in pairs_ordered:
        if sim_scores[i] > (avg + more):
            createEdges(G, p[0], p[1])
        i += 1


def connectIntraClusterDocEdges(G):
    clusters = [x for x, y in G.nodes(data=True) if y['type'] == 'clust_summary']  # get clusters

    import re
    pattern = re.compile("^(\d+d)+$")

    for cluster in clusters:
        nodes = G.edges(cluster)  # connected nodes

        docs = [x[1] for x in nodes if pattern.match(x[1])]

        unorderedPairGenerator = ((x, y) for x in docs for y in docs if y > x)

        graph = G.nodes(data=True)

        pairs_ordered = []
        sim_scores = []

        for pair in unorderedPairGenerator:
            item_1_normalized_text = normalize(graph[pair[0]]['text'])  # [:12]
            item_2_normalized_text = normalize(graph[pair[1]]['text'])  # [:12]
            sim_scores.append(jaccard(item_1_normalized_text, item_2_normalized_text))
            pairs_ordered.append([pair[0], pair[1]])

        if len(sim_scores) > 1:
            avg = statistics.mean(sim_scores)
            more = statistics.stdev(sim_scores)

            i = 0
            for p in pairs_ordered:
                if sim_scores[i] > (avg + more):
                    createEdges(G, p[0], p[1])
                i += 1

def expand_view(G):
    clusters = [x for x, y in G.nodes(data=True) if y['type'] == 'clust_summary']  # get clusters
    clust_view = dict()
    doc_view = dict()

    for clust in clusters:
        docs_list = list()
        related_clust = list()
        for n in G.neighbors(clust):
            if n.endswith('c'):
                related_clust.append(n)
            else:
                docs_list.append(n)

        text = G.nodes[clust]['text']
        # text = ' '.join(text.split()[:12]) + " ..."
        clust_view[clust] = {"docs_list": docs_list, "rel_clusts_list": related_clust, "summary": text}

    docs = [x for x, y in G.nodes(data=True) if y['type'] == 'doc_summary']  # get clusters
    for doc in docs:
        snip_list = list()
        related_docs = list()
        for n in G.neighbors(doc):
            if n.endswith('d'):
                related_docs.append(n)
            elif not n.endswith('c'):
                snip_list.append(n)

        text = G.nodes[doc]["text"]
        # text = ' '.join(text.split()[:7]) + " ..."

        doc_view[doc] = {"snips_list": snip_list, "rel_docs_list": related_docs, "summary": text}

    save_json('clust_view', clust_view)
    save_json('doc_view', doc_view)

# G = nx.read_gml("C:/Users/abdur/PycharmProjects/untitled/research/tatti.gml")
# expand_view(G)
# from networkx.readwrite import json_graph
# with open('networkdata1.json', 'w') as outfile1:
#     outfile1.write(json.dumps(json_graph.node_link_data(G)))