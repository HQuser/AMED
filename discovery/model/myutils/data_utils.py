import nltk
from bs4 import BeautifulSoup

from model.myutils.Preprocess import Preprocess

pr = Preprocess()


def cleanText(text):
    # clean_text = pr.remove_Tags(text)
    clean_text = BeautifulSoup(text).get_text()
    clean_text = pr.remove_punct(clean_text)
    clean_text = pr.remove_numbers(clean_text)

    return clean_text


def get_sentences(results):
    listSnippet = list()
    for k, item in results.items():
        title = cleanText(item['title'])
        if item.get('snippet') != None:
            listSnippet.append(title + " " + cleanText(item['snippet']))
        else:
            listSnippet.append(title)

    return listSnippet


def map_cluster_to_data_expanded(cluster_assignment, results):
    for k, v in results.items():
        temp = {'clusterassignment': int(cluster_assignment[k])}
        results[k] = {**v, **temp}

    print(results)

    return results


def map_cluster_to_doc_expanded(cluster_assignment, mm_docs):
    for k, v in mm_docs.items():
        temp = {'clusterassignment': int(cluster_assignment[k])}
        mm_docs[k] = {'mm_doc': v, **temp}

    print(mm_docs)

    return mm_docs


def map_cluster_summary_to_data_expanded(data, summarylist):
    for k, v in data.items():
        temp = {'clustersummary': summarylist[v['clusterassignment']]}
        data[k] = {**v, **temp}

    # print(data)

    return data
