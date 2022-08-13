from multiprocessing import Process

import scipy
from sentence_transformers import SentenceTransformer

from model.myutils.my_files_utils import save_json, read_json


def get_sentence_embedding(listSentences):
    # model = SentenceTransformer('bert-base-nli-mean-tokens')
    print("sentence start")
    model = SentenceTransformer('bert-base-nli-stsb-mean-tokens')
    model.cuda()
    # model = SentenceTransformer('roberta-large-nli-stsb-mean-tokens')

    # nemod = Wikipedia2Vec.load("enwiki_20180420_win10_100d.pkl")
    # print(nemod.get_word_vector("apple"))
    # print(nemod.most_similar(nemod.get_word('apple'), 5))

    sentences = listSentences
    sentence_embeddings = model.encode(sentences)

    print("sentence end")
    return sentence_embeddings


def search_through_embeddings(query, embeddings, search_results):
    print("Start Snip View")
    model = SentenceTransformer('bert-base-nli-stsb-mean-tokens')
    queries = list(query)
    query_embeddings = model.encode(queries)
    snip_view = dict()

    for query, query_embedding in zip(queries, query_embeddings):
        distances = scipy.spatial.distance.cdist([query_embedding], embeddings, "cosine")[0]

        results = zip(range(len(distances)), distances)
        results = sorted(results, key=lambda x: x[1], reverse = True)

        snip_count = 0
        for idx, distance in results:
            snip_view[snip_count] = search_results[idx]
            snip_count = snip_count + 1
            # print(search_results_sentences[idx].strip(), "(Score: %.4f)" % (1 - distance))

        save_json('snip_view', snip_view)
        print("End Snip View")

    print("finished")
    return 1


# def get_snip_view(query, embeddings, search_results):
#     snip_process = Process(target=search_through_embeddings, args=(query, embeddings, search_results,))
#     print("Snip process start")
#     # creating processes
#
#     # starting process 1
#     snip_process.start()
#     # wait until process 1 is finished
#     print("Snip process end")
#     return snip_process
